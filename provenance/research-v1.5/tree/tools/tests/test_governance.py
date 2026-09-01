from __future__ import annotations

import subprocess
import sys

from research_tools.paths import get_paths
from research_tools.validate.governance import (
    _authorize_edit_path,
    _canonicalize_repo_relative_path,
    validate_current_claims,
    validate_current_surface_hygiene,
    validate_current_surfaces,
    validate_support_surface_boundaries,
    validate_subsystem_registry,
    validate_repository_file_registry,
    validate_repository_minimality,
    validate_routing_surfaces,
    validate_merged_doc_quality,
    validate_edit_scope,
)


def _cleanup_transients(repo_root):
    for path in sorted(repo_root.rglob('*.pyc')):
        path.unlink()
    for path in sorted(repo_root.rglob('*'), reverse=True):
        if path.is_dir() and path.name in {'__pycache__', '.mypy_cache', '.pytest_cache', '.ruff_cache'}:
            import shutil; shutil.rmtree(path)


def test_governance_validations_pass() -> None:
    repo_root = get_paths().research_root
    _cleanup_transients(repo_root)
    results = []
    results.extend(validate_current_surfaces(repo_root))
    results.extend(validate_subsystem_registry(repo_root))
    results.extend(validate_repository_file_registry(repo_root))
    results.extend(validate_current_claims(repo_root))
    results.extend(validate_repository_minimality(repo_root))
    results.extend(validate_routing_surfaces(repo_root))
    results.extend(validate_merged_doc_quality(repo_root))
    results.extend(validate_edit_scope(repo_root))
    assert not [result for result in results if result.status == 'fail']


def test_package_doctor_passes() -> None:
    repo_root = get_paths().research_root
    _cleanup_transients(repo_root)
    run = subprocess.run([sys.executable, str(repo_root / 'package_doctor.py')], capture_output=True, text=True)
    assert run.returncode == 0, run.stdout + run.stderr


def test_current_surface_hygiene_catches_stale_wrapper_fragment(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "governance").mkdir(parents=True)
    (repo / "structured-unity-framework" / "governance").mkdir(parents=True)
    bad = repo / "bad.md"
    bad.write_text("see docs/state/PROJECT_STATUS.md\n", encoding="utf-8")
    root_registry = {"current_files": ["bad.md"], "live_entrypoints": ["bad.md"]}
    suf_registry = {"current_files": [], "live_entrypoints": []}
    import json
    (repo / "governance" / "CURRENT_SURFACES_REGISTRY_v0_1.json").write_text(json.dumps(root_registry), encoding="utf-8")
    (repo / "structured-unity-framework" / "governance" / "CURRENT_SURFACES_REGISTRY_v0_1.json").write_text(json.dumps(suf_registry), encoding="utf-8")

    results = validate_current_surface_hygiene(repo)

    assert any(result.status == "fail" for result in results)


def test_current_surface_hygiene_catches_archived_governance_reference(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "governance").mkdir(parents=True)
    (repo / "structured-unity-framework" / "governance").mkdir(parents=True)
    bad = repo / "bad.md"
    bad.write_text("see governance/AUTHORITATIVE_SOURCES_v0_1.json\n", encoding="utf-8")
    import json
    gov = {
        "current_surfaces": {
            "root_entrypoints": ["bad.md"],
            "root_governance": [],
            "package_entrypoints": {},
            "assisted_use": None,
        }
    }
    (repo / "governance" / "GOVERNANCE_CORE_v0_2.json").write_text(json.dumps(gov), encoding="utf-8")
    (repo / "structured-unity-framework" / "governance" / "CURRENT_SURFACES_REGISTRY_v0_1.json").write_text(
        json.dumps({"current_files": [], "live_entrypoints": []}),
        encoding="utf-8",
    )

    results = validate_current_surface_hygiene(repo)

    assert any(result.status == "fail" for result in results)


def test_routing_surfaces_catch_orphan(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "governance").mkdir(parents=True)
    (repo / "structured-unity-framework" / "governance").mkdir(parents=True)
    (repo / "README.md").write_text("root only\n", encoding="utf-8")
    (repo / "START_HERE.md").write_text("root only\n", encoding="utf-8")
    (repo / "docs" / "frontdoor").mkdir(parents=True)
    (repo / "docs" / "frontdoor" / "PROJECT_PURPOSE_AND_USE_CASES.md").write_text("purpose\n", encoding="utf-8")
    (repo / "docs" / "frontdoor" / "CONTROL_AND_GOVERNANCE_SURFACE.md").write_text("control\n", encoding="utf-8")
    (repo / "governance" / "AUTHORITATIVE_INDEX_v0_1.md").write_text("index\n", encoding="utf-8")
    (repo / "orphan.md").write_text("current but unreachable\n", encoding="utf-8")
    import json
    (repo / "governance" / "CURRENT_SURFACES_REGISTRY_v0_1.json").write_text(json.dumps({"current_files": ["README.md", "START_HERE.md", "docs/frontdoor/PROJECT_PURPOSE_AND_USE_CASES.md", "docs/frontdoor/CONTROL_AND_GOVERNANCE_SURFACE.md", "governance/AUTHORITATIVE_INDEX_v0_1.md", "orphan.md"], "live_entrypoints": ["README.md"]}), encoding="utf-8")
    (repo / "structured-unity-framework" / "governance" / "CURRENT_SURFACES_REGISTRY_v0_1.json").write_text(json.dumps({"current_files": [], "live_entrypoints": []}), encoding="utf-8")

    results = validate_routing_surfaces(repo)

    assert any(result.status == "fail" for result in results)


def test_subsystem_registry_catches_duplicate_cluster_ids(tmp_path) -> None:
    import json

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "governance").mkdir(parents=True)
    (repo / "docs" / "frontdoor").mkdir(parents=True)
    (repo / "structured-unity-framework" / "governance").mkdir(parents=True)
    (repo / "governance" / "FEDERATED_SUBSYSTEM_PROTOCOL_v0_1.md").write_text("protocol\n", encoding="utf-8")
    (repo / "governance" / "AUTHORITATIVE_INDEX_v0_1.md").write_text("index\n", encoding="utf-8")
    (repo / "docs" / "frontdoor" / "CONTROL_AND_GOVERNANCE_SURFACE.md").write_text("control\n", encoding="utf-8")
    (repo / "structured-unity-framework" / "START_HERE.md").write_text("start\n", encoding="utf-8")
    (repo / "structured-unity-framework" / "governance" / "AUTHORITATIVE_INDEX_v0_1.md").write_text("index\n", encoding="utf-8")
    registry = {
        "version": "0.1.0",
        "purpose": "test",
        "subsystems": [
            {
                "id": "root-governance",
                "owner": "Research root governance",
                "purpose": "Own umbrella routing.",
                "visibility": "public",
                "scope_prefixes": ["governance/", "docs/frontdoor/"],
                "entry_surface": "governance/FEDERATED_SUBSYSTEM_PROTOCOL_v0_1.md",
                "authoritative_surface": "governance/AUTHORITATIVE_INDEX_v0_1.md",
                "validation_cluster": {
                    "cluster_id": "duplicate-cluster",
                    "source_files": ["docs/frontdoor/CONTROL_AND_GOVERNANCE_SURFACE.md"],
                },
            },
            {
                "id": "structured-unity-framework",
                "owner": "Structured Unity Framework",
                "purpose": "Own academic-core truth.",
                "visibility": "public",
                "scope_prefixes": ["structured-unity-framework/"],
                "entry_surface": "structured-unity-framework/START_HERE.md",
                "authoritative_surface": "structured-unity-framework/governance/AUTHORITATIVE_INDEX_v0_1.md",
                "validation_cluster": {
                    "cluster_id": "duplicate-cluster",
                    "source_files": ["structured-unity-framework/START_HERE.md"],
                },
            },
        ],
    }
    (repo / "governance" / "SUBSYSTEM_REGISTRY_v0_1.json").write_text(
        json.dumps(registry),
        encoding="utf-8",
    )

    results = validate_subsystem_registry(repo)

    assert any(
        result.check_name == "subsystem-cluster-ids-unique" and result.status == "fail"
        for result in results
    )


def test_subsystem_registry_catches_missing_entry_surface(tmp_path) -> None:
    import json

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "governance").mkdir(parents=True)
    (repo / "governance" / "AUTHORITATIVE_INDEX_v0_1.md").write_text("index\n", encoding="utf-8")
    registry = {
        "version": "0.1.0",
        "purpose": "test",
        "subsystems": [
            {
                "id": "root-governance",
                "owner": "Research root governance",
                "purpose": "Own umbrella routing.",
                "visibility": "public",
                "scope_prefixes": ["governance/"],
                "entry_surface": "governance/MISSING.md",
                "authoritative_surface": "governance/AUTHORITATIVE_INDEX_v0_1.md",
                "validation_cluster": {
                    "cluster_id": "root-governance",
                    "source_files": ["governance/AUTHORITATIVE_INDEX_v0_1.md"],
                },
            }
        ],
    }
    (repo / "governance" / "SUBSYSTEM_REGISTRY_v0_1.json").write_text(
        json.dumps(registry),
        encoding="utf-8",
    )

    results = validate_subsystem_registry(repo)

    assert any(
        result.check_name == "subsystem-entry-surfaces-exist" and result.status == "fail"
        for result in results
    )


def test_merged_doc_quality_catches_residue(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    from research_tools.validate.governance import MERGED_DOC_EXPECTATIONS
    for rel in MERGED_DOC_EXPECTATIONS:
        p2 = repo / rel
        p2.parent.mkdir(parents=True, exist_ok=True)
        p2.write_text("# placeholder\n## Table of contents\n## Provenance\n", encoding="utf-8")
    bad = repo / "structured-unity-framework" / "docs" / "argument" / "CONTRIBUTION_AND_POSITIONING.md"
    bad.write_text("# Contribution\n## Source surfaces preserved here\n", encoding="utf-8")

    results = validate_merged_doc_quality(repo)

    assert any(result.status == "fail" for result in results)


def test_support_surface_boundaries_catch_overclaim(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "structured-unity-framework" / "framework" / "research-program.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "# Research Program\nThis package is conclusively proven across all domains.\n",
        encoding="utf-8",
    )
    (repo / "structured-unity-framework" / "applications").mkdir(parents=True, exist_ok=True)
    (repo / "structured-unity-framework" / "applications" / "README.md").write_text(
        "# Applications Atlas\nThis layer does **not** imply that SUF is already validated across every mapped area.\n demonstrated routes\n research map\n",
        encoding="utf-8",
    )
    (repo / "structured-unity-framework" / "meta").mkdir(parents=True, exist_ok=True)
    (repo / "structured-unity-framework" / "meta" / "publication-scope.md").write_text(
        "# Publication Scope\nThe package is active, but not empirically closed.\nthat one demonstrated route proves the framework universally\nthat the current package already yields objectively settled cross-domain measurement or strong predictive closure\n",
        encoding="utf-8",
    )

    results = validate_support_surface_boundaries(repo)

    assert any(result.status == "fail" for result in results)


def test_merged_doc_quality_missing_file_fails_cleanly(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    results = validate_merged_doc_quality(repo)

    assert all(result.status == "fail" for result in results)
    assert all("unavailable" in result.message for result in results)


def test_support_surface_boundary_regex_avoids_negation_false_positive(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "structured-unity-framework" / "framework" / "research-program.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        """# Research Program
It does not replace the theory stack, prove phenomenology from metrics, or claim that one case confirms the whole framework.
It does not freeze one threshold system, one weighting scheme, or one aggregation formula across all future domains.
The package should not imply that current route-local estimators already yield objective cross-domain measurement or mature high-fit prediction.
It is not ready for broad deployment, and this does not generalize broadly.
""",
        encoding="utf-8",
    )
    (repo / "structured-unity-framework" / "applications").mkdir(parents=True, exist_ok=True)
    (repo / "structured-unity-framework" / "applications" / "README.md").write_text(
        """# Applications Atlas
This layer does **not** imply that SUF is already validated across every mapped area.
demonstrated routes
research map
""",
        encoding="utf-8",
    )
    (repo / "structured-unity-framework" / "meta").mkdir(parents=True, exist_ok=True)
    (repo / "structured-unity-framework" / "meta" / "publication-scope.md").write_text(
        """# Publication Scope
The package is active, but not empirically closed.
that one demonstrated route proves the framework universally
that the current package already yields objectively settled cross-domain measurement or strong predictive closure
""",
        encoding="utf-8",
    )

    results = validate_support_surface_boundaries(repo)

    assert not [result for result in results if result.status == "fail"]


def test_edit_scope_catches_out_of_scope_existing_file_change(tmp_path) -> None:
    import shutil
    import json
    import hashlib

    source = get_paths().research_root
    repo = tmp_path / "repo"
    shutil.copytree(source, repo)
    target = repo / "structured-unity-framework" / "meta" / "weak-naturalization.md"
    target.write_text(target.read_text(encoding="utf-8") + "\nThis proves SUF universally.\n", encoding="utf-8")

    results = validate_edit_scope(repo)

    assert any(result.check_name == "edit-scope-changes-within-policy" and result.status == "fail" for result in results)


def test_edit_scope_allows_current_surface_change(tmp_path) -> None:
    import shutil

    source = get_paths().research_root
    repo = tmp_path / "repo"
    shutil.copytree(source, repo)
    target = repo / "README.md"
    target.write_text(target.read_text(encoding="utf-8") + "\nTemporary current-surface wording update.\n", encoding="utf-8")

    results = validate_edit_scope(repo)

    assert not any(result.check_name == "edit-scope-changes-within-policy" and result.status == "fail" for result in results)


def test_edit_scope_allows_designated_tooling_change(tmp_path) -> None:
    import shutil

    source = get_paths().research_root
    repo = tmp_path / "repo"
    shutil.copytree(source, repo)
    target = repo / "tools" / "README.md"
    target.write_text(target.read_text(encoding="utf-8") + "\nTemporary tooling note.\n", encoding="utf-8")

    results = validate_edit_scope(repo)

    assert not any(result.check_name == "edit-scope-changes-within-policy" and result.status == "fail" for result in results)


def test_canonicalize_repo_relative_path_normalizes_aliases() -> None:
    assert _canonicalize_repo_relative_path('./tools//../tools/README.md') == 'tools/README.md'
    assert _canonicalize_repo_relative_path('governance/./CURRENT_SURFACES_REGISTRY_v0_1.json') == 'governance/CURRENT_SURFACES_REGISTRY_v0_1.json'


def test_canonicalize_repo_relative_path_rejects_escape() -> None:
    assert _canonicalize_repo_relative_path('../README.md') is None
    assert _canonicalize_repo_relative_path('../../tools/README.md') is None


def test_authorize_edit_path_uses_canonical_aliases_consistently() -> None:
    decision = _authorize_edit_path(
        './tools//../tools/README.md',
        always_files=set(),
        declared_files=set(),
        always_prefixes=('tools/',),
        declared_prefixes=(),
    )

    assert decision['editable'] is True
    assert decision['canonical_path'] == 'tools/README.md'
    assert decision['reason'] == 'always-prefix'


def test_authorize_edit_path_rejects_prefix_near_miss() -> None:
    decision = _authorize_edit_path(
        'toolshed/README.md',
        always_files=set(),
        declared_files=set(),
        always_prefixes=('tools/',),
        declared_prefixes=(),
    )

    assert decision['editable'] is False
    assert decision['reason'] == 'out-of-scope'


def test_repository_file_registry_ignores_operational_artifacts(tmp_path) -> None:
    import json

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "governance").mkdir(parents=True)
    (repo / "structured-unity-framework" / "governance").mkdir(parents=True)
    (repo / "README.md").write_text("root\n", encoding="utf-8")
    (repo / ".git").mkdir()
    (repo / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (repo / "tools" / "out").mkdir(parents=True)
    (repo / "tools" / "out" / "report.md").write_text("generated\n", encoding="utf-8")
    (repo / "tools" / ".ruff_cache").mkdir(parents=True)
    (repo / "tools" / ".ruff_cache" / "cache").write_text("cache\n", encoding="utf-8")

    root_registry = {
        "scope_prefix": "",
        "files": [
            {"path": "README.md", "category": "README.md", "extension": ".md"},
            {"path": "governance/REPOSITORY_FILE_REGISTRY_v0_1.json", "category": "REPOSITORY_FILE_REGISTRY_v0_1.json", "extension": ".json"},
            {"path": "structured-unity-framework/governance/REPOSITORY_FILE_REGISTRY_v0_1.json", "category": "REPOSITORY_FILE_REGISTRY_v0_1.json", "extension": ".json"},
        ],
    }
    suf_registry = {
        "scope_prefix": "structured-unity-framework/",
        "files": [
            {
                "path": "structured-unity-framework/governance/REPOSITORY_FILE_REGISTRY_v0_1.json",
                "category": "REPOSITORY_FILE_REGISTRY_v0_1.json",
                "extension": ".json",
            }
        ],
    }
    (repo / "governance" / "REPOSITORY_FILE_REGISTRY_v0_1.json").write_text(json.dumps(root_registry), encoding="utf-8")
    (repo / "structured-unity-framework" / "governance" / "REPOSITORY_FILE_REGISTRY_v0_1.json").write_text(json.dumps(suf_registry), encoding="utf-8")

    results = validate_repository_file_registry(repo)

    assert not [result for result in results if result.status == "fail"]


def test_edit_scope_ignores_operational_artifacts(tmp_path) -> None:
    import json
    import hashlib

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "governance").mkdir(parents=True)
    (repo / "structured-unity-framework" / "governance").mkdir(parents=True)
    (repo / "README.md").write_text("root\n", encoding="utf-8")
    (repo / ".git").mkdir()
    (repo / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (repo / "tools" / "out").mkdir(parents=True)
    (repo / "tools" / "out" / "report.md").write_text("generated\n", encoding="utf-8")
    (repo / "tools" / ".ruff_cache").mkdir(parents=True)
    (repo / "tools" / ".ruff_cache" / "cache").write_text("cache\n", encoding="utf-8")

    policy_path = repo / "governance" / "AGENT_EDIT_SCOPE_POLICY_v0_1.json"
    baseline_path = repo / "governance" / "REPOSITORY_EDIT_BASELINE_v0_1.json"
    current_registry_path = repo / "governance" / "CURRENT_SURFACES_REGISTRY_v0_1.json"
    suf_registry_path = repo / "structured-unity-framework" / "governance" / "CURRENT_SURFACES_REGISTRY_v0_1.json"

    policy = {
        "version": "0.1.0",
        "purpose": "test",
        "include_current_surfaces": True,
        "always_allowed_files": [],
        "always_allowed_prefixes": [],
        "declared_allowed_files": ["governance/AGENT_EDIT_SCOPE_POLICY_v0_1.json"],
        "declared_allowed_prefixes": [],
        "notes": [],
        "excluded_from_baseline": ["governance/REPOSITORY_EDIT_BASELINE_v0_1.json"],
    }

    current_registry = {
        "current_files": [
            "README.md",
            "governance/CURRENT_SURFACES_REGISTRY_v0_1.json",
            "structured-unity-framework/governance/CURRENT_SURFACES_REGISTRY_v0_1.json",
        ],
        "live_entrypoints": ["README.md"],
    }
    empty_suf_registry = {
        "current_files": ["structured-unity-framework/governance/CURRENT_SURFACES_REGISTRY_v0_1.json"],
        "live_entrypoints": [],
    }

    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    current_registry_path.write_text(json.dumps(current_registry), encoding="utf-8")
    suf_registry_path.write_text(json.dumps(empty_suf_registry), encoding="utf-8")

    baseline = {
        "version": "0.1.0",
        "files": [
            {"path": "README.md", "sha256": hashlib.sha256((repo / "README.md").read_bytes()).hexdigest()},
            {"path": "governance/AGENT_EDIT_SCOPE_POLICY_v0_1.json", "sha256": hashlib.sha256(policy_path.read_bytes()).hexdigest()},
            {"path": "governance/CURRENT_SURFACES_REGISTRY_v0_1.json", "sha256": hashlib.sha256(current_registry_path.read_bytes()).hexdigest()},
            {"path": "structured-unity-framework/governance/CURRENT_SURFACES_REGISTRY_v0_1.json", "sha256": hashlib.sha256(suf_registry_path.read_bytes()).hexdigest()},
        ],
    }
    baseline_path.write_text(json.dumps(baseline), encoding="utf-8")

    results = validate_edit_scope(repo)

    assert not any(result.check_name == "edit-scope-changes-within-policy" and result.status == "fail" for result in results)
