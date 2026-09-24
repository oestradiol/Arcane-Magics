#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re
import sys


def first_action(row: dict) -> str:
    return row["actions"][0]


def always_unknown(row: dict) -> str:
    return "UNKNOWN" if "UNKNOWN" in row["actions"] else row["actions"][-1]


def latest_literal_action(row: dict) -> str:
    """Recent-context lexical control, deliberately not a semantic memory system."""
    for text in reversed(row["history"]):
        for action in row["actions"]:
            if action == "UNKNOWN":
                continue
            pattern = re.escape(action).replace(r"\_", r"[ _-]")
            if re.search(rf"\b{pattern}\b", text, re.I):
                return action
    return always_unknown(row)


BASELINES = {
    "first_action": first_action,
    "always_unknown": always_unknown,
    "latest_literal_action": latest_literal_action,
}


def evaluate(rows: list[dict], predictor) -> dict:
    correct = 0
    wrong = []
    by_class: dict[str, dict[str, int]] = {}
    for row in rows:
        pred = predictor(row)
        ok = pred == row["gold"]
        correct += int(ok)
        if not ok:
            wrong.append({"id": row["id"], "prediction": pred, "gold": row["gold"]})
        slot = by_class.setdefault(row["class"], {"n": 0, "correct": 0})
        slot["n"] += 1
        slot["correct"] += int(ok)
    return {
        "n": len(rows),
        "correct": correct,
        "accuracy": correct / len(rows) if rows else 0.0,
        "by_class": by_class,
        "wrong": wrong,
    }


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("dev.jsonl")
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    out = {name: evaluate(rows, predictor) for name, predictor in BASELINES.items()}
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
