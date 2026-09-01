from __future__ import annotations

import json
import os
import sys
import shutil
from pathlib import Path

sys.dont_write_bytecode = True
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")

from authoritative_guard import AuthorityError, verify_integrity

BASE = Path(__file__).resolve().parent
TOOLS_SRC = BASE / "tools" / "src"
if str(TOOLS_SRC) not in sys.path:
    sys.path.insert(0, str(TOOLS_SRC))

from research_tools.paths import get_paths  # noqa: E402
from research_tools.validate.governance import (  # noqa: E402
    validate_current_claims,
    validate_current_surfaces,
    validate_subsystem_registry,
    validate_repository_file_registry,
    validate_repository_minimality,
    validate_routing_surfaces,
    validate_merged_doc_quality,
    validate_edit_scope,
)
from research_tools.workflows.validate_clusters import collect_validation_clusters  # noqa: E402
from research_tools.workflows.validate_all import collect_validation_results  # noqa: E402



def cleanup_transient_artifacts(base: Path) -> tuple[list[str], list[str]]:
    removed_dirs: list[str] = []
    removed_files: list[str] = []
    for file_path in sorted(base.rglob('*.pyc')):
        if file_path.is_file():
            file_path.unlink()
            removed_files.append(file_path.relative_to(base).as_posix())
    for file_path in sorted(base.rglob('.DS_Store')):
        if file_path.is_file():
            file_path.unlink()
            removed_files.append(file_path.relative_to(base).as_posix())
    for pattern in ('__pycache__', '.mypy_cache', '.pytest_cache', '.ruff_cache'):
        for directory in sorted(base.rglob(pattern), reverse=True):
            if directory.is_dir():
                shutil.rmtree(directory)
                removed_dirs.append(directory.relative_to(base).as_posix())
    return removed_dirs, removed_files

def _safe_read_text(path: Path) -> tuple[str | None, str | None]:
    if not path.exists():
        return None, f"missing file: {path.relative_to(BASE).as_posix()}"
    if not path.is_file():
        return None, f"not a regular file: {path.relative_to(BASE).as_posix()}"
    return path.read_text(encoding="utf-8"), None


def main() -> None:
    checks = []
    issues = []

    def record(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"check": name, "ok": ok, "detail": detail})
        if not ok:
            issues.append({"check": name, "detail": detail})

    removed_dirs, removed_files = cleanup_transient_artifacts(BASE)
    remaining_transients = [
        p.relative_to(BASE).as_posix()
        for p in BASE.rglob('*')
        if (p.is_dir() and p.name in {'__pycache__', '.mypy_cache', '.pytest_cache', '.ruff_cache'})
        or (p.is_file() and (p.suffix == '.pyc' or p.name == '.DS_Store'))
    ]
    record(
        'layout:transient-artifacts-clean',
        not remaining_transients,
        f'removed_dirs={removed_dirs} removed_files={removed_files} remaining={remaining_transients}',
    )

    try:
        integrity = verify_integrity(strict=True)
        record("integrity:manifest-pass", integrity["status"] == "PASS", f"verified_files={integrity['verified_files']}")
    except AuthorityError as e:
        record("integrity:manifest-pass", False, str(e))

    for rel in [
        "START_HERE.md",
        "docs/frontdoor/PROJECT_PURPOSE_AND_USE_CASES.md",
        "docs/frontdoor/CONTROL_AND_GOVERNANCE_SURFACE.md",
        "governance/AUTHORITATIVE_INDEX_v0_2.md",
        "structured-unity-framework/START_HERE.md",
        "structured-unity-framework/governance/AUTHORITATIVE_INDEX_v0_1.md",
    ]:
        p = BASE / rel
        record(f"exists:{rel}", p.exists(), "present" if p.exists() else f"missing {rel}")

    os.environ.setdefault("PYTHONPATH", str(TOOLS_SRC))
    paths = get_paths()
    validation_results = collect_validation_results(paths)
    failed_validation = [r for r in validation_results if r.status == "fail"]
    record(
        "tools:validate-all-pass",
        not failed_validation,
        "none" if not failed_validation else "; ".join(f"{r.check_name}:{r.message}" for r in failed_validation[:20]),
    )
    cluster_runs = collect_validation_clusters(paths)
    failed_clusters = [cluster for cluster in cluster_runs if cluster.failed]
    record(
        "tools:validate-clusters-pass",
        not failed_clusters,
        (
            "none"
            if not failed_clusters
            else "; ".join(
                f"{cluster.spec.cluster_id}:{cluster.failed} failures"
                for cluster in failed_clusters[:20]
            )
        ),
    )


    suf_audit_path = BASE / "structured-unity-framework/docs/audit/OBJECTIONS_AND_EVIDENCE_STATUS.md"
    suf_control_path = BASE / "structured-unity-framework/docs/frontdoor/CONTROL_AND_GOVERNANCE_SURFACE.md"
    suf_execution_path = BASE / "structured-unity-framework/docs/current-execution-order.md"

    suf_audit_text, audit_error = _safe_read_text(suf_audit_path)
    record(
        "suf:locked-payoff-trail-present",
        audit_error is None and "### Inferential trail `IT-001`" in suf_audit_text and "### Weakening conditions and revision triggers" in suf_audit_text,
        "locked payoff trail and weakening conditions must both be present" if audit_error is None else audit_error,
    )
    suf_control_text, control_error = _safe_read_text(suf_control_path)
    record(
        "suf:interpretive-pressure-surface-present",
        control_error is None and "## Interpretive pressure and minimum challenge tooling" in suf_control_text and "O / C / M / I / P" in suf_control_text,
        "control surface must keep interpretive-pressure language explicit" if control_error is None else control_error,
    )
    # `suf:execution-order-parallel-instrumentation` was dropped 2026-04-20:
    # Taiwan chapter is complete (20 events landed, three-case synthesis closed).
    # The "parallel-to-Taiwan instrumentation" hook belonged to an earlier phase.
    # If a new parallel-work discipline is needed, re-add with current wording.
    _ = suf_execution_path  # kept for future phase checks

    for name, results in [
        ("audit:current-surfaces", validate_current_surfaces(BASE)),
        ("audit:subsystem-registry", validate_subsystem_registry(BASE)),
        ("audit:file-registry", validate_repository_file_registry(BASE)),
        ("audit:current-claims", validate_current_claims(BASE)),
        ("audit:minimality", validate_repository_minimality(BASE)),
        ("audit:routing", validate_routing_surfaces(BASE)),
        ("audit:merged-doc-quality", validate_merged_doc_quality(BASE)),
        ("audit:edit-scope", validate_edit_scope(BASE)),
    ]:
        failed = [r for r in results if r.status == "fail"]
        record(name, not failed, "none" if not failed else "; ".join(f"{r.check_name}:{r.message}" for r in failed[:20]))

    status = "PASS" if not issues else "FAIL"
    summary = {
        "doctor_version": "0.2.0",
        "status": status,
        "total_checks": len(checks),
        "passed_checks": sum(1 for c in checks if c["ok"]),
        "failed_checks": sum(1 for c in checks if not c["ok"]),
        "issues": issues,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    sys.exit(0 if status == "PASS" else 1)


if __name__ == "__main__":
    main()
