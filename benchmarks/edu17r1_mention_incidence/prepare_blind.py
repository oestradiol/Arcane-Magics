#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SENSITIVE_FIELDS = {"label", "rationale", "gold", "answer", "expected"}


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_no}: row must be an object")
        rid = row.get("id")
        if not isinstance(rid, str) or not rid:
            raise ValueError(f"{path}:{line_no}: missing non-empty string id")
        if rid in seen:
            raise ValueError(f"{path}:{line_no}: duplicate id {rid}")
        if row.get("label") not in {"incidence", "non_incidence"}:
            raise ValueError(f"{path}:{line_no}: invalid or missing hidden label")
        seen.add(rid)
        rows.append(row)
    if not rows:
        raise ValueError(f"{path}: hidden split is empty")
    return rows


def blind_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    blinded = []
    for row in rows:
        out = {k: v for k, v in row.items() if k not in SENSITIVE_FIELDS}
        if "id" not in out or "text" not in out:
            raise ValueError("every blinded row must retain id and text")
        blinded.append(out)
    return blinded


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def prepare(hidden: Path, sealed_manifest: Path, blind_output: Path, blind_manifest_output: Path) -> dict[str, Any]:
    manifest = json.loads(sealed_manifest.read_text(encoding="utf-8"))
    expected = manifest.get("dataset_sha256")
    actual = sha256_bytes(hidden)
    if expected != actual:
        raise ValueError(f"hidden split hash mismatch: manifest={expected!r} actual={actual!r}")
    if manifest.get("labels_public_before_run") is not False:
        raise ValueError("sealed manifest does not preserve hidden-label boundary")

    if not manifest.get("condition_freeze_sha256"):
        raise ValueError("sealed manifest missing condition-freeze binding")

    rows = load_jsonl(hidden)
    blinded = blind_rows(rows)
    write_jsonl(blind_output, blinded)

    blind_manifest = {
        "schema": "Venus.EDU17R1BlindInputManifest.v0.1",
        "benchmark": "edu17r1_mention_incidence",
        "source_hidden_sha256": actual,
        "condition_freeze_sha256": manifest.get("condition_freeze_sha256"),
        "blind_input_sha256": sha256_bytes(blind_output),
        "n": len(blinded),
        "excluded_fields": sorted(SENSITIVE_FIELDS),
        "labels_exposed": False,
        "promotion_authority": False,
    }
    blind_manifest_output.write_text(
        json.dumps(blind_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return blind_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare label-free EDU17R1 inputs from evaluator-held hidden data.")
    parser.add_argument("hidden", type=Path)
    parser.add_argument("sealed_manifest", type=Path)
    parser.add_argument("--blind-output", type=Path, required=True)
    parser.add_argument("--blind-manifest-output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = prepare(args.hidden, args.sealed_manifest, args.blind_output, args.blind_manifest_output)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, indent=2, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
