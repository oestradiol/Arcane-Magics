#!/usr/bin/env python3
from __future__ import annotations

"""Prospective founder/source-ablation audit for recompiled U1 recurrence."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]

SOURCE_FILES = (
    "kernel/__init__.py",
    "kernel/runtime/internal_ostar.py",
    "kernel/runtime/transform_program.py",
    "kernel/runtime/transform_program_repair_search.py",
    "kernel/runtime/transform_program_successor.py",
    "kernel/runtime/vmk2.py",
    "kernel/development/u1_recurrence.py",
)

ARTIFACT_FILES = (
    "kernel/development/SSR1_TRANSFORM_REPAIR_PRESSURE_PARENT.json",
    "kernel/development/SSR1_TRANSFORM_REPAIR_TRAINING_RETURNS.json",
    "kernel/development/SSR1_TRANSFORM_REPAIR_HELDOUT_RETURN.json",
    "kernel/development/SSR1_CTL_ADMISSION_RESULT.json",
)

FORBIDDEN_SOURCE_TOKENS = (
    "/Canonical/",
    "Canonical/Future/",
    "personal_context",
    "conversation_state",
    "requests.",
    "urllib.request",
    "http.client",
)

VERIFY_SOURCE = r'''
from __future__ import annotations
import json
from pathlib import Path
import socket
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

class _DeniedSocket:
    def __init__(self, *args, **kwargs):
        raise RuntimeError("network disabled in founder-ablation verifier")

socket.socket = _DeniedSocket
socket.create_connection = lambda *a, **k: (_ for _ in ()).throw(
    RuntimeError("network disabled in founder-ablation verifier")
)

from kernel.development.u1_recurrence import run_u1_recurrence

def load(name):
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))

formed = {
    "problem_id": "opaque-problem-a",
    "disposition": "FORMED_BOUNDED_PROBLEM",
    "residual_coordinates": ["continuation_state_unresolved"],
    "discriminator": "REPRODUCE_OR_REFRESH_CONTINUATION_STATE",
    "source_stream_ids": ["opaque-stream-a"],
}

renamed = {
    **formed,
    "problem_id": "renamed-problem-z",
    "source_stream_ids": ["renamed-stream-z"],
}

def run(problem):
    result, successor = run_u1_recurrence(
        formed_problem=problem,
        pressure_parent=load("SSR1_TRANSFORM_REPAIR_PRESSURE_PARENT.json"),
        training_return=load("SSR1_TRANSFORM_REPAIR_TRAINING_RETURNS.json"),
        heldout_return=load("SSR1_TRANSFORM_REPAIR_HELDOUT_RETURN.json"),
        ctl_ostar_admission=load("SSR1_CTL_ADMISSION_RESULT.json"),
    )
    return {
        "recurrence_id": result.recurrence_id,
        "problem_pressure_digest": result.problem_pressure_digest,
        "parent_correct": result.parent_correct,
        "successor_correct": result.successor_correct,
        "ablated_correct": result.ablated_correct,
        "total": result.total,
        "safety_floor_unchanged": result.safety_floor_unchanged,
        "rollback_available": result.rollback_available,
        "ctl_ostar_admitted": result.ctl_ostar_admitted,
        "promotion_authority": result.promotion_authority,
        "successor_present": successor is not None,
    }

first = run(formed)
second = run(renamed)
print(json.dumps({
    "first": first,
    "renamed": second,
    "label_invariant_metrics": {
        key: first[key] == second[key]
        for key in (
            "parent_correct",
            "successor_correct",
            "ablated_correct",
            "total",
            "safety_floor_unchanged",
            "rollback_available",
            "ctl_ostar_admitted",
            "promotion_authority",
            "successor_present",
        )
    },
    "provenance_changes": (
        first["problem_pressure_digest"] != second["problem_pressure_digest"]
        and first["recurrence_id"] != second["recurrence_id"]
    ),
}, sort_keys=True))
'''


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _copy_bundle(dst: Path) -> dict[str, str]:
    manifest: dict[str, str] = {}
    for rel in SOURCE_FILES:
        src = ROOT / rel
        if not src.is_file():
            raise ValueError(f"missing required source: {rel}")
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        manifest[rel] = sha256(target)

    # Use deliberately inert package initializers so importing the implicated
    # runtime does not drag unrelated repository modules into the bundle.
    for rel in ("kernel/runtime/__init__.py", "kernel/development/__init__.py"):
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('"""Isolated U1 portability bundle package."""\n', encoding="utf-8")
        manifest[rel] = sha256(target)

    artifacts = dst / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    for rel in ARTIFACT_FILES:
        src = ROOT / rel
        if not src.is_file():
            raise ValueError(f"missing required artifact: {rel}")
        target = artifacts / Path(rel).name
        shutil.copy2(src, target)
        manifest[f"artifacts/{target.name}"] = sha256(target)

    verify = dst / "verify.py"
    verify.write_text(VERIFY_SOURCE, encoding="utf-8")
    manifest["verify.py"] = sha256(verify)
    return manifest


def _source_audit(bundle: Path) -> None:
    for rel in SOURCE_FILES:
        text = (bundle / rel).read_text(encoding="utf-8")
        for token in FORBIDDEN_SOURCE_TOKENS:
            if token in text:
                raise ValueError(f"forbidden live founder/source dependency token {token!r} in {rel}")


def _run_isolated(bundle: Path) -> dict:
    env = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": str(bundle / "isolated-home"),
        "PYTHONNOUSERSITE": "1",
    }
    proc = subprocess.run(
        [sys.executable, "-I", str(bundle / "verify.py")],
        cwd=bundle,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
    )
    if proc.returncode != 0:
        raise ValueError(
            "isolated verifier failed:\nSTDOUT:\n"
            + proc.stdout
            + "\nSTDERR:\n"
            + proc.stderr
        )
    return json.loads(proc.stdout)


def audit() -> dict:
    with tempfile.TemporaryDirectory(prefix="venus-u1-founder-ablation-") as td:
        bundle = Path(td) / "bundle"
        bundle.mkdir(parents=True)
        manifest = _copy_bundle(bundle)
        _source_audit(bundle)
        result = _run_isolated(bundle)

        first = result["first"]
        expected = {
            "parent_correct": 5,
            "successor_correct": 8,
            "ablated_correct": 5,
            "total": 8,
            "safety_floor_unchanged": True,
            "rollback_available": True,
            "ctl_ostar_admitted": True,
            "promotion_authority": False,
            "successor_present": True,
        }
        for key, value in expected.items():
            if first.get(key) != value:
                raise ValueError(f"isolated recurrence drift: {key}={first.get(key)!r}")

        if not all(result["label_invariant_metrics"].values()):
            raise ValueError("problem/source label renaming changed consequence metrics")
        if not result["provenance_changes"]:
            raise ValueError("renamed provenance failed to change provenance-bound identities")

        # Required-artifact deletion must fail closed.
        missing = bundle / "artifacts" / "SSR1_TRANSFORM_REPAIR_HELDOUT_RETURN.json"
        missing.unlink()
        proc = subprocess.run(
            [sys.executable, "-I", str(bundle / "verify.py")],
            cwd=bundle,
            env={
                "PATH": os.environ.get("PATH", ""),
                "HOME": str(bundle / "isolated-home"),
                "PYTHONNOUSERSITE": "1",
            },
            text=True,
            capture_output=True,
            timeout=60,
        )
        if proc.returncode == 0:
            raise ValueError("missing required return artifact did not fail closed")

        return {
            "schema": "Venus.U1FounderSourceAblationAudit.v0.1",
            "status": "PASS_BOUNDED_RECOMPILED_U1_FOUNDER_SOURCE_ABLATION",
            "isolated_mode": True,
            "fresh_directory": True,
            "repository_root_required_at_runtime": False,
            "canonical_library_required": False,
            "conversation_state_required": False,
            "network_admitted": False,
            "bundle_manifest": manifest,
            "baseline": result["first"],
            "renamed": result["renamed"],
            "label_invariant_metrics": result["label_invariant_metrics"],
            "provenance_changes_under_rename": result["provenance_changes"],
            "missing_artifact_fails_closed": True,
            "independent_external_replication": False,
            "promotion_authority": False,
            "open_ended_rsi": False,
            "agi": False,
            "consciousness": False,
        }


def main() -> int:
    try:
        result = audit()
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
