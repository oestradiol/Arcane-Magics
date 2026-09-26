from __future__ import annotations

"""Chronological raw-first interaction storage for WorldMirror Console.

Raw carrier bytes are preserved separately from decoded/semantic views.
Chronology is SQLite metadata; semantic objects are delegated to VenusMemory.
Storing an interaction is evidence custody, not a learning claim.
"""

from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path
import sqlite3
import time
import uuid
from typing import Any

from kernel.runtime.canonical import chain_digest
from kernel.runtime.memory import VenusMemory


@dataclass(frozen=True)
class InteractionEvent:
    seq: int
    event_id: str
    session_id: str
    actor: str
    kind: str
    media_type: str
    raw_sha256: str
    raw_bytes: int
    semantic_digest: str
    created_ns: int
    parent_event_id: str | None
    decoded_text: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class InteractionStore:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.raw_dir = self.root / "raw"
        self.raw_dir.mkdir(exist_ok=True)
        self.memory = VenusMemory(self.root / "semantic")
        self.db = sqlite3.connect(self.root / "timeline.sqlite3")
        self.db.row_factory = sqlite3.Row
        self._schema()

    def _schema(self) -> None:
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS sessions(
                session_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_ns INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events(
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                session_id TEXT NOT NULL,
                actor TEXT NOT NULL,
                kind TEXT NOT NULL,
                media_type TEXT NOT NULL,
                raw_sha256 TEXT NOT NULL,
                raw_bytes INTEGER NOT NULL,
                semantic_digest TEXT NOT NULL,
                created_ns INTEGER NOT NULL,
                parent_event_id TEXT,
                FOREIGN KEY(session_id) REFERENCES sessions(session_id)
            );
            CREATE INDEX IF NOT EXISTS idx_events_session_seq
                ON events(session_id, seq);
            """
        )
        self.db.commit()

    def close(self) -> None:
        self.memory.close()
        self.db.close()

    def __enter__(self) -> "InteractionStore":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def create_session(self, *, title: str = "", session_id: str | None = None) -> str:
        sid = session_id or uuid.uuid4().hex
        now = time.time_ns()
        with self.db:
            self.db.execute(
                "INSERT INTO sessions(session_id,title,created_ns) VALUES(?,?,?)",
                (sid, title, now),
            )
        return sid

    def sessions(self, *, limit: int = 100) -> tuple[dict[str, Any], ...]:
        rows = self.db.execute(
            "SELECT session_id,title,created_ns FROM sessions "
            "ORDER BY created_ns DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return tuple(dict(row) for row in rows)

    def _raw_path(self, digest: str) -> Path:
        return self.raw_dir / digest[:2] / (digest + ".bin")

    def _put_raw(self, raw: bytes) -> str:
        digest = hashlib.sha256(raw).hexdigest()
        path = self._raw_path(digest)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        return digest

    @staticmethod
    def _decode(raw: bytes, media_type: str) -> tuple[str | None, str | None]:
        mt = media_type.casefold()
        textual = (
            mt.startswith("text/")
            or "json" in mt
            or "xml" in mt
            or mt == "application/x-www-form-urlencoded"
        )
        if not textual:
            return None, None
        try:
            return raw.decode("utf-8"), "utf-8"
        except UnicodeDecodeError:
            return None, "utf-8-decode-failed"

    def append(
        self,
        *,
        session_id: str,
        actor: str,
        kind: str,
        media_type: str,
        raw: bytes,
        parent_event_id: str | None = None,
    ) -> InteractionEvent:
        exists = self.db.execute(
            "SELECT 1 FROM sessions WHERE session_id=?",
            (session_id,),
        ).fetchone()
        if exists is None:
            raise KeyError(f"unknown session: {session_id}")
        if not actor or not kind or not media_type:
            raise ValueError("actor, kind, and media_type are required")

        raw_sha = self._put_raw(raw)
        decoded, decode_status = self._decode(raw, media_type)
        parent_semantic: tuple[str, ...] = ()
        if parent_event_id:
            prow = self.db.execute(
                "SELECT semantic_digest FROM events WHERE event_id=? AND session_id=?",
                (parent_event_id, session_id),
            ).fetchone()
            if prow is None:
                raise KeyError(f"unknown parent event: {parent_event_id}")
            parent_semantic = (str(prow["semantic_digest"]),)

        position = int(
            self.db.execute(
                "SELECT COUNT(*) AS n FROM events WHERE session_id=?",
                (session_id,),
            ).fetchone()["n"]
        )
        semantic_payload = {
            "actor": actor,
            "kind": kind,
            "media_type": media_type,
            "raw_sha256": raw_sha,
            "raw_bytes": len(raw),
            "decoded_text": decoded,
            "decode_status": decode_status,
            "session_position": position,
        }
        semantic_digest = self.memory.put(
            "INTERACTION_EVENT_VIEW",
            semantic_payload,
            parents=parent_semantic,
            provenance=(
                f"raw:sha256:{raw_sha}",
                f"session:{session_id}",
                f"actor:{actor}",
            ),
            scope="WORLDMIRROR_CONSOLE",
            labels=("interaction", kind, actor),
        )
        previous = parent_event_id or "GENESIS"
        event_id = chain_digest(
            previous,
            "WORLDMIRROR_INTERACTION",
            {
                "session_id": session_id,
                "position": position,
                "actor": actor,
                "kind": kind,
                "media_type": media_type,
                "raw_sha256": raw_sha,
                "semantic_digest": semantic_digest,
            },
        )
        created_ns = time.time_ns()
        with self.db:
            cur = self.db.execute(
                "INSERT INTO events("
                "event_id,session_id,actor,kind,media_type,raw_sha256,raw_bytes,"
                "semantic_digest,created_ns,parent_event_id"
                ") VALUES(?,?,?,?,?,?,?,?,?,?)",
                (
                    event_id,
                    session_id,
                    actor,
                    kind,
                    media_type,
                    raw_sha,
                    len(raw),
                    semantic_digest,
                    created_ns,
                    parent_event_id,
                ),
            )
        return InteractionEvent(
            seq=int(cur.lastrowid),
            event_id=event_id,
            session_id=session_id,
            actor=actor,
            kind=kind,
            media_type=media_type,
            raw_sha256=raw_sha,
            raw_bytes=len(raw),
            semantic_digest=semantic_digest,
            created_ns=created_ns,
            parent_event_id=parent_event_id,
            decoded_text=decoded,
        )

    def events(self, session_id: str, *, limit: int = 200) -> tuple[InteractionEvent, ...]:
        rows = self.db.execute(
            "SELECT * FROM events WHERE session_id=? ORDER BY seq ASC LIMIT ?",
            (session_id, limit),
        ).fetchall()
        out = []
        for row in rows:
            semantic = self.memory.get(str(row["semantic_digest"]), touch=False)
            out.append(
                InteractionEvent(
                    seq=int(row["seq"]),
                    event_id=str(row["event_id"]),
                    session_id=str(row["session_id"]),
                    actor=str(row["actor"]),
                    kind=str(row["kind"]),
                    media_type=str(row["media_type"]),
                    raw_sha256=str(row["raw_sha256"]),
                    raw_bytes=int(row["raw_bytes"]),
                    semantic_digest=str(row["semantic_digest"]),
                    created_ns=int(row["created_ns"]),
                    parent_event_id=(
                        str(row["parent_event_id"])
                        if row["parent_event_id"] is not None
                        else None
                    ),
                    decoded_text=semantic.payload.get("decoded_text"),
                )
            )
        return tuple(out)

    def raw_bytes(self, digest: str) -> bytes:
        data = self._raw_path(digest).read_bytes()
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError("raw interaction digest mismatch")
        return data
