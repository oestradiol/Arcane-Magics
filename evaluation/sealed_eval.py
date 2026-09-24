from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
from typing import Iterable

CONTAMINATION_STATES = {"DECLARED_CLEAN", "UNKNOWN", "KNOWN_EXPOSURE"}

class SealedEvaluationError(ValueError):
    pass

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def canonical_sha256(data: dict) -> str:
    raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def seal_hidden_dataset(
    path: Path,
    *,
    benchmark: str,
    frozen_at: str,
    evaluator: str,
    contamination: str,
    n: int | None = None,
) -> dict:
    if contamination not in CONTAMINATION_STATES:
        raise SealedEvaluationError(f"invalid contamination state: {contamination}")
    if not path.exists() or not path.is_file():
        raise SealedEvaluationError(f"hidden dataset missing: {path}")
    if not benchmark or not evaluator or not frozen_at:
        raise SealedEvaluationError("benchmark, evaluator, and frozen_at are required")
    manifest = {
        "schema": "Venus.SealedHiddenDataset.v0.1",
        "benchmark": benchmark,
        "dataset_sha256": sha256_file(path),
        "bytes": path.stat().st_size,
        "n": n,
        "frozen_at": frozen_at,
        "evaluator": evaluator,
        "contamination": contamination,
        "labels_public_before_run": False,
        "evaluator_separated_from_execution": True,
        "no_post_exposure_repair": True,
        "promotion_authority": False,
    }
    manifest["manifest_sha256"] = canonical_sha256(manifest)
    return manifest

def validate_hidden_manifest(manifest: dict) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema") != "Venus.SealedHiddenDataset.v0.1":
        errors.append("wrong schema")
    if not manifest.get("benchmark"):
        errors.append("missing benchmark")
    if not manifest.get("dataset_sha256") or len(str(manifest.get("dataset_sha256"))) != 64:
        errors.append("invalid dataset_sha256")
    if manifest.get("labels_public_before_run") is not False:
        errors.append("labels_public_before_run must be false")
    if manifest.get("evaluator_separated_from_execution") is not True:
        errors.append("evaluator must be separated from execution")
    if manifest.get("no_post_exposure_repair") is not True:
        errors.append("no_post_exposure_repair must be true")
    if manifest.get("promotion_authority") is not False:
        errors.append("sealed manifest cannot grant promotion authority")
    if manifest.get("contamination") not in CONTAMINATION_STATES:
        errors.append("invalid contamination state")
    expected = manifest.get("manifest_sha256")
    if expected:
        payload = dict(manifest)
        payload.pop("manifest_sha256", None)
        if canonical_sha256(payload) != expected:
            errors.append("manifest_sha256 mismatch")
    else:
        errors.append("missing manifest_sha256")
    return errors

def bind_run_receipt(
    *,
    hidden_manifest: dict,
    condition_outputs: dict[str, Path],
    run_id: str,
    executed_at: str,
    evaluator: str,
    required_conditions: Iterable[str],
) -> dict:
    errors = validate_hidden_manifest(hidden_manifest)
    if errors:
        raise SealedEvaluationError("; ".join(errors))
    required = set(required_conditions)
    supplied = set(condition_outputs)
    if required != supplied:
        raise SealedEvaluationError(
            f"condition mismatch: missing={sorted(required-supplied)} extra={sorted(supplied-required)}"
        )
    if evaluator != hidden_manifest["evaluator"]:
        raise SealedEvaluationError("run evaluator differs from sealed evaluator")
    outputs = {}
    for cid, path in sorted(condition_outputs.items()):
        if not path.exists() or not path.is_file():
            raise SealedEvaluationError(f"missing output for condition {cid}: {path}")
        outputs[cid] = {
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        }
    receipt = {
        "schema": "Venus.SealedEvaluationRunReceipt.v0.1",
        "run_id": run_id,
        "benchmark": hidden_manifest["benchmark"],
        "hidden_manifest_sha256": hidden_manifest["manifest_sha256"],
        "hidden_dataset_sha256": hidden_manifest["dataset_sha256"],
        "executed_at": executed_at,
        "evaluator": evaluator,
        "conditions": outputs,
        "no_post_exposure_repair": True,
        "promotion_authority": False,
    }
    receipt["receipt_sha256"] = canonical_sha256(receipt)
    return receipt
