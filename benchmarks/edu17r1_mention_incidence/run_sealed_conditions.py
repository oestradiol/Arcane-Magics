#!/usr/bin/env python3
from __future__ import annotations

"""Execution-side custody wrapper for sealed EDU17R1 A/B/C/D runs.

This wrapper never reads gold labels and has no scoring or promotion authority.
It binds a blind execution to the exact prefrozen condition implementations,
protocol, analysis plan, frozen candidate, and ownership receipt.
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FREEZE = HERE / "CONDITION_IMPLEMENTATIONS.json"
DECISIONS = {"incidence", "non_incidence", "withhold"}


class SealedExecutionError(ValueError):
    pass


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    seen: set[str] = set()
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise SealedExecutionError(f"{path}:{line_no}: row must be object")
        rid = row.get("id")
        if not isinstance(rid, str) or not rid:
            raise SealedExecutionError(f"{path}:{line_no}: missing id")
        if rid in seen:
            raise SealedExecutionError(f"{path}:{line_no}: duplicate id {rid}")
        if "label" in row or "rationale" in row or "gold" in row or "answer" in row:
            raise SealedExecutionError(f"{path}:{line_no}: sensitive field in blind input")
        seen.add(rid)
        rows.append(row)
    if not rows:
        raise SealedExecutionError("blind input is empty")
    return rows


def verify_frozen_artifact(entry: dict[str, Any]) -> dict[str, str]:
    path = ROOT / entry["path"]
    if not path.exists():
        raise SealedExecutionError(f"missing frozen artifact: {entry['path']}")
    actual = git_blob_sha(path)
    expected = entry["git_blob_sha"]
    if actual != expected:
        raise SealedExecutionError(
            f"frozen artifact drift: {entry['path']} expected={expected} actual={actual}"
        )
    return {"path": entry["path"], "git_blob_sha": actual}


def verify_freeze() -> dict[str, Any]:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if freeze.get("schema") != "Venus.EDU17R1ConditionImplementationFreeze.v0.1":
        raise SealedExecutionError("unexpected condition-freeze schema")
    if freeze.get("status") != "PREFROZEN_BEFORE_HIDDEN_SPLIT":
        raise SealedExecutionError("condition freeze is not prefrozen")
    if freeze.get("hidden_labels_exposed") is not False:
        raise SealedExecutionError("condition freeze reports hidden-label exposure")
    if freeze.get("post_exposure_repair_allowed") is not False:
        raise SealedExecutionError("post-exposure repair must remain forbidden")

    verified = {
        "protocol": verify_frozen_artifact(freeze["protocol"]),
        "analysis_plan": verify_frozen_artifact(freeze["analysis_plan"]),
        "frozen_candidate": verify_frozen_artifact(freeze["frozen_candidate"]),
        "ownership_receipt": verify_frozen_artifact(freeze["ownership_receipt"]),
        "conditions": {},
    }
    if "execution_custody_wrapper" in freeze:
        verified["execution_custody_wrapper"] = verify_frozen_artifact(
            freeze["execution_custody_wrapper"]
        )
    for cid in ("A", "B", "C", "D"):
        row = freeze["conditions"][cid]
        path = ROOT / row["artifact"]
        if not path.exists():
            raise SealedExecutionError(f"missing condition {cid}: {row['artifact']}")
        actual = git_blob_sha(path)
        if actual != row["git_blob_sha"]:
            raise SealedExecutionError(
                f"condition {cid} drift: expected={row['git_blob_sha']} actual={actual}"
            )
        verified["conditions"][cid] = {
            "artifact": row["artifact"],
            "git_blob_sha": actual,
            "role": row["role"],
        }
    return verified


def verify_blind_manifest(blind: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "Venus.EDU17R1BlindInputManifest.v0.1":
        raise SealedExecutionError("unexpected blind manifest schema")
    if manifest.get("labels_exposed") is not False:
        raise SealedExecutionError("blind manifest reports labels exposed")
    current_freeze_sha256 = sha256_bytes(FREEZE)
    if manifest.get("condition_freeze_sha256") != current_freeze_sha256:
        raise SealedExecutionError(
            "blind manifest condition-freeze mismatch: "
            f"sealed={manifest.get('condition_freeze_sha256')} current={current_freeze_sha256}"
        )
    actual = sha256_bytes(blind)
    if actual != manifest.get("blind_input_sha256"):
        raise SealedExecutionError(
            f"blind input hash mismatch: expected={manifest.get('blind_input_sha256')} actual={actual}"
        )
    rows = load_jsonl(blind)
    if len(rows) != manifest.get("n"):
        raise SealedExecutionError(
            f"blind input count mismatch: manifest={manifest.get('n')} actual={len(rows)}"
        )
    return {"manifest": manifest, "rows": rows}


def validate_predictions(path: Path, expected_ids: tuple[str, ...]) -> dict[str, Any]:
    rows = []
    seen: set[str] = set()
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        rid = row.get("id")
        pred = row.get("prediction")
        if rid in seen:
            raise SealedExecutionError(f"{path}:{line_no}: duplicate prediction id {rid}")
        if pred not in DECISIONS:
            raise SealedExecutionError(f"{path}:{line_no}: invalid prediction {pred!r}")
        seen.add(rid)
        rows.append(row)
    ids = tuple(row["id"] for row in rows)
    if set(ids) != set(expected_ids):
        missing = sorted(set(expected_ids) - set(ids))
        extra = sorted(set(ids) - set(expected_ids))
        raise SealedExecutionError(f"{path}: id mismatch missing={missing} extra={extra}")
    return {
        "path": str(path),
        "sha256": sha256_bytes(path),
        "n": len(rows),
    }


def run_conditions(blind: Path, output_dir: Path, expected_ids: tuple[str, ...]) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, Any] = {}
    for cid in ("A", "B", "C", "D"):
        script = HERE / f"condition_{cid.casefold()}.py"
        out = output_dir / f"condition-{cid}.jsonl"
        proc = subprocess.run(
            [sys.executable, str(script), str(blind), "--output", str(out)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise SealedExecutionError(
                f"condition {cid} failed: rc={proc.returncode} stderr={proc.stderr.strip()}"
            )
        outputs[cid] = validate_predictions(out, expected_ids)
    return outputs


def execute(blind: Path, blind_manifest: Path, output_dir: Path) -> dict[str, Any]:
    frozen = verify_freeze()
    blind_info = verify_blind_manifest(blind, blind_manifest)
    expected_ids = tuple(row["id"] for row in blind_info["rows"])
    outputs = run_conditions(blind, output_dir, expected_ids)

    body = {
        "schema": "Venus.EDU17R1SealedExecutionReceipt.v0.1",
        "benchmark": "edu17r1_mention_incidence",
        "freeze_file": str(FREEZE.relative_to(ROOT)),
        "freeze_sha256": sha256_bytes(FREEZE),
        "verified_frozen_artifacts": frozen,
        "source_hidden_sha256": blind_info["manifest"]["source_hidden_sha256"],
        "blind_input_sha256": blind_info["manifest"]["blind_input_sha256"],
        "blind_manifest_sha256": sha256_bytes(blind_manifest),
        "n": len(expected_ids),
        "conditions": outputs,
        "gold_labels_read": False,
        "scoring_performed": False,
        "promotion_authority": False,
        "post_exposure_repair_authorized": False,
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    body["receipt_sha256"] = hashlib.sha256(canonical).hexdigest()
    receipt_path = output_dir / "execution-receipt.json"
    receipt_path.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return body


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Execute prefrozen EDU17R1 A/B/C/D conditions on evaluator-provided blind input."
    )
    parser.add_argument("blind_jsonl", type=Path)
    parser.add_argument("blind_manifest", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = execute(args.blind_jsonl, args.blind_manifest, args.output_dir)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}, indent=2, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
