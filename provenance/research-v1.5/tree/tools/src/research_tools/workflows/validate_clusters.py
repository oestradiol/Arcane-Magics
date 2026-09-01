from __future__ import annotations

from collections.abc import Callable

from research_tools.models.clusters import ValidationClusterRun, ValidationClusterSpec
from research_tools.models.reports import ValidationResult
from research_tools.parse.governance_core import (
    GovernanceCore,
    SubsystemSpec as V2SubsystemSpec,
    derive_subsystem_validation_cluster,
    parse_governance_core,
)
from research_tools.parse.source_registry import parse_source_registry, source_registry_index
from research_tools.paths import RepoPaths, format_optional_report_path, format_report_path
from research_tools.validate.archives import validate_archive_links
from research_tools.validate.governance import (
    validate_current_claims,
    validate_current_surfaces,
    validate_edit_scope,
    validate_merged_doc_quality,
    validate_repository_file_registry,
    validate_repository_minimality,
    validate_routing_surfaces,
)
from research_tools.validate.governance_consistency import validate_governance_consistency
from research_tools.validate.knowledge import validate_knowledge_package
from research_tools.validate.links import validate_markdown_links
from research_tools.validate.release_hygiene import validate_release_hygiene
from research_tools.validate.route_consistency import validate_nz_route, validate_taiwan_route
from research_tools.validate.sources import validate_source_registry
from research_tools.validate.status_surfaces import validate_status_surfaces
from research_tools.validate.versions import validate_versions


def _summarize_results(results: list[ValidationResult]) -> tuple[int, int, int, str]:
    passed = sum(1 for result in results if result.status == "pass")
    failed = sum(1 for result in results if result.status == "fail")
    warned = sum(1 for result in results if result.status == "warn")
    status = "fail" if failed else "warn" if warned else "pass"
    return passed, failed, warned, status


def _run_root_governance_cluster(paths: RepoPaths) -> list[ValidationResult]:
    repo_root = paths.research_root
    results: list[ValidationResult] = []
    results.extend(validate_current_surfaces(repo_root))
    results.extend(validate_repository_file_registry(repo_root))
    results.extend(validate_current_claims(repo_root))
    results.extend(validate_repository_minimality(repo_root))
    results.extend(validate_routing_surfaces(repo_root))
    results.extend(validate_merged_doc_quality(repo_root))
    results.extend(validate_governance_consistency(repo_root))
    results.extend(validate_edit_scope(repo_root))
    return results


def _run_suf_active_core_cluster(paths: RepoPaths) -> list[ValidationResult]:
    entries = parse_source_registry(paths.source_registry)
    source_index = source_registry_index(entries)
    results: list[ValidationResult] = []
    results.extend(validate_nz_route(paths.nz_route_root, source_index))
    results.extend(validate_taiwan_route(paths.taiwan_route_root, source_index))
    results.extend(validate_status_surfaces(paths))
    return results


def _run_knowledge_cluster(paths: RepoPaths) -> list[ValidationResult]:
    return validate_knowledge_package(paths.knowledge_root)


def _run_tooling_release_cluster(paths: RepoPaths) -> list[ValidationResult]:
    entries = parse_source_registry(paths.source_registry)
    results: list[ValidationResult] = []
    results.extend(validate_markdown_links(paths.research_root))
    results.extend(validate_source_registry(entries))
    results.extend(validate_archive_links(entries))
    results.extend(validate_versions(paths))
    results.extend(validate_release_hygiene(paths.research_root))
    return results


CLUSTER_RUNNERS: dict[str, Callable[[RepoPaths], list[ValidationResult]]] = {
    # v0.2 cluster IDs (derived from subsystem_id)
    "root_governance_cluster": _run_root_governance_cluster,
    "structured_unity_framework_cluster": _run_suf_active_core_cluster,
    "knowledge_cluster": _run_knowledge_cluster,
    "tools_cluster": _run_tooling_release_cluster,
}


def _build_cluster_run(
    spec: ValidationClusterSpec,
    paths: RepoPaths,
    results: list[ValidationResult],
) -> ValidationClusterRun:
    passed, failed, warned, status = _summarize_results(results)
    return ValidationClusterRun(
        spec=spec,
        source_files=tuple(paths.research_root / rel for rel in spec.source_files),
        results=tuple(results),
        passed=passed,
        failed=failed,
        warned=warned,
        status=status,
    )


def _cluster_spec_from_v2(subsystem: V2SubsystemSpec, research_root: Path) -> ValidationClusterSpec | None:
    """Build cluster spec from v0.2 governance core subsystem."""
    source_files = derive_subsystem_validation_cluster(subsystem, research_root)
    if source_files is None:
        return None
    
    cluster_id = subsystem.subsystem_id.replace("-", "_") + "_cluster"
    entry_surface = subsystem.entry if subsystem.entry else (subsystem.surfaces[0] if subsystem.surfaces else "")
    
    return ValidationClusterSpec(
        cluster_id=cluster_id,
        owner=subsystem.owner,
        purpose=subsystem.purpose,
        entry_surface=entry_surface,
        source_files=tuple(source_files),
    )


def _collect_v2_clusters(paths: RepoPaths, governance: GovernanceCore) -> list[ValidationClusterRun]:
    """Collect validation clusters from v0.2 governance core."""
    clusters: list[ValidationClusterRun] = []
    
    for subsystem_id, subsystem in governance.subsystems.items():
        if subsystem.visibility == "private":
            continue  # Skip private subsystems in public validation
        
        spec = _cluster_spec_from_v2(subsystem, paths.research_root)
        if spec is None:
            continue
        
        # Build protocol validation results
        results: list[ValidationResult] = []
        
        # Check entry surface exists
        if subsystem.entry:
            entry_path = paths.research_root / subsystem.entry
            results.append(
                ValidationResult(
                    check_name="cluster-entry-surface-exists",
                    status="pass" if entry_path.exists() else "fail",
                    message="Cluster entry surface exists." if entry_path.exists() else "Cluster entry surface is missing.",
                    path=str(paths.governance_core),
                    expected=subsystem.entry,
                    found=subsystem.entry if entry_path.exists() else "missing",
                )
            )
        
        # Check state surface exists
        if subsystem.state_surface:
            state_path = paths.research_root / subsystem.state_surface
            results.append(
                ValidationResult(
                    check_name="cluster-state-surface-exists",
                    status="pass" if state_path.exists() else "fail",
                    message="Cluster state surface exists." if state_path.exists() else "Cluster state surface is missing.",
                    path=str(paths.governance_core),
                    expected=subsystem.state_surface,
                    found=subsystem.state_surface if state_path.exists() else "missing",
                )
            )
        
        # Run cluster-specific validation
        runner = CLUSTER_RUNNERS.get(spec.cluster_id)
        if runner is None:
            # Try alternate cluster_id formats
            alt_id = subsystem_id.replace("-", "_")
            runner = CLUSTER_RUNNERS.get(alt_id)
        
        if runner is None:
            results.append(
                ValidationResult(
                    check_name="cluster-runner-registered",
                    status="warn",  # Warn, don't fail - v0.2 may define new clusters
                    message=f"Validation cluster `{spec.cluster_id}` has no registered runner yet (v0.2 migration in progress).",
                    path=str(paths.governance_core),
                    expected=spec.cluster_id,
                    found="not yet mapped",
                )
            )
        else:
            results.extend(runner(paths))
        
        clusters.append(_build_cluster_run(spec, paths, results))
    
    return clusters


def collect_validation_clusters(paths: RepoPaths) -> list[ValidationClusterRun]:
    """Collect validation clusters from v0.2 governance core."""
    if not paths.governance_core.exists():
        return [
            ValidationClusterRun(
                spec=ValidationClusterSpec(
                    cluster_id="governance-core-missing",
                    owner="Research root",
                    purpose="GOVERNANCE_CORE_v0_2.json is required for cluster validation",
                    entry_surface="governance/GOVERNANCE_CORE_v0_2.json",
                    source_files=(),
                ),
                source_files=(),
                results=[
                    ValidationResult(
                        check_name="governance-core-exists",
                        status="fail",
                        message="GOVERNANCE_CORE_v0_2.json not found. Run governance compression migration.",
                        path=str(paths.governance_core),
                        expected="governance/GOVERNANCE_CORE_v0_2.json",
                        found="missing",
                    )
                ],
                passed=0,
                failed=1,
                warned=0,
                status="fail",
            )
        ]
    
    governance = parse_governance_core(paths.governance_core)
    return _collect_v2_clusters(paths, governance)


def render_cluster_report(generated_at: str, clusters: list[ValidationClusterRun]) -> str:
    cluster_summaries = "\n".join(
        f"- `{cluster.spec.cluster_id}` [{cluster.status}] owner `{cluster.spec.owner}` entry `{cluster.spec.entry_surface}` passed `{cluster.passed}` failed `{cluster.failed}` warned `{cluster.warned}`"
        for cluster in clusters
    )
    cluster_sections = []
    for cluster in clusters:
        files = "\n".join(f"- `{format_report_path(path)}`" for path in cluster.source_files)
        results = "\n".join(
            f"- `{result.check_name}` [{result.status}] {result.message}"
            + (f" Expected `{result.expected}`." if result.expected else "")
            + (f" Found `{result.found}`." if result.found else "")
            + (f" Path `{format_optional_report_path(result.path)}`." if result.path else "")
            for result in cluster.results
        )
        cluster_sections.append(
            f"""## {cluster.spec.cluster_id}

- owner: `{cluster.spec.owner}`
- purpose: {cluster.spec.purpose}
- entry surface: `{cluster.spec.entry_surface}`
- status: `{cluster.status}`
- passed: `{cluster.passed}`
- failed: `{cluster.failed}`
- warned: `{cluster.warned}`

### Source files

{files}

### Results

{results}
"""
        )
    body = "\n".join(cluster_sections)
    return f"""# Federated Validation Clusters

Generated: `{generated_at}`

## Summary

{cluster_summaries}

{body}

## Human validation required

This output is read-only and provisional until a human reviews it.
"""
