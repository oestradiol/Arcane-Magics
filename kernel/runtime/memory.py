#!/usr/bin/env python3
"""Persistent content-addressed memory for the Venus developmental runtime.

Authority model:
- objects are immutable and addressed by SHA-256 of canonical semantic content;
- dispositions are mutable metadata and never rewrite object identity;
- CONSUMED preserves provenance by pointing to a replacement rather than deleting history;
- large payloads are compressed into a deduplicated object directory;
- canonical export is deterministic and can be hashed independently of SQLite layout.

This module is storage, not cognition: retaining a record is not learning unless the
retained state changes later admissible transformation.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sqlite3
import zlib
from typing import Any, Iterable

_ALLOWED_STATUS = {
    "ACTIVE", "OPEN", "WITHHOLD", "CONSUMED", "INVALID", "REJECTED", "HISTORICAL"
}


def _canon(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class MemoryObject:
    digest: str
    kind: str
    payload: Any
    parents: tuple[str, ...]
    provenance: tuple[str, ...]
    scope: str | None
    labels: tuple[str, ...]
    status: str
    replacement: str | None
    reason: str


class VenusMemory:
    """Transactional semantic memory with provenance-preserving consumption."""

    def __init__(self, root: str | Path, *, inline_limit: int = 16_384):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.objects_dir = self.root / "objects"
        self.objects_dir.mkdir(exist_ok=True)
        self.db_path = self.root / "index.sqlite3"
        self.inline_limit = inline_limit
        self.db = sqlite3.connect(self.db_path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA journal_mode=WAL")
        self._schema()

    def close(self) -> None:
        self.db.close()

    def __enter__(self) -> "VenusMemory":
        return self

    def __exit__(self, *_exc) -> None:
        self.close()

    def _schema(self) -> None:
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS objects(
                digest TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                canonical BLOB,
                blob_digest TEXT,
                payload_bytes INTEGER NOT NULL,
                scope TEXT
            );
            CREATE TABLE IF NOT EXISTS parents(
                child TEXT NOT NULL,
                parent TEXT NOT NULL,
                position INTEGER NOT NULL,
                PRIMARY KEY(child, position)
            );
            CREATE TABLE IF NOT EXISTS provenance(
                digest TEXT NOT NULL,
                source TEXT NOT NULL,
                position INTEGER NOT NULL,
                PRIMARY KEY(digest, position)
            );
            CREATE TABLE IF NOT EXISTS labels(
                digest TEXT NOT NULL,
                label TEXT NOT NULL,
                PRIMARY KEY(digest, label)
            );
            CREATE TABLE IF NOT EXISTS disposition(
                digest TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                replacement TEXT,
                reason TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS access(
                digest TEXT PRIMARY KEY,
                count INTEGER NOT NULL DEFAULT 0
            );
            CREATE INDEX IF NOT EXISTS idx_objects_kind ON objects(kind);
            CREATE INDEX IF NOT EXISTS idx_labels_label ON labels(label);
            CREATE INDEX IF NOT EXISTS idx_disposition_status ON disposition(status);
            """
        )
        self.db.commit()

    def _blob_path(self, digest: str) -> Path:
        return self.objects_dir / digest[:2] / (digest + ".z")

    def _write_blob(self, data: bytes) -> str:
        digest = _sha(data)
        path = self._blob_path(digest)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(zlib.compress(data, level=9))
        return digest

    def _read_blob(self, digest: str) -> bytes:
        return zlib.decompress(self._blob_path(digest).read_bytes())

    def put(
        self,
        kind: str,
        payload: Any,
        *,
        parents: Iterable[str] = (),
        provenance: Iterable[str] = (),
        scope: str | None = None,
        labels: Iterable[str] = (),
        status: str = "ACTIVE",
    ) -> str:
        if status not in _ALLOWED_STATUS:
            raise ValueError(f"unknown status: {status}")
        parents = tuple(parents)
        provenance = tuple(provenance)
        labels = tuple(sorted(set(labels)))
        for parent in parents:
            self._semantic(parent)
        semantic = {
            "kind": kind,
            "payload": payload,
            "parents": parents,
            "provenance": provenance,
            "scope": scope,
            "labels": labels,
        }
        raw = _canon(semantic)
        digest = _sha(raw)

        inline = raw if len(raw) <= self.inline_limit else None
        blob = None if inline is not None else self._write_blob(raw)

        with self.db:
            self.db.execute(
                "INSERT OR IGNORE INTO objects"
                "(digest,kind,canonical,blob_digest,payload_bytes,scope)"
                " VALUES(?,?,?,?,?,?)",
                (digest, kind, inline, blob, len(raw), scope),
            )
            for i, parent in enumerate(parents):
                self.db.execute(
                    "INSERT OR IGNORE INTO parents(child,parent,position) VALUES(?,?,?)",
                    (digest, parent, i),
                )
            for i, source in enumerate(provenance):
                self.db.execute(
                    "INSERT OR IGNORE INTO provenance(digest,source,position) VALUES(?,?,?)",
                    (digest, source, i),
                )
            for label in labels:
                self.db.execute(
                    "INSERT OR IGNORE INTO labels(digest,label) VALUES(?,?)",
                    (digest, label),
                )
            self.db.execute(
                "INSERT OR IGNORE INTO disposition(digest,status,replacement,reason)"
                " VALUES(?,?,NULL,'')",
                (digest, status),
            )
            self.db.execute(
                "INSERT OR IGNORE INTO access(digest,count) VALUES(?,0)", (digest,)
            )
        return digest

    def _semantic(self, digest: str) -> dict[str, Any]:
        row = self.db.execute(
            "SELECT canonical,blob_digest FROM objects WHERE digest=?", (digest,)
        ).fetchone()
        if row is None:
            raise KeyError(digest)
        raw = row["canonical"] if row["canonical"] is not None else self._read_blob(row["blob_digest"])
        if _sha(raw) != digest:
            raise ValueError(f"memory digest mismatch: {digest}")
        return json.loads(raw)

    def get(self, digest: str, *, touch: bool = True) -> MemoryObject:
        semantic = self._semantic(digest)
        disp = self.db.execute(
            "SELECT status,replacement,reason FROM disposition WHERE digest=?", (digest,)
        ).fetchone()
        if touch:
            with self.db:
                self.db.execute("UPDATE access SET count=count+1 WHERE digest=?", (digest,))
        return MemoryObject(
            digest=digest,
            kind=semantic["kind"],
            payload=semantic["payload"],
            parents=tuple(semantic["parents"]),
            provenance=tuple(semantic["provenance"]),
            scope=semantic["scope"],
            labels=tuple(semantic["labels"]),
            status=disp["status"],
            replacement=disp["replacement"],
            reason=disp["reason"],
        )

    def set_disposition(
        self,
        digest: str,
        status: str,
        *,
        replacement: str | None = None,
        reason: str = "",
    ) -> None:
        if status not in _ALLOWED_STATUS:
            raise ValueError(f"unknown status: {status}")
        self._semantic(digest)
        if replacement is not None:
            self._semantic(replacement)
            cursor = replacement
            seen: set[str] = set()
            while cursor is not None:
                if cursor == digest:
                    raise ValueError("replacement cycle")
                if cursor in seen:
                    raise ValueError("existing replacement cycle")
                seen.add(cursor)
                row = self.db.execute(
                    "SELECT replacement FROM disposition WHERE digest=?", (cursor,)
                ).fetchone()
                cursor = row["replacement"] if row is not None else None
        if status == "CONSUMED" and replacement is None:
            raise ValueError("CONSUMED requires replacement")
        with self.db:
            self.db.execute(
                "UPDATE disposition SET status=?, replacement=?, reason=? WHERE digest=?",
                (status, replacement, reason, digest),
            )

    def consume(self, digest: str, replacement: str, *, reason: str) -> None:
        self.set_disposition(
            digest, "CONSUMED", replacement=replacement, reason=reason
        )

    def query(
        self,
        *,
        kind: str | None = None,
        status: str | None = None,
        label: str | None = None,
        limit: int = 100,
    ) -> tuple[str, ...]:
        clauses, args = [], []
        if kind is not None:
            clauses.append("o.kind=?")
            args.append(kind)
        if status is not None:
            clauses.append("d.status=?")
            args.append(status)
        join = ""
        if label is not None:
            join = " JOIN labels l ON l.digest=o.digest "
            clauses.append("l.label=?")
            args.append(label)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        rows = self.db.execute(
            "SELECT o.digest FROM objects o "
            "JOIN disposition d ON d.digest=o.digest "
            + join + where + " ORDER BY o.digest LIMIT ?",
            (*args, limit),
        ).fetchall()
        return tuple(r["digest"] for r in rows)

    def dependency_closure(self, roots: Iterable[str]) -> tuple[str, ...]:
        seen = set(roots)
        queue = list(roots)
        while queue:
            parent = queue.pop()
            rows = self.db.execute(
                "SELECT child FROM parents WHERE parent=?", (parent,)
            ).fetchall()
            for row in rows:
                child = row["child"]
                if child not in seen:
                    seen.add(child)
                    queue.append(child)
        return tuple(sorted(seen))

    def cold_candidates(self, *, max_accesses: int = 0, limit: int = 100) -> tuple[str, ...]:
        rows = self.db.execute(
            "SELECT a.digest FROM access a "
            "JOIN disposition d ON d.digest=a.digest "
            "WHERE a.count<=? AND d.status IN ('CONSUMED','HISTORICAL','REJECTED','INVALID') "
            "ORDER BY a.count,a.digest LIMIT ?",
            (max_accesses, limit),
        ).fetchall()
        return tuple(r["digest"] for r in rows)

    def canonical_export(self) -> bytes:
        records = []
        rows = self.db.execute("SELECT digest FROM objects ORDER BY digest").fetchall()
        for row in rows:
            obj = self.get(row["digest"], touch=False)
            records.append(
                {
                    "digest": obj.digest,
                    "kind": obj.kind,
                    "payload": obj.payload,
                    "parents": obj.parents,
                    "provenance": obj.provenance,
                    "scope": obj.scope,
                    "labels": obj.labels,
                    "status": obj.status,
                    "replacement": obj.replacement,
                    "reason": obj.reason,
                }
            )
        return _canon({"schema": "Venus.Memory.v1", "records": records})

    def checkpoint(self, path: str | Path) -> dict[str, Any]:
        raw = self.canonical_export()
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(zlib.compress(raw, level=9))
        return {
            "schema": "Venus.MemoryCheckpoint.v1",
            "records": len(json.loads(raw)["records"]),
            "sha256": _sha(raw),
            "bytes_uncompressed": len(raw),
            "path": str(path),
        }
