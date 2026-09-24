from __future__ import annotations

"""Execute only fixed, repository-owned checks selected by a Venus proposal."""

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

from kernel.runtime.vmk2 import digest


SAFE_COMMANDS: Mapping[str, tuple[str, ...]] = {
    "AUDIT_AUTONOMY_MATRIX": (sys.executable, "scripts/audit_autonomy_safety_matrix.py"),
    "UNIT_AUTONOMY": (
        sys.executable, "-m", "unittest",
        "tests.test_autonomous_worker",
        "tests.test_autonomous_governance",
    ),
    "UNIT_INTERNAL_OSTAR": (
        sys.executable, "-m", "unittest",
        "tests.test_internal_ostar_causality",
        "tests.test_internal_ostar_source_removal",
    ),
    "UNIT_WORLD_INPUT_SECURITY": (
        sys.executable, "-m", "unittest",
        "tests.test_world_input_security_public_dev",
    ),
    "FULL_UNIT_SUITE": (
        sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py",
    ),
}


@dataclass(frozen=True)
class CheckResult:
    check_id: str
    returncode: int
    stdout_sha256: str
    stderr_sha256: str
    passed: bool


@dataclass(frozen=True)
class ProposalEvidence:
    schema: str
    evidence_id: str
    proposal_id: str
    status: str
    results: tuple[CheckResult, ...]
    all_local_checks_passed: bool
    external_return_satisfied: bool
    promotion_authority: bool = False


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def run_proposal_checks(proposal: Mapping[str, Any], *, cwd: str | Path = ".") -> ProposalEvidence:
    if proposal.get("arbitrary_code_write_authority") is not False:
        raise ValueError("proposal may not carry arbitrary code-write authority")
    if proposal.get("promotion_authority") is not False:
        raise ValueError("proposal may not carry promotion authority")

    results: list[CheckResult] = []
    for check_id in proposal.get("check_ids", ()):
        check_id = str(check_id)
        command = SAFE_COMMANDS.get(check_id)
        if command is None:
            raise ValueError(f"unrecognized check id: {check_id}")
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            text=True,
            capture_output=True,
            check=False,
        )
        results.append(CheckResult(
            check_id=check_id,
            returncode=completed.returncode,
            stdout_sha256=_sha(completed.stdout),
            stderr_sha256=_sha(completed.stderr),
            passed=completed.returncode == 0,
        ))

    all_passed = all(x.passed for x in results)
    external_required = bool(proposal.get("external_return_required"))
    if external_required:
        status = "WITHHOLD_EXTERNAL_RETURN"
    else:
        status = "LOCAL_CHECKS_PASS" if all_passed else "LOCAL_CHECKS_FAIL"

    body = {
        "schema": "Venus.AutonomousProposalEvidence.v0.1",
        "proposal_id": str(proposal["proposal_id"]),
        "status": status,
        "results": tuple(asdict(x) for x in results),
        "all_local_checks_passed": all_passed,
        "external_return_satisfied": False,
        "promotion_authority": False,
    }
    return ProposalEvidence(
        schema=body["schema"],
        evidence_id=digest(body),
        proposal_id=body["proposal_id"],
        status=status,
        results=tuple(results),
        all_local_checks_passed=all_passed,
        external_return_satisfied=False,
        promotion_authority=False,
    )


def evidence_dict(evidence: ProposalEvidence) -> dict[str, Any]:
    out = asdict(evidence)
    return out
