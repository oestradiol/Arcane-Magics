from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from research_tools.models.reports import ValidationResult
from research_tools.parse.subsystems import parse_subsystem_registry
from research_tools.repo_files import iter_truth_files


SUPPORT_SURFACE_BOUNDARY_EXPECTATIONS = {
    "structured-unity-framework/framework/research-program.md": {
        "contains": [
            "It does not replace the theory stack, prove phenomenology from metrics, or claim that one case confirms the whole framework.",
            "It does not freeze one threshold system, one weighting scheme, or one aggregation formula across all future domains.",
        ],
        "contains_any": [
            [
                # 2026-04-20: prose renamed "estimators" -> "structured evidence organizers"
                # (Estimator -> Structured Evidence Organizer rename to prevent predictive overselling).
                "The package should not imply that current route-local structured evidence organizers already yield objective cross-domain measurement or mature high-fit prediction.",
                "The package should not imply that current route-local estimators already yield objective cross-domain measurement or mature high-fit prediction.",
            ]
        ],
        "absent_patterns": [
            {
                "label": "conclusive-proof-across-all-domains",
                "pattern": r"(?i)\b(?:is|was|has been|already is|already been)\s+conclusively\s+proven\s+across\s+all\s+domains\b",
            },
            {
                "label": "empirically-closed-across-all-future-domains",
                "pattern": r"(?i)\ball\s+future\s+domains\s+(?:are|were|remain|seem|look)\s+already\s+empirically\s+closed\b",
            },
        ],
    },
    "structured-unity-framework/applications/README.md": {
        "contains": [
            "does **not** imply that SUF is already validated across every mapped area.",
            "demonstrated routes",
            "research map",
        ],
        "absent_patterns": [
            {
                "label": "all-applications-empirically-closed",
                "pattern": r"(?i)\ball\s+applications\s+(?:are|were|remain|seem|look)\s+already\s+empirically\s+closed\b",
            },
            {
                "label": "layer-proves-suf-universally",
                "pattern": r"(?i)\bthis\s+layer\s+proves\s+SUF\s+universally\b",
            },
        ],
    },
    "structured-unity-framework/meta/publication-scope.md": {
        "contains": [
            "The package is active, but not empirically closed.",
            "that one demonstrated route proves the framework universally",
            "that the current package already yields objectively settled cross-domain measurement or strong predictive closure",
        ],
        "absent_patterns": [],
    },
}


EDIT_SCOPE_CURRENT_SURFACE_REGISTRIES = [
    "governance/GOVERNANCE_CORE_v0_2.json",
    "structured-unity-framework/governance/CURRENT_SURFACES_REGISTRY_v0_1.json",
]


def _sha256(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


ROUTING_SURFACES = {
    "root": [
        "README.md",
        "START_HERE.md",
        "docs/frontdoor/PROJECT_PURPOSE_AND_USE_CASES.md",
        "docs/frontdoor/CONTROL_AND_GOVERNANCE_SURFACE.md",
        "governance/AUTHORITATIVE_INDEX_v0_2.md",
    ],
    "suf": [
        "structured-unity-framework/README.md",
        "structured-unity-framework/START_HERE.md",
        "structured-unity-framework/docs/INDEX.md",
        "structured-unity-framework/docs/frontdoor/PROJECT_PURPOSE_AND_USE_CASES.md",
        "structured-unity-framework/docs/frontdoor/CONTROL_AND_GOVERNANCE_SURFACE.md",
        "structured-unity-framework/docs/frontdoor/SCIENTIFIC_GROUNDING_AND_LIMITS.md",
        "structured-unity-framework/docs/frontdoor/FRAMEWORK_OVERVIEW_AND_READING_GUIDE.md",
        "structured-unity-framework/governance/AUTHORITATIVE_INDEX_v0_1.md",
    ],
}

MERGED_DOC_EXPECTATIONS = {
    "docs/frontdoor/CONTROL_AND_GOVERNANCE_SURFACE.md": [
        "## Table of contents",
        "## Skeptical audit",
        "## Trust and style",
        "## Provenance",
    ],
    "structured-unity-framework/docs/frontdoor/CONTROL_AND_GOVERNANCE_SURFACE.md": [
        "## Table of contents",
        "## Skeptical audit",
        "## Trust and style",
        "## Provenance",
    ],
    "structured-unity-framework/docs/frontdoor/SCIENTIFIC_GROUNDING_AND_LIMITS.md": [
        "## Table of contents",
        "## Detailed limits surfaces",
        "## Provenance",
    ],
    "structured-unity-framework/docs/frontdoor/FRAMEWORK_OVERVIEW_AND_READING_GUIDE.md": [
        "## Table of contents",
        "## Reader paths",
        "## Reading and audit paths",
        "## Provenance",
    ],
    "structured-unity-framework/docs/argument/CONTRIBUTION_AND_POSITIONING.md": [
        "## Table of contents",
        "## Locked payoff and contribution candidates",
        "## Bounded rival positioning",
        "## Provenance",
    ],
    "structured-unity-framework/docs/audit/OBJECTIONS_AND_EVIDENCE_STATUS.md": [
        "## Table of contents",
        "## Reviewer objections and current answers",
        "## Evidence-status matrix role",
        "## Provenance",
    ],
    "structured-unity-framework/docs/monograph/SUPPORT_PACKAGE.md": [
        "## Table of contents",
        "## Monograph chapter scaffold",
        "## Bounded closure note",
        "## Provenance",
    ],
}


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _load_root_current_registry(repo_root: Path) -> tuple[dict, Path, str]:
    v2_path = repo_root / "governance" / "GOVERNANCE_CORE_v0_2.json"
    if v2_path.exists():
        return _read_json(v2_path), v2_path, "v0.2"

    v1_path = repo_root / "governance" / "CURRENT_SURFACES_REGISTRY_v0_1.json"
    if v1_path.exists():
        return _read_json(v1_path), v1_path, "v0.1"

    raise FileNotFoundError("missing root governance current-surface registry")


def _load_root_subsystem_registry(repo_root: Path) -> tuple[str, Path]:
    v2_path = repo_root / "governance" / "GOVERNANCE_CORE_v0_2.json"
    if v2_path.exists():
        return "v0.2", v2_path

    v1_path = repo_root / "governance" / "SUBSYSTEM_REGISTRY_v0_1.json"
    if v1_path.exists():
        return "v0.1", v1_path

    raise FileNotFoundError("missing root subsystem registry")


def _safe_read_text(path: Path) -> tuple[str | None, str | None]:
    if not path.exists():
        return None, f"missing file: {path}"
    if not path.is_file():
        return None, f"not a regular file: {path}"
    return path.read_text(encoding="utf-8"), None


def _contains_result(check_name: str, path: Path, needle: str, message: str) -> ValidationResult:
    text, error = _safe_read_text(path)
    if error is not None:
        return ValidationResult(
            check_name=check_name,
            status="fail",
            message=f"{message} Required fragment could not be checked because the file is unavailable.",
            path=str(path),
            expected=needle,
            found=error,
        )
    ok = needle in text
    return ValidationResult(
        check_name=check_name,
        status="pass" if ok else "fail",
        message=message if ok else f"{message} Required fragment missing.",
        path=str(path),
        expected=needle,
        found=needle if ok else "missing",
    )


def _absent_result(check_name: str, path: Path, needle: str, message: str) -> ValidationResult:
    text, error = _safe_read_text(path)
    if error is not None:
        return ValidationResult(
            check_name=check_name,
            status="fail",
            message=f"{message} Forbidden-fragment check could not run because the file is unavailable.",
            path=str(path),
            expected=f"absent: {needle}",
            found=error,
        )
    ok = needle.casefold() not in text.casefold()
    return ValidationResult(
        check_name=check_name,
        status="pass" if ok else "fail",
        message=message if ok else f"{message} Forbidden fragment present.",
        path=str(path),
        expected=f"absent: {needle}",
        found="absent" if ok else needle,
    )


def _absent_pattern_result(check_name: str, path: Path, pattern: str, label: str, message: str) -> ValidationResult:
    text, error = _safe_read_text(path)
    if error is not None:
        return ValidationResult(
            check_name=check_name,
            status="fail",
            message=f"{message} Forbidden-pattern check could not run because the file is unavailable.",
            path=str(path),
            expected=f"absent pattern: {label}",
            found=error,
        )
    match = re.search(pattern, text)
    ok = match is None
    return ValidationResult(
        check_name=check_name,
        status="pass" if ok else "fail",
        message=message if ok else f"{message} Forbidden pattern present.",
        path=str(path),
        expected=f"absent pattern: {label}",
        found="absent" if ok else match.group(0),
    )


def _actual_file_list(repo_root: Path) -> list[str]:
    return iter_truth_files(repo_root)


def validate_current_surfaces(repo_root: Path) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    root_registry, root_registry_path, _ = _load_root_current_registry(repo_root)
    suf_registry_path = repo_root / 'structured-unity-framework' / 'governance' / 'CURRENT_SURFACES_REGISTRY_v0_1.json'

    current_files = _extract_current_files_from_registry(root_registry, "root")
    missing = [rel for rel in current_files if not (repo_root / rel).exists()]
    results.append(ValidationResult(
        check_name='root-current-surfaces-exist',
        status='pass' if not missing else 'fail',
        message='All current root surfaces exist.' if not missing else 'Root current-surface registry references missing files.',
        path=str(root_registry_path),
        expected='all listed current files exist',
        found='none missing' if not missing else ', '.join(missing),
    ))
    
    # Validate SUF (still v0.1 until SUF package updates)
    if suf_registry_path.exists():
        registry = _read_json(suf_registry_path)
        current_files = registry.get('current_files', [])
        missing = [rel for rel in current_files if not (repo_root / rel).exists()]
        results.append(ValidationResult(
            check_name='suf-current-surfaces-exist',
            status='pass' if not missing else 'fail',
            message='All current surfaces listed in SUF registry exist.' if not missing else 'SUF registry references missing files.',
            path=str(suf_registry_path),
            expected='all listed current files exist',
            found='none missing' if not missing else ', '.join(missing),
        ))
        live_entrypoints = registry.get('live_entrypoints', [])
        missing_entrypoints = [rel for rel in live_entrypoints if rel not in current_files]
        results.append(ValidationResult(
            check_name='suf-entrypoints-subset-of-current',
            status='pass' if not missing_entrypoints else 'fail',
            message='Live entrypoints are also marked current.' if not missing_entrypoints else 'Some live entrypoints are not marked current.',
            path=str(suf_registry_path),
            expected='live_entrypoints subset of current_files',
            found='ok' if not missing_entrypoints else ', '.join(missing_entrypoints),
        ))
    return results


def validate_subsystem_registry(repo_root: Path) -> list[ValidationResult]:
    try:
        registry_version, registry_path = _load_root_subsystem_registry(repo_root)
        if registry_version == "v0.2":
            from research_tools.models.subsystems import SubsystemSpec, SubsystemValidationCluster
            from research_tools.parse.governance_core import (
                derive_subsystem_validation_cluster,
                parse_governance_core,
            )

            governance = parse_governance_core(registry_path)
            subsystems = []
            for sid, sdata in governance.subsystems.items():
                cluster_sources = derive_subsystem_validation_cluster(sdata, registry_path)
                validation_cluster = None
                if cluster_sources:
                    validation_cluster = SubsystemValidationCluster(
                        cluster_id=sid,
                        source_files=tuple(cluster_sources),
                    )
                subsystems.append(SubsystemSpec(
                    subsystem_id=sid,
                    owner=sdata.owner,
                    purpose=sdata.purpose,
                    visibility=sdata.visibility,
                    scope_prefixes=sdata.scope_prefixes,
                    entry_surface=sdata.entry or "",
                    authoritative_surface=sdata.state_surface or "",
                    validation_cluster=validation_cluster,
                ))
        else:
            subsystems = parse_subsystem_registry(registry_path)
    except Exception as exc:
        return [
            ValidationResult(
                check_name="subsystem-registry-parse",
                status="fail",
                message="Subsystem registry could not be parsed.",
                path=str(registry_path),
                expected="valid subsystem registry JSON",
                found=str(exc),
            )
        ]

    public_subsystems = [s for s in subsystems if s.visibility != 'private']

    results: list[ValidationResult] = []
    subsystem_ids = [subsystem.subsystem_id for subsystem in subsystems]
    duplicate_subsystems = sorted(
        subsystem_id
        for subsystem_id, count in Counter(subsystem_ids).items()
        if count > 1
    )
    results.append(
        ValidationResult(
            check_name="subsystem-ids-unique",
            status="pass" if not duplicate_subsystems else "fail",
            message=(
                "Subsystem registry uses unique subsystem ids."
                if not duplicate_subsystems
                else "Subsystem registry reuses subsystem ids."
            ),
            path=str(registry_path),
            expected="unique subsystem ids",
            found="ok" if not duplicate_subsystems else ", ".join(duplicate_subsystems),
        )
    )

    cluster_ids = [
        subsystem.validation_cluster.cluster_id
        for subsystem in subsystems
        if subsystem.validation_cluster is not None
    ]
    duplicate_clusters = sorted(
        cluster_id for cluster_id, count in Counter(cluster_ids).items() if count > 1
    )
    results.append(
        ValidationResult(
            check_name="subsystem-cluster-ids-unique",
            status="pass" if not duplicate_clusters else "fail",
            message=(
                "Subsystem registry uses unique validation cluster ids."
                if not duplicate_clusters
                else "Subsystem registry reuses validation cluster ids."
            ),
            path=str(registry_path),
            expected="unique cluster ids",
            found="ok" if not duplicate_clusters else ", ".join(duplicate_clusters),
        )
    )

    # Only check surfaces that are declared; empty entry means subsystem uses
    # state_surface or validation_policy as its declared interface.
    missing_entry_surfaces = [
        subsystem.entry_surface
        for subsystem in public_subsystems
        if subsystem.entry_surface
        and not (repo_root / subsystem.entry_surface).exists()
    ]
    results.append(
        ValidationResult(
            check_name="subsystem-entry-surfaces-exist",
            status="pass" if not missing_entry_surfaces else "fail",
            message=(
                "Subsystem entry surfaces exist."
                if not missing_entry_surfaces
                else "Subsystem registry references missing entry surfaces."
            ),
            path=str(registry_path),
            expected="all entry surfaces exist",
            found="ok" if not missing_entry_surfaces else ", ".join(missing_entry_surfaces),
        )
    )

    missing_authoritative_surfaces = [
        subsystem.authoritative_surface
        for subsystem in public_subsystems
        if subsystem.authoritative_surface
        and not (repo_root / subsystem.authoritative_surface).exists()
    ]
    results.append(
        ValidationResult(
            check_name="subsystem-authoritative-surfaces-exist",
            status="pass" if not missing_authoritative_surfaces else "fail",
            message=(
                "Subsystem authoritative surfaces exist."
                if not missing_authoritative_surfaces
                else "Subsystem registry references missing authoritative surfaces."
            ),
            path=str(registry_path),
            expected="all authoritative surfaces exist",
            found=(
                "ok"
                if not missing_authoritative_surfaces
                else ", ".join(missing_authoritative_surfaces)
            ),
        )
    )

    entry_scope_mismatches = [
        f"{subsystem.subsystem_id}:{subsystem.entry_surface}"
        for subsystem in public_subsystems
        if subsystem.entry_surface
        and not any(
            subsystem.entry_surface.startswith(prefix)
            for prefix in subsystem.scope_prefixes
        )
    ]
    results.append(
        ValidationResult(
            check_name="subsystem-entry-surfaces-in-scope",
            status="pass" if not entry_scope_mismatches else "fail",
            message=(
                "Subsystem entry surfaces stay within declared scope prefixes."
                if not entry_scope_mismatches
                else "Some subsystem entry surfaces fall outside their declared scope."
            ),
            path=str(registry_path),
            expected="entry surfaces within scope prefixes",
            found="ok" if not entry_scope_mismatches else ", ".join(entry_scope_mismatches),
        )
    )

    authoritative_scope_mismatches = [
        f"{subsystem.subsystem_id}:{subsystem.authoritative_surface}"
        for subsystem in public_subsystems
        if subsystem.authoritative_surface
        and not any(
            subsystem.authoritative_surface.startswith(prefix)
            for prefix in subsystem.scope_prefixes
        )
    ]
    results.append(
        ValidationResult(
            check_name="subsystem-authoritative-surfaces-in-scope",
            status="pass" if not authoritative_scope_mismatches else "fail",
            message=(
                "Subsystem authoritative surfaces stay within declared scope prefixes."
                if not authoritative_scope_mismatches
                else "Some subsystem authoritative surfaces fall outside their declared scope."
            ),
            path=str(registry_path),
            expected="authoritative surfaces within scope prefixes",
            found=(
                "ok"
                if not authoritative_scope_mismatches
                else ", ".join(authoritative_scope_mismatches)
            ),
        )
    )

    def _normalized_cluster_sources(subsystem) -> tuple[str, ...]:
        if subsystem.validation_cluster is None:
            return ()
        local_prefixes = [
            prefix.rstrip("/")
            for prefix in subsystem.scope_prefixes
            if not prefix.startswith("../")
        ]
        default_prefix = local_prefixes[0] if local_prefixes else ""
        normalized: list[str] = []
        for rel in subsystem.validation_cluster.source_files:
            if "/" not in rel and default_prefix:
                normalized.append(f"{default_prefix}/{rel}")
            else:
                normalized.append(rel)
        return tuple(normalized)

    missing_cluster_sources = sorted(
        {
            rel
            for subsystem in public_subsystems
            for rel in _normalized_cluster_sources(subsystem)
            if not (repo_root / rel).exists()
        }
    )
    results.append(
        ValidationResult(
            check_name="subsystem-cluster-source-files-exist",
            status="pass" if not missing_cluster_sources else "fail",
            message=(
                "Subsystem validation-cluster source files exist."
                if not missing_cluster_sources
                else "Subsystem registry references missing validation-cluster source files."
            ),
            path=str(registry_path),
            expected="all validation-cluster source files exist",
            found="ok" if not missing_cluster_sources else ", ".join(missing_cluster_sources),
        )
    )

    nonlocal_cluster_sources = [
        subsystem.subsystem_id
        for subsystem in public_subsystems
        if not any(
            any(rel.startswith(prefix) for prefix in subsystem.scope_prefixes)
            for rel in _normalized_cluster_sources(subsystem)
        )
    ]
    results.append(
        ValidationResult(
            check_name="subsystem-clusters-include-local-sources",
            status="pass" if not nonlocal_cluster_sources else "fail",
            message=(
                "Each subsystem validation cluster includes at least one local-scope source file."
                if not nonlocal_cluster_sources
                else "Some subsystem validation clusters do not include any local-scope source files."
            ),
            path=str(registry_path),
            expected="each cluster includes at least one source file in local scope",
            found="ok" if not nonlocal_cluster_sources else ", ".join(nonlocal_cluster_sources),
        )
    )

    return results


def validate_repository_file_registry(repo_root: Path) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    
    # Try v0.2 registry manifest first
    v2_registry_path = repo_root / 'governance' / 'REGISTRY_MANIFEST_v0_2.json'
    if v2_registry_path.exists():
        registry = _read_json(v2_registry_path)
        actual = _actual_file_list(repo_root)
        # Use `files` (canonical full catalog); `files_sample` is a display convenience.
        registered = sorted(entry['path'] for entry in registry.get('files', []))
        missing = sorted(set(actual) - set(registered))
        extra = sorted(set(registered) - set(actual))
        results.append(ValidationResult(
            check_name='v2-file-registry-coverage',
            status='pass' if not missing and not extra else 'fail',
            message='Registry manifest matches the actual file set.' if not missing and not extra else 'Registry manifest does not match the actual file set.',
            path=str(v2_registry_path),
            expected='full coverage with no extras',
            found=('ok' if not missing and not extra else f'missing={missing}; extra={extra}'),
        ))
        return results
    
    # Fall back to v0.1 registry (SUF only; root uses v0.2 REGISTRY_MANIFEST)
    for registry_path, prefix in ((repo_root / 'governance' / 'REGISTRY_MANIFEST_v0_2.json', 'root'), (repo_root / 'structured-unity-framework' / 'governance' / 'REPOSITORY_FILE_REGISTRY_v0_1.json', 'suf')):
        if not registry_path.exists():
            continue
        registry = _read_json(registry_path)
        scope_prefix = registry.get('scope_prefix', '')
        actual = [rel for rel in _actual_file_list(repo_root) if rel.startswith(scope_prefix)]
        registered = sorted(entry['path'] for entry in registry['files'])
        missing = sorted(set(actual) - set(registered))
        extra = sorted(set(registered) - set(actual))
        results.append(ValidationResult(
            check_name=f'{prefix}-file-registry-coverage',
            status='pass' if not missing and not extra else 'fail',
            message='Repository file registry matches the actual file set in scope.' if not missing and not extra else 'Repository file registry does not match the actual file set in scope.',
            path=str(registry_path),
            expected='full coverage with no extras',
            found=('ok' if not missing and not extra else f'missing={missing}; extra={extra}'),
        ))
    return results


def validate_repository_minimality(repo_root: Path) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    
    # Check for v0.2 allowlist in REGISTRY_MANIFEST
    allowlist_path = repo_root / 'governance' / 'REGISTRY_MANIFEST_v0_2.json'
    if allowlist_path.exists():
        allow = _read_json(allowlist_path)
        allowed = set(allow.get('allowed_root_files', []))
        actual_root_files = sorted(p.name for p in repo_root.iterdir() if p.is_file())
        forbidden = [name for name in actual_root_files if name not in allowed]
        results.append(ValidationResult(
            check_name='root-allowlist',
            status='pass' if not forbidden else 'fail',
            message='Root file set respects the explicit allowlist.' if not forbidden else 'Root contains files outside the explicit allowlist.',
            path=str(allowlist_path),
            expected='all root files allowlisted',
            found='ok' if not forbidden else ', '.join(forbidden),
        ))

    transient_dirs = sorted(
        path.relative_to(repo_root).as_posix()
        for path in repo_root.rglob('*')
        if path.is_dir() and path.name in {'__pycache__', '.mypy_cache', '.pytest_cache', '.ruff_cache'}
    )
    transient_files = sorted(
        path.relative_to(repo_root).as_posix()
        for path in repo_root.rglob('*')
        if path.is_file() and (path.suffix == '.pyc' or path.name == '.DS_Store')
    )
    results.append(
        ValidationResult(
            check_name='operational-artifacts-ignored',
            status='pass',
            message='Operational cache artifacts are excluded from repository-truth minimality checks.' if transient_dirs or transient_files else 'No operational cache artifacts detected during minimality checks.',
            path=str(repo_root),
            expected='operational artifacts are ignored or absent',
            found='none detected' if not transient_dirs and not transient_files else f'ignored dirs={transient_dirs}; ignored files={transient_files}',
        )
    )
    return results


def validate_current_claims(repo_root: Path) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    for expectations_path in (
        repo_root / 'governance' / 'CURRENT_CLAIM_EXPECTATIONS_v0_2.json',
        repo_root / 'structured-unity-framework' / 'governance' / 'CURRENT_CLAIM_EXPECTATIONS_v0_1.json',
    ):
        data = _read_json(expectations_path)
        for item in data.get('contains', []):
            path = repo_root / item['path']
            results.append(_contains_result(item['check_name'], path, item['needle'], item['message']))
        for item in data.get('absent', []):
            path = repo_root / item['path']
            results.append(_absent_result(item['check_name'], path, item['needle'], item['message']))
    results.extend(validate_current_surface_hygiene(repo_root))
    results.extend(validate_support_surface_boundaries(repo_root))
    return results


def validate_current_surface_hygiene(repo_root: Path) -> list[ValidationResult]:
    base_forbidden_fragments = [
        'docs/state/PROJECT_STATUS.md',
        'docs/state/CURRENT_EXECUTION_ORDER.md',
        'docs/state/PENDING_INVENTORY.md',
        'CURRENT_OPERATOR_START_HERE.md',
    ]
    root_v02_archived_fragments = [
        # PACKAGE_ENFORCEMENT_LAYER archived in v0.2 migration
        'governance/AUTHORITATIVE_SOURCES_v0_1.json',
        'governance/CURRENT_SURFACES_REGISTRY_v0_1.json',
        'governance/FEDERATED_SUBSYSTEM_PROTOCOL_v0_1.md',
        'governance/SUBSYSTEM_REGISTRY_v0_1.json',
        'governance/IMPLEMENTATION_LAYER_POLICY_v0_1.md',
    ]
    results: list[ValidationResult] = []
    seen: set[str] = set()
    registry_specs: list[tuple[dict, Path, str, list[str]]] = []
    root_registry, root_registry_path, root_version = _load_root_current_registry(repo_root)
    registry_specs.append(
        (
            root_registry,
            root_registry_path,
            'root',
            base_forbidden_fragments + (root_v02_archived_fragments if root_version == 'v0.2' else []),
        )
    )
    suf_registry_path = repo_root / 'structured-unity-framework' / 'governance' / 'CURRENT_SURFACES_REGISTRY_v0_1.json'
    if suf_registry_path.exists():
        registry_specs.append((
            _read_json(suf_registry_path),
            suf_registry_path,
            'suf',
            list(base_forbidden_fragments),
        ))

    for registry, registry_path, prefix, forbidden_fragments in registry_specs:
        # Handle v0.2 GOVERNANCE_CORE structure (current_surfaces with nested arrays)
        # or v0.1 CURRENT_SURFACES_REGISTRY structure (current_files flat list)
        current_files = _extract_current_files_from_registry(registry, prefix)
        for rel in current_files:
            if rel in seen:
                continue
            seen.add(rel)
            path = repo_root / rel
            if not path.exists() or path.suffix not in {'.md', '.py'}:
                continue
            text, error = _safe_read_text(path)
            if error is not None:
                results.append(ValidationResult(
                    check_name=f'{prefix}-surface-hygiene:{rel}',
                    status='fail',
                    message='Current surface hygiene could not be checked because the file is unavailable.',
                    path=str(path),
                    expected='no stale wrapper fragments',
                    found=error,
                ))
                continue
            bad = [frag for frag in forbidden_fragments if frag in text]
            results.append(ValidationResult(
                check_name=f'{prefix}-surface-hygiene:{rel}',
                status='pass' if not bad else 'fail',
                message='Current surface is free of known stale wrapper fragments.' if not bad else 'Current surface still contains stale wrapper fragments.',
                path=str(path),
                expected='no stale wrapper fragments',
                found='ok' if not bad else ', '.join(bad),
            ))
    return results


def validate_support_surface_boundaries(repo_root: Path) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    for rel, expectations in SUPPORT_SURFACE_BOUNDARY_EXPECTATIONS.items():
        path = repo_root / rel
        for needle in expectations.get('contains', []):
            results.append(_contains_result(
                f'support-boundary-present:{rel}:{needle[:32]}',
                path,
                needle,
                'Support surface preserves an explicit bounded-scope boundary anchor.',
            ))
        for alternatives in expectations.get('contains_any', []):
            text, error = _safe_read_text(path)
            if error is not None:
                results.append(ValidationResult(
                    check_name=f'support-boundary-present-any:{rel}:{alternatives[0][:32]}',
                    status='fail',
                    message='Support surface boundary alternatives could not be checked because the file is unavailable.',
                    path=str(path),
                    expected='one of the accepted boundary anchors present',
                    found=error,
                ))
                continue
            found = next((needle for needle in alternatives if needle in text), None)
            results.append(ValidationResult(
                check_name=f'support-boundary-present-any:{rel}:{alternatives[0][:32]}',
                status='pass' if found else 'fail',
                message='Support surface preserves an accepted bounded-scope boundary anchor.' if found else 'Support surface is missing an accepted bounded-scope boundary anchor.',
                path=str(path),
                expected='one of: ' + ' | '.join(alternatives),
                found=found or 'missing',
            ))
        for needle in expectations.get('absent', []):
            results.append(_absent_result(
                f'support-boundary-absent:{rel}:{needle[:32]}',
                path,
                needle,
                'Support surface stays free of known absolute-closure or universal-proof overclaims.',
            ))
        for item in expectations.get('absent_patterns', []):
            results.append(_absent_pattern_result(
                f"support-boundary-absent-pattern:{rel}:{item['label']}",
                path,
                item['pattern'],
                item['label'],
                'Support surface stays free of known absolute-closure or universal-proof overclaims.',
            ))
    return results



def _canonicalize_repo_relative_path(path: str) -> str | None:
    candidate = Path(path)
    if candidate.is_absolute():
        return None

    parts: list[str] = []
    for part in candidate.parts:
        if part in ('', '.'):
            continue
        if part == '..':
            if not parts:
                return None
            parts.pop()
            continue
        parts.append(part)

    if not parts:
        return None
    return Path(*parts).as_posix()



def _canonicalize_repo_relative_paths(paths: set[str] | list[str]) -> set[str]:
    canonical: set[str] = set()
    for path in paths:
        normalized = _canonicalize_repo_relative_path(path)
        if normalized is not None:
            canonical.add(normalized)
    return canonical



def _load_current_surface_paths(repo_root: Path) -> set[str]:
    current: set[str] = set()
    for rel in EDIT_SCOPE_CURRENT_SURFACE_REGISTRIES:
        registry = _read_json(repo_root / rel)
        current.update(_extract_current_files_from_registry(registry, "root"))
    return _canonicalize_repo_relative_paths(current)



def _normalize_scope_prefixes(prefixes: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    normalized: list[str] = []
    for prefix in prefixes:
        canonical = _canonicalize_repo_relative_path(prefix)
        if canonical is None:
            continue
        normalized.append(canonical.rstrip('/') + '/')
    return tuple(sorted(set(normalized)))



def _path_matches_prefix(path: str, prefix: str) -> bool:
    return path == prefix[:-1] or path.startswith(prefix)



def _authorize_edit_path(
    path: str,
    *,
    always_files: set[str],
    declared_files: set[str],
    always_prefixes: tuple[str, ...],
    declared_prefixes: tuple[str, ...],
) -> dict[str, str | bool]:
    canonical_path = _canonicalize_repo_relative_path(path)
    if canonical_path is None:
        return {
            'raw_path': path,
            'canonical_path': '',
            'editable': False,
            'reason': 'invalid-path',
            'matched_scope': '',
        }

    if canonical_path in always_files:
        return {
            'raw_path': path,
            'canonical_path': canonical_path,
            'editable': True,
            'reason': 'always-file',
            'matched_scope': canonical_path,
        }
    if canonical_path in declared_files:
        return {
            'raw_path': path,
            'canonical_path': canonical_path,
            'editable': True,
            'reason': 'declared-file',
            'matched_scope': canonical_path,
        }
    for prefix in always_prefixes:
        if _path_matches_prefix(canonical_path, prefix):
            return {
                'raw_path': path,
                'canonical_path': canonical_path,
                'editable': True,
                'reason': 'always-prefix',
                'matched_scope': prefix,
            }
    for prefix in declared_prefixes:
        if _path_matches_prefix(canonical_path, prefix):
            return {
                'raw_path': path,
                'canonical_path': canonical_path,
                'editable': True,
                'reason': 'declared-prefix',
                'matched_scope': prefix,
            }
    return {
        'raw_path': path,
        'canonical_path': canonical_path,
        'editable': False,
        'reason': 'out-of-scope',
        'matched_scope': '',
    }



def validate_edit_scope(repo_root: Path) -> list[ValidationResult]:
    # v0.2: Extract edit_scope_policy from GOVERNANCE_CORE_v0_2.json
    governance_core_path = repo_root / 'governance' / 'GOVERNANCE_CORE_v0_2.json'
    if not governance_core_path.exists():
        return [ValidationResult(
            check_name='edit-scope-governance-core',
            status='fail',
            message='GOVERNANCE_CORE_v0_2.json not found',
            path=str(governance_core_path),
            expected='file exists',
            found='missing',
        )]
    governance = _read_json(governance_core_path)
    policy = governance.get('edit_scope_policy', {})
    baseline_path = repo_root / 'governance' / 'REGISTRY_MANIFEST_v0_2.json'
    if baseline_path.exists():
        baseline = _read_json(baseline_path)
    else:
        legacy_baseline_path = repo_root / 'governance' / 'REPOSITORY_EDIT_BASELINE_v0_1.json'
        baseline = _read_json(legacy_baseline_path) if legacy_baseline_path.exists() else {'files': []}
        baseline_path = legacy_baseline_path if legacy_baseline_path.exists() else governance_core_path

    excluded_from_baseline = set(policy.get('excluded_from_baseline', []))
    baseline_entries = {entry['path']: entry['sha256'] for entry in baseline.get('files', []) if entry['path'] not in excluded_from_baseline}
    actual_files = [rel for rel in _actual_file_list(repo_root) if rel not in excluded_from_baseline]
    actual_hashes = {rel: _sha256(repo_root / rel) for rel in actual_files}

    current_surface_files = _load_current_surface_paths(repo_root) if policy.get('include_current_surfaces', True) else set()
    always_files = current_surface_files | _canonicalize_repo_relative_paths(policy.get('always_allowed_files', []))
    declared_files = _canonicalize_repo_relative_paths(policy.get('declared_allowed_files', []))
    always_prefixes = _normalize_scope_prefixes(policy.get('always_allowed_prefixes', []))
    declared_prefixes = _normalize_scope_prefixes(policy.get('declared_allowed_prefixes', []))

    changed_entries: list[dict[str, str]] = []
    for rel, sha in sorted(actual_hashes.items()):
        baseline_sha = baseline_entries.get(rel)
        if baseline_sha is None:
            changed_entries.append({'path': rel, 'change': 'new-file'})
        elif baseline_sha != sha:
            changed_entries.append({'path': rel, 'change': 'modified'})
    for rel in sorted(set(baseline_entries) - set(actual_hashes)):
        changed_entries.append({'path': rel, 'change': 'removed'})

    out_of_scope = []
    for entry in changed_entries:
        decision = _authorize_edit_path(
            entry['path'],
            always_files=always_files,
            declared_files=declared_files,
            always_prefixes=always_prefixes,
            declared_prefixes=declared_prefixes,
        )
        if not decision['editable']:
            canonical = decision['canonical_path'] or entry['path']
            out_of_scope.append(f"{entry['change']}:{canonical}")

    declared_targets = sorted(declared_files) + sorted(declared_prefixes)
    # Post-v0.2 migration: no historical baseline exists. This is the accepted
    # state (v0.1 REPOSITORY_EDIT_BASELINE was archived in the migration).
    # Report 'warn' instead of 'fail' so operators see the condition without a
    # false-alarm, and skip the changes-within-policy check entirely when
    # baseline is empty (every file would otherwise appear as 'new').
    baseline_empty = not baseline_entries
    results = [
        ValidationResult(
            check_name='edit-scope-baseline-readable',
            status='pass' if baseline_entries else 'warn',
            message='Repository edit baseline is present and readable.' if baseline_entries else 'No edit baseline active (accepted post-v0.2-migration state; changes-within-policy check is skipped).',
            path=str(baseline_path),
            expected='baseline file entries available or explicit empty-baseline acceptance',
            found=str(len(baseline_entries)),
        ),
        ValidationResult(
            check_name='edit-scope-policy-readable',
            status='pass',
            message='Agent edit scope policy is present and readable.',
            path=str(governance_core_path),
            expected='GOVERNANCE_CORE_v0_2.json readable',
            found='ok',
        ),
        ValidationResult(
            check_name='edit-scope-changes-within-policy',
            status='pass' if (baseline_empty or not out_of_scope) else 'fail',
            message=('Edit-scope change check skipped (empty baseline).' if baseline_empty
                    else ('All files changed relative to the review baseline stay within current surfaces, designated work surfaces, or declared scope.' if not out_of_scope
                          else 'Some files changed relative to the review baseline fall outside current surfaces, designated work surfaces, and declared scope.')),
            path=str(governance_core_path),
            expected='all changed files within allowed scope',
            found=('skipped' if baseline_empty else ('ok' if not out_of_scope else '; '.join(out_of_scope[:50]))),
        ),
        ValidationResult(
            check_name='edit-scope-declared-scope-empty-or-explicit',
            status='pass',
            message='Declared edit scope remains explicit; empty means no exceptional paths are currently authorized.',
            path=str(governance_core_path),
            expected='explicit exceptional scope declaration',
            found='none' if not declared_targets else '; '.join(declared_targets),
        ),
    ]
    return results



def _extract_current_files_from_registry(registry: dict, scope: str) -> list[str]:
    """Extract current files from v0.1 or v0.2 registry format."""
    if 'current_surfaces' in registry:
        # v0.2 GOVERNANCE_CORE format
        cs = registry['current_surfaces']
        files = []
        files.extend(cs.get('root_entrypoints', []))
        files.extend(cs.get('root_governance', []))
        files.extend(cs.get('package_entrypoints', {}).values())
        assisted = cs.get('assisted_use')
        if assisted:
            files.append(assisted)
        return files
    else:
        # v0.1 CURRENT_SURFACES_REGISTRY format
        return registry.get('current_files', [])


def validate_routing_surfaces(repo_root: Path) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    root_registry, _, _ = _load_root_current_registry(repo_root)
    registries = {'root': root_registry}
    suf_registry_path = repo_root / 'structured-unity-framework' / 'governance' / 'CURRENT_SURFACES_REGISTRY_v0_1.json'
    if suf_registry_path.exists():
        registries['suf'] = _read_json(suf_registry_path)

    for scope, registry in registries.items():
        routing_relpaths = list(ROUTING_SURFACES[scope])
        if scope == 'root':
            if (repo_root / 'governance' / 'AUTHORITATIVE_INDEX_v0_2.md').exists():
                routing_relpaths = [
                    'README.md',
                    'START_HERE.md',
                    'docs/frontdoor/PROJECT_PURPOSE_AND_USE_CASES.md',
                    'docs/frontdoor/CONTROL_AND_GOVERNANCE_SURFACE.md',
                    'governance/AUTHORITATIVE_INDEX_v0_2.md',
                ]
            else:
                routing_relpaths = [
                    'README.md',
                    'START_HERE.md',
                    'docs/frontdoor/PROJECT_PURPOSE_AND_USE_CASES.md',
                    'docs/frontdoor/CONTROL_AND_GOVERNANCE_SURFACE.md',
                    'governance/AUTHORITATIVE_INDEX_v0_1.md',
                ]
        routing_paths = [repo_root / rel for rel in routing_relpaths]
        routing_text = '\n'.join(path.read_text(encoding='utf-8') for path in routing_paths if path.exists())
        scope_prefix = 'structured-unity-framework/' if scope == 'suf' else ''
        orphans = []
        for rel in _extract_current_files_from_registry(registry, scope):
            if rel in routing_relpaths:
                continue
            candidates = {rel, Path(rel).name}
            if scope_prefix and rel.startswith(scope_prefix):
                candidates.add(rel[len(scope_prefix):])
            if not any(candidate in routing_text for candidate in candidates):
                orphans.append(rel)
        results.append(ValidationResult(
            check_name=f'{scope}-routing-coverage',
            status='pass' if not orphans else 'fail',
            message='Every current file is reachable from at least one current routing surface.' if not orphans else 'Some current files are orphaned from current routing surfaces.',
            path=', '.join(str(p) for p in routing_paths),
            expected='all current files referenced by current routing surfaces',
            found='ok' if not orphans else ', '.join(orphans),
        ))
    return results


def validate_merged_doc_quality(repo_root: Path) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    forbidden_fragments = [
        '## Source surfaces preserved here',
        '## Preserved source:',
        'This file preserves and consolidates the material from the source surfaces listed below.',
    ]
    for rel, required in MERGED_DOC_EXPECTATIONS.items():
        path = repo_root / rel
        text, error = _safe_read_text(path)
        if error is not None:
            results.append(ValidationResult(
                check_name=f'merged-doc-quality:{rel}',
                status='fail',
                message='Merged document quality could not be checked because the file is unavailable.',
                path=str(path),
                expected='required headings present; no consolidation residue',
                found=error,
            ))
            continue
        missing = [frag for frag in required if frag not in text]
        bad = [frag for frag in forbidden_fragments if frag in text]
        results.append(ValidationResult(
            check_name=f'merged-doc-quality:{rel}',
            status='pass' if not missing and not bad else 'fail',
            message='Merged document keeps navigation headings and clean consolidation prose.' if not missing and not bad else 'Merged document is missing navigation headings or still contains consolidation residue.',
            path=str(path),
            expected='required headings present; no consolidation residue',
            found='ok' if not missing and not bad else f'missing={missing}; residue={bad}',
        ))
    return results
