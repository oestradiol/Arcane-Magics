from research_tools.parse.nz_ledger import parse_nz_ledger
from research_tools.parse.taiwan_ledger import parse_taiwan_ledger
from research_tools.paths import get_paths
from research_tools.reports.nz_summary import (
    compare_nz_summary_to_docs,
    compute_nz_lag_pairs,
    compute_nz_window_summaries,
    compute_route_summary,
    render_nz_lag_report,
    render_nz_summary_report,
    render_nz_window_report,
)
from research_tools.reports.nz_taiwan_summary import (
    compare_nz_taiwan_summary_to_docs,
    render_nz_taiwan_report,
)
from research_tools.reports.release_readiness import render_release_readiness_report
from research_tools.reports.taiwan_lag import compute_taiwan_lag_pair, render_taiwan_lag_report
from research_tools.reports.taiwan_summary import (
    compare_taiwan_summary_to_docs,
    render_taiwan_summary_report,
)
from research_tools.validate.knowledge import validate_knowledge_package
from research_tools.validate.versions import validate_versions
from research_tools.workflows.validate_all import collect_validation_results


def test_nz_summary_report_renders_current_metrics() -> None:
    paths = get_paths()
    events = parse_nz_ledger(paths.nz_route_root / "event-ledger-seed.md")
    summary = compute_route_summary("nz", events)
    windows = compute_nz_window_summaries(events)
    validations = compare_nz_summary_to_docs(
        summary=summary,
        window_summary=windows["Main perturbation interval"],
        comparator_b_summary=windows["Comparator B"],
        project_status_path=paths.suf_root / "docs" / "project-status.md",
        i_summary_path=paths.nz_route_root / "first-pass-i-summary.md",
        seed_readout_path=paths.nz_route_root / "first-pass-seed-readout.md",
        window_comparison_path=paths.nz_route_root / "first-pass-window-comparison.md",
        sensitivity_note_path=paths.nz_route_root / "first-pass-sensitivity-and-null-note.md",
    )

    output = render_nz_summary_report(
        summary=summary,
        window_summary=windows["Main perturbation interval"],
        validations=validations,
        source_files=[paths.nz_route_root / "event-ledger-seed.md"],
        generated_at="2026-04-02T00:00:00+00:00",
    )

    assert "`38`" in output
    assert "`29`" in output
    assert "- none" in output


def test_nz_window_comparison_report_renders_expected_rows() -> None:
    paths = get_paths()
    events = parse_nz_ledger(paths.nz_route_root / "event-ledger-seed.md")

    output = render_nz_window_report(
        compute_nz_window_summaries(events),
        "2026-04-02T00:00:00+00:00",
        [paths.nz_route_root / "event-ledger-seed.md"],
    )

    assert "Main perturbation interval" in output
    assert "`29`" in output


def test_nz_lag_report_renders_expected_pairs() -> None:
    paths = get_paths()
    events = parse_nz_ledger(paths.nz_route_root / "event-ledger-seed.md")

    output = render_nz_lag_report(
        compute_nz_lag_pairs(events),
        "2026-04-02T00:00:00+00:00",
        [paths.nz_route_root / "event-ledger-seed.md"],
    )

    assert "Level 2 preparation staging" in output
    assert "`1, 2, 2, 3, 8, 8`" in output


def test_nz_taiwan_summary_report_renders_expected_rows() -> None:
    paths = get_paths()
    nz_events = parse_nz_ledger(paths.nz_route_root / "event-ledger-seed.md")
    taiwan_events = parse_taiwan_ledger(paths.taiwan_route_root / "taiwan-event-ledger-seed.md")
    nz_summary = compute_route_summary("nz", nz_events)
    taiwan_summary = compute_route_summary("taiwan", taiwan_events)
    validations = compare_nz_taiwan_summary_to_docs(
        nz_summary=nz_summary,
        taiwan_summary=taiwan_summary,
        comparison_note_path=paths.taiwan_route_root / "first-nz-taiwan-comparison-note.md",
    )

    output = render_nz_taiwan_report(
        nz_summary=nz_summary,
        taiwan_summary=taiwan_summary,
        validations=validations,
        source_files=[paths.taiwan_route_root / "first-nz-taiwan-comparison-note.md"],
        generated_at="2026-04-02T00:00:00+00:00",
    )

    assert "`15`" in output
    assert "public-health policy and command / border-control coordination = 6 / 15 each" in output
    assert "public-information receiving share" in output
    assert "- none" in output


def test_taiwan_summary_report_renders_expected_rows() -> None:
    paths = get_paths()
    taiwan_events = parse_taiwan_ledger(paths.taiwan_route_root / "taiwan-event-ledger-seed.md")
    taiwan_summary = compute_route_summary("taiwan", taiwan_events)
    validations = compare_taiwan_summary_to_docs(
        summary=taiwan_summary,
        ledger_path=paths.taiwan_route_root / "taiwan-event-ledger-seed.md",
        evidence_map_path=paths.taiwan_route_root / "taiwan-chapter-evidence-map.md",
        table_plan_path=paths.taiwan_route_root / "taiwan-chapter-table-and-figure-plan.md",
    )

    output = render_taiwan_summary_report(
        summary=taiwan_summary,
        validations=validations,
        source_files=[
            paths.taiwan_route_root / "taiwan-event-ledger-seed.md",
            paths.taiwan_route_root / "taiwan-chapter-evidence-map.md",
            paths.taiwan_route_root / "taiwan-chapter-table-and-figure-plan.md",
        ],
        generated_at="2026-04-02T00:00:00+00:00",
    )

    assert "`15`" in output
    assert "`31 / 52 = 0.60`" in output
    assert "public-health policy and command = 6 / 15" in output
    assert "Matches current published Taiwan chapter-facing docs." in output
    assert "- none" in output


def test_taiwan_lag_report_renders_expected_pair() -> None:
    paths = get_paths()
    taiwan_events = parse_taiwan_ledger(paths.taiwan_route_root / "taiwan-event-ledger-seed.md")

    output = render_taiwan_lag_report(
        compute_taiwan_lag_pair(taiwan_events),
        "2026-04-02T00:00:00+00:00",
        [paths.taiwan_route_root / "taiwan-event-ledger-seed.md"],
    )

    assert "Bounded quarantine-routing lag pair" in output
    assert "`tw-p-002`" in output
    assert "`tw-p-010`" in output
    assert "`11`" in output
    assert "only one conservative clean Taiwan lag pair is currently publishable" in output


def test_knowledge_validation_passes_for_current_package() -> None:
    results = validate_knowledge_package(get_paths().knowledge_root)

    assert not [result for result in results if result.status == "fail"]


def test_version_validation_passes_for_current_package_surfaces() -> None:
    results = validate_versions(get_paths())

    assert not [result for result in results if result.status == "fail"]


def test_release_readiness_report_renders_without_blockers_for_current_repo() -> None:
    paths = get_paths()
    results = collect_validation_results(paths)
    output = render_release_readiness_report(
        generated_at="2026-04-02T00:00:00+00:00",
        results=results,
        source_files=[paths.research_root / "README.md", paths.suf_root / "README.md"],
    )

    assert "Zero unresolved release blockers." in output
    assert "- none" in output
