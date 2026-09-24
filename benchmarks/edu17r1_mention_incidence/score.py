#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

LABELS = {"incidence", "non_incidence"}
DECISIONS = LABELS | {"withhold"}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_no}: row must be an object")
        rows.append(row)
    return rows


def keyed(rows: list[dict[str, Any]], path: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        rid = row.get("id")
        if not isinstance(rid, str) or not rid:
            raise ValueError(f"{path}: every row requires a non-empty string id")
        if rid in out:
            raise ValueError(f"{path}: duplicate id {rid}")
        out[rid] = row
    return out


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_div(num: int, den: int) -> float:
    return num / den if den else 0.0


def withhold_for_label(gold, pred, label: str) -> int:
    return sum(
        grow["label"] == label and pred[rid].get("prediction") == "withhold"
        for rid, grow in gold.items()
    )


def score(gold_path: Path, prediction_path: Path, manifest_path: Path | None = None) -> dict[str, Any]:
    if manifest_path is not None:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected = manifest.get("dataset_sha256")
        actual = sha256_bytes(gold_path)
        if expected != actual:
            raise ValueError(f"hidden split hash mismatch: manifest={expected!r} actual={actual!r}")

    gold = keyed(load_jsonl(gold_path), gold_path)
    pred = keyed(load_jsonl(prediction_path), prediction_path)
    missing = sorted(set(gold) - set(pred))
    extra = sorted(set(pred) - set(gold))
    if missing or extra:
        raise ValueError(f"id mismatch: missing={missing} extra={extra}")

    tp = fp = tn = fn = withhold = correct = 0
    by_subtype: dict[str, dict[str, int]] = {}

    for rid, grow in gold.items():
        label = grow.get("label")
        if label not in LABELS:
            raise ValueError(f"{gold_path}: {rid}: invalid label {label!r}")
        decision = pred[rid].get("prediction")
        if decision not in DECISIONS:
            raise ValueError(f"{prediction_path}: {rid}: invalid prediction {decision!r}")

        subtype = str(grow.get("subtype", "unspecified"))
        slot = by_subtype.setdefault(subtype, {"n": 0, "correct": 0, "withhold": 0, "false_binding": 0})
        slot["n"] += 1

        if decision == "withhold":
            withhold += 1
            slot["withhold"] += 1
            continue

        ok = decision == label
        correct += int(ok)
        slot["correct"] += int(ok)

        if label == "incidence" and decision == "incidence":
            tp += 1
        elif label == "incidence" and decision == "non_incidence":
            fn += 1
        elif label == "non_incidence" and decision == "incidence":
            fp += 1
            slot["false_binding"] += 1
        else:
            tn += 1

    n = len(gold)
    answered = n - withhold
    precision = safe_div(tp, tp + fp)
    recall = safe_div(tp, tp + fn + withhold_for_label(gold, pred, "incidence"))
    f1 = safe_div(2 * precision * recall, precision + recall) if precision + recall else 0.0
    actual_non_incidence = sum(row["label"] == "non_incidence" for row in gold.values())

    return {
        "schema": "Venus.EDU17R1MentionIncidenceScore.v0.1",
        "n": n,
        "answered": answered,
        "coverage": safe_div(answered, n),
        "correct": correct,
        "accuracy": safe_div(correct, n),
        "selective_accuracy": safe_div(correct, answered),
        "tp": tp, "fp": fp, "tn": tn, "fn": fn, "withhold": withhold,
        "precision_incidence": precision,
        "recall_incidence": recall,
        "f1_incidence": f1,
        "false_unresolved_binding_rate": safe_div(fp, actual_non_incidence),
        "false_withhold_rate": safe_div(withhold, n),
        "by_subtype": by_subtype,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Score EDU17R1 MENTION != INCIDENCE predictions.")
    parser.add_argument("gold", type=Path)
    parser.add_argument("predictions", type=Path)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    try:
        result = score(args.gold, args.predictions, args.manifest)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, indent=2, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
