from __future__ import annotations

from research_tools.paths import get_paths
from research_tools.workflows.validate_clusters import collect_validation_clusters, render_cluster_report


def test_validation_clusters_pass_on_current_state() -> None:
    clusters = collect_validation_clusters(get_paths())

    assert clusters
    assert not [cluster for cluster in clusters if cluster.failed]


def test_validation_cluster_protocol_is_explicit() -> None:
    paths = get_paths()
    clusters = collect_validation_clusters(paths)

    ids = [cluster.spec.cluster_id for cluster in clusters]
    assert len(ids) == len(set(ids))
    assert all(cluster.spec.owner for cluster in clusters)
    assert all(cluster.spec.entry_surface for cluster in clusters)
    assert all(cluster.source_files for cluster in clusters)
    assert all((paths.research_root / cluster.spec.entry_surface).exists() for cluster in clusters)


def test_validation_clusters_follow_governance_core_order() -> None:
    """v0.2: Clusters derived from GOVERNANCE_CORE subsystems."""
    paths = get_paths()
    from research_tools.parse.governance_core import parse_governance_core
    governance = parse_governance_core(paths.governance_core)
    # v0.2 clusters are derived from public subsystems
    expected_cluster_ids = [
        sid.replace("-", "_") + "_cluster"
        for sid, subsys in governance.subsystems.items()
        if subsys.visibility == "public"
    ]
    cluster_ids = [cluster.spec.cluster_id for cluster in collect_validation_clusters(paths)]

    assert cluster_ids == expected_cluster_ids


def test_validation_cluster_report_renders_protocol_fields() -> None:
    clusters = collect_validation_clusters(get_paths())
    report = render_cluster_report("2026-04-17T00:00:00+00:00", clusters)

    assert "# Federated Validation Clusters" in report
    assert "root_governance_cluster" in report
    assert "knowledge_cluster" in report
    assert "entry surface" in report
