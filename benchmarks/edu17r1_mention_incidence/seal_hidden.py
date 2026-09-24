#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

LABELS = {"incidence", "non_incidence"}


def load_and_validate(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        rid = row.get("id")
        label = row.get("label")
        if not isinstance(rid, str) or not rid:
            raise ValueError(f"{path}:{line_no}: missing non-empty string id")
        if rid in seen:
            raise ValueError(f"{path}:{line_no}: duplicate id {rid}")
        if label not in LABELS:
            raise ValueError(f"{path}:{line_no}: invalid label {label!r}")
        seen.add(rid)
        rows.append(row)
    if not rows:
        raise ValueError(f"{path}: hidden split is empty")
    return rows


def build_manifest(hidden_path: Path, *, frozen_at: str, evaluator: str, contamination: str) -> dict[str, Any]:
    rows = load_and_validate(hidden_path)
    return {
        "schema": "Venus.SealedHiddenSplit.v0.1",
        "benchmark": "edu17r1_mention_incidence",
        "dataset_sha256": hashlib.sha256(hidden_path.read_bytes()).hexdigest(),
        "n": len(rows),
        "frozen_at": frozen_at,
        "evaluator": evaluator,
        "contamination": contamination,
        "labels_public_before_run": False,
        "promotion_authority": False,
        "note": (
            "This manifest binds hidden bytes without publishing examples or labels. "
            "The evaluator must retain the hidden split outside the public repository until the run is complete."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Hash and validate a hidden EDU17R1 split without publishing its labels.")
    parser.add_argument("hidden", type=Path)
    parser.add_argument("--frozen-at", required=True)
    parser.add_argument("--evaluator", required=True)
    parser.add_argument("--contamination", required=True, choices=("DECLARED_CLEAN", "UNKNOWN", "KNOWN_EXPOSURE"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        manifest = build_manifest(
            args.hidden,
            frozen_at=args.frozen_at,
            evaluator=args.evaluator,
            contamination=args.contamination,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, indent=2, sort_keys=True))
        return 1

    rendered = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
