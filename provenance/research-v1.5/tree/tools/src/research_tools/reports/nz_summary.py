from __future__ import annotations

import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from statistics import fmean, median

from research_tools.config import NZ_EVENT_PREFIXES, POSSIBLE_DIRECTED_EDGES, UNIT_TO_CLUSTER
from research_tools.models.ledger import LedgerEvent
from research_tools.models.reports import RouteSummary, ValidationResult, WindowSummary
from research_tools.paths import format_report_path


def _format_ratio(numerator: int, denominator: int, digits: int) -> str:
    if denominator == 0:
        return "0"
    return f"{numerator / denominator:.{digits}f}"


def _cross_cluster_counts(events: list[LedgerEvent]) -> tuple[int, int, int]:
    unique_edges: set[tuple[str, str]] = set()
    weighted_cross = 0
    weighted_total = 0
    for event in events:
        issuer_cluster = UNIT_TO_CLUSTER[event.issuing_unit]
        for receiver in event.receiving_units:
            edge = (event.issuing_unit, receiver)
            unique_edges.add(edge)
            weighted_total += 1
            if issuer_cluster != UNIT_TO_CLUSTER[receiver]:
                weighted_cross += 1
    return len(unique_edges), weighted_cross, weighted_total


def compute_route_summary(route_name: str, events: list[LedgerEvent]) -> RouteSummary:
    event_count = len(events)
    active_units = {
        event.issuing_unit for event in events
    } | {receiver for event in events for receiver in event.receiving_units}
    active_edges, weighted_cross, weighted_total = _cross_cluster_counts(events)
    issuer_counts = Counter(event.issuing_unit for event in events)
    top_issuer, top_issuer_count = issuer_counts.most_common(1)[0]
    top_issuers = tuple(
        issuer for issuer, count in issuer_counts.items() if count == top_issuer_count
    )
    pi_receiving = sum(
        1 for event in events if "public-information coordination" in event.receiving_units
    )
    mean_breadth = fmean(len(event.receiving_units) for event in events)
    return RouteSummary(
        route_name=route_name,
        event_count=event_count,
        main_interval_count=sum(
            1 for event in events if event.event_id.startswith(NZ_EVENT_PREFIXES["main"])
        )
        if route_name == "nz"
        else None,
        active_units=len(active_units),
        active_edges=active_edges,
        occupied_edge_ratio=active_edges / POSSIBLE_DIRECTED_EDGES,
        weighted_cross_cluster_numerator=weighted_cross,
        weighted_cross_cluster_denominator=weighted_total,
        weighted_cross_cluster_share=weighted_cross / weighted_total,
        top_issuer=top_issuer,
        top_issuers=top_issuers,
        top_issuer_count=top_issuer_count,
        public_information_receiving_count=pi_receiving,
        mean_receiving_breadth=mean_breadth,
    )


def compute_nz_window_summaries(events: list[LedgerEvent]) -> dict[str, WindowSummary]:
    windows = {
        "Comparator A": [event for event in events if event.event_id.startswith("nz-a-")],
        "Main perturbation interval": [
            event for event in events if event.event_id.startswith("nz-p-")
        ],
        "Comparator B": [event for event in events if event.event_id.startswith("nz-b-")],
    }
    summaries: dict[str, WindowSummary] = {}
    for label, window_events in windows.items():
        active_units = {
            event.issuing_unit for event in window_events
        } | {receiver for event in window_events for receiver in event.receiving_units}
        sec_issuing_count = sum(
            1
            for event in window_events
            if event.issuing_unit == "strategic executive coordination"
        )
        _, weighted_cross, weighted_total = _cross_cluster_counts(window_events)
        summaries[label] = WindowSummary(
            label=label,
            event_count=len(window_events),
            sigma3_event_count=sum(1 for event in window_events if event.sigma3_tagged),
            public_information_marked_count=sum(
                1 for event in window_events if event.public_information_marked
            ),
            mean_receiving_breadth=fmean(len(event.receiving_units) for event in window_events),
            active_units=len(active_units),
            sec_issuing_count=sec_issuing_count,
            sec_issuing_denominator=len(window_events),
            weighted_cross_cluster_numerator=weighted_cross,
            weighted_cross_cluster_denominator=weighted_total,
        )
    return summaries


def _extract_first_int(pattern: str, text: str) -> int:
    match = re.search(pattern, text)
    if not match:
        raise ValueError(f"Pattern not found: {pattern}")
    return int(match.group(1))


def _extract_ratio(pattern: str, text: str) -> tuple[int, int, str]:
    match = re.search(pattern, text)
    if not match:
        raise ValueError(f"Pattern not found: {pattern}")
    return int(match.group(1)), int(match.group(2)), match.group(3)


def _extract_window_row(label: str, text: str) -> re.Match[str]:
    match = re.search(
        (
            rf"\| {re.escape(label)} \| `(\d+)` \| `(\d+)` \| `(\d+)` \| "
            r"`([0-9.]+)` \| `(\d+) / 7` \| `(\d+) / (\d+)` \| "
            r"`(\d+) / (\d+) = ([0-9.]+)` \|"
        ),
        text,
    )
    if not match:
        raise ValueError(f"{label} row not found.")
    return match


def compare_nz_summary_to_docs(
    summary: RouteSummary,
    window_summary: WindowSummary,
    comparator_b_summary: WindowSummary,
    project_status_path: Path,
    i_summary_path: Path,
    seed_readout_path: Path,
    window_comparison_path: Path,
    sensitivity_note_path: Path,
) -> list[ValidationResult]:
    results: list[ValidationResult] = []

    project_status = project_status_path.read_text(encoding="utf-8")
    i_summary = i_summary_path.read_text(encoding="utf-8")
    seed_readout = seed_readout_path.read_text(encoding="utf-8")
    window_comparison = window_comparison_path.read_text(encoding="utf-8")
    sensitivity_note = sensitivity_note_path.read_text(encoding="utf-8")

    expected_event_count = _extract_first_int(
        r"`(\d+)`-event (?:seed|public) ledger",
        project_status,
    )
    expected_main_interval = _extract_first_int(
        r"`(\d+)`-event main perturbation interval", project_status
    )
    expected_active_edges = _extract_first_int(
        r"active directed edges observed: `(\d+)`",
        i_summary,
    )
    ratio_num, ratio_den, ratio_display = _extract_ratio(
        r"occupied-edge ratio: `(\d+) / (\d+) = ([0-9.]+)`", i_summary
    )
    weighted_num, weighted_den, weighted_display = _extract_ratio(
        r"cross-cluster weighted edge occurrences: `(\d+) / (\d+) = ([0-9.]+)`", i_summary
    )
    issuing_num, issuing_den = (
        _extract_first_int(
            r"strategic executive coordination issues `(\d+) / \d+` coded events",
            i_summary,
        ),
        _extract_first_int(
            r"strategic executive coordination issues `\d+ / (\d+)` coded events",
            i_summary,
        ),
    )
    pi_receiving_num = _extract_first_int(
        r"`public-information coordination` receives `(\d+)/\d+` events", seed_readout
    )
    pi_receiving_den = _extract_first_int(
        r"`public-information coordination` receives `\d+/(\d+)` events", seed_readout
    )
    main_window_match = _extract_window_row("Main perturbation interval", window_comparison)
    comparator_b_match = _extract_window_row("Comparator B", window_comparison)
    sensitivity_event_count = _extract_first_int(r"- `(\d+)` total coded events", sensitivity_note)
    sensitivity_main_interval = _extract_first_int(
        r"- `(\d+)` main-interval events", sensitivity_note
    )
    sensitivity_sec_num = _extract_first_int(
        r"- `strategic executive coordination` issues `(\d+) / \d+`", sensitivity_note
    )
    sensitivity_sec_den = _extract_first_int(
        r"- `strategic executive coordination` issues `\d+ / (\d+)`", sensitivity_note
    )
    sensitivity_pi_num = _extract_first_int(
        r"- `public-information coordination` receives `(\d+) / \d+`", sensitivity_note
    )
    sensitivity_pi_den = _extract_first_int(
        r"- `public-information coordination` receives `\d+ / (\d+)`", sensitivity_note
    )
    sensitivity_weighted_num, sensitivity_weighted_den, sensitivity_weighted_display = (
        _extract_ratio(
            r"- weighted cross-cluster routing = `(\d+) / (\d+) = ([0-9.]+)`",
            sensitivity_note,
        )
    )

    checks = [
        ("nz-event-count", summary.event_count, expected_event_count),
        ("nz-main-interval-count", summary.main_interval_count, expected_main_interval),
        ("nz-active-edges", summary.active_edges, expected_active_edges),
        ("nz-occupied-edge-numerator", summary.active_edges, ratio_num),
        ("nz-occupied-edge-denominator", POSSIBLE_DIRECTED_EDGES, ratio_den),
        (
            "nz-occupied-edge-ratio",
            _format_ratio(summary.active_edges, POSSIBLE_DIRECTED_EDGES, 3),
            ratio_display,
        ),
        (
            "nz-weighted-cross-numerator",
            summary.weighted_cross_cluster_numerator,
            weighted_num,
        ),
        (
            "nz-weighted-cross-denominator",
            summary.weighted_cross_cluster_denominator,
            weighted_den,
        ),
        (
            "nz-weighted-cross-ratio",
            _format_ratio(
                summary.weighted_cross_cluster_numerator,
                summary.weighted_cross_cluster_denominator,
                2,
            ),
            weighted_display,
        ),
        ("nz-issuing-concentration-numerator", summary.top_issuer_count, issuing_num),
        ("nz-issuing-concentration-denominator", summary.event_count, issuing_den),
        ("nz-pi-receiving-numerator", summary.public_information_receiving_count, pi_receiving_num),
        ("nz-pi-receiving-denominator", summary.event_count, pi_receiving_den),
        ("nz-main-window-events", window_summary.event_count, int(main_window_match.group(1))),
        (
            "nz-main-window-sigma3",
            window_summary.sigma3_event_count,
            int(main_window_match.group(2)),
        ),
        (
            "nz-main-window-pi-marked",
            window_summary.public_information_marked_count,
            int(main_window_match.group(3)),
        ),
        (
            "nz-main-window-breadth",
            f"{window_summary.mean_receiving_breadth:.1f}",
            main_window_match.group(4),
        ),
        (
            "nz-main-window-active-units",
            window_summary.active_units,
            int(main_window_match.group(5)),
        ),
        (
            "nz-main-window-sec-num",
            window_summary.sec_issuing_count,
            int(main_window_match.group(6)),
        ),
        (
            "nz-main-window-sec-den",
            window_summary.sec_issuing_denominator,
            int(main_window_match.group(7)),
        ),
        (
            "nz-main-window-weighted-cross-num",
            window_summary.weighted_cross_cluster_numerator,
            int(main_window_match.group(8)),
        ),
        (
            "nz-main-window-weighted-cross-den",
            window_summary.weighted_cross_cluster_denominator,
            int(main_window_match.group(9)),
        ),
        (
            "nz-main-window-weighted-cross-ratio",
            _format_ratio(
                window_summary.weighted_cross_cluster_numerator,
                window_summary.weighted_cross_cluster_denominator,
                2,
            ),
            main_window_match.group(10),
        ),
        (
            "nz-comparator-b-events",
            comparator_b_summary.event_count,
            int(comparator_b_match.group(1)),
        ),
        (
            "nz-comparator-b-sigma3",
            comparator_b_summary.sigma3_event_count,
            int(comparator_b_match.group(2)),
        ),
        (
            "nz-comparator-b-pi-marked",
            comparator_b_summary.public_information_marked_count,
            int(comparator_b_match.group(3)),
        ),
        (
            "nz-comparator-b-breadth",
            f"{comparator_b_summary.mean_receiving_breadth:.1f}",
            comparator_b_match.group(4),
        ),
        (
            "nz-comparator-b-active-units",
            comparator_b_summary.active_units,
            int(comparator_b_match.group(5)),
        ),
        (
            "nz-comparator-b-sec-num",
            comparator_b_summary.sec_issuing_count,
            int(comparator_b_match.group(6)),
        ),
        (
            "nz-comparator-b-sec-den",
            comparator_b_summary.sec_issuing_denominator,
            int(comparator_b_match.group(7)),
        ),
        (
            "nz-comparator-b-weighted-cross-num",
            comparator_b_summary.weighted_cross_cluster_numerator,
            int(comparator_b_match.group(8)),
        ),
        (
            "nz-comparator-b-weighted-cross-den",
            comparator_b_summary.weighted_cross_cluster_denominator,
            int(comparator_b_match.group(9)),
        ),
        (
            "nz-comparator-b-weighted-cross-ratio",
            _format_ratio(
                comparator_b_summary.weighted_cross_cluster_numerator,
                comparator_b_summary.weighted_cross_cluster_denominator,
                2,
            ),
            comparator_b_match.group(10),
        ),
        ("nz-sensitivity-event-count", summary.event_count, sensitivity_event_count),
        ("nz-sensitivity-main-interval", summary.main_interval_count, sensitivity_main_interval),
        ("nz-sensitivity-sec-num", summary.top_issuer_count, sensitivity_sec_num),
        ("nz-sensitivity-sec-den", summary.event_count, sensitivity_sec_den),
        ("nz-sensitivity-pi-num", summary.public_information_receiving_count, sensitivity_pi_num),
        ("nz-sensitivity-pi-den", summary.event_count, sensitivity_pi_den),
        (
            "nz-sensitivity-weighted-cross-num",
            summary.weighted_cross_cluster_numerator,
            sensitivity_weighted_num,
        ),
        (
            "nz-sensitivity-weighted-cross-den",
            summary.weighted_cross_cluster_denominator,
            sensitivity_weighted_den,
        ),
        (
            "nz-sensitivity-weighted-cross-ratio",
            _format_ratio(
                summary.weighted_cross_cluster_numerator,
                summary.weighted_cross_cluster_denominator,
                2,
            ),
            sensitivity_weighted_display,
        ),
    ]

    for check_name, found, expected in checks:
        status = "pass" if found == expected else "fail"
        results.append(
            ValidationResult(
                check_name=check_name,
                status=status,
                message="Published NZ metric matches computed value."
                if status == "pass"
                else "Published NZ metric diverges from computed value.",
                expected=str(expected),
                found=str(found),
            )
        )
    return results


def render_nz_summary_report(
    summary: RouteSummary,
    window_summary: WindowSummary,
    validations: list[ValidationResult],
    source_files: list[Path],
    generated_at: str,
) -> str:
    mismatches = [result for result in validations if result.status != "pass"]
    occupied_ratio = _format_ratio(summary.active_edges, POSSIBLE_DIRECTED_EDGES, 3)
    weighted_ratio = _format_ratio(
        summary.weighted_cross_cluster_numerator,
        summary.weighted_cross_cluster_denominator,
        2,
    )
    fit_status = (
        "Matches current published docs."
        if not mismatches
        else "Human review required before trusting this against published docs."
    )
    mismatch_lines = (
        "\n".join(
            f"- `{result.check_name}`: expected `{result.expected}`, found `{result.found}`"
            for result in mismatches
        )
        if mismatches
        else "- none"
    )
    files = "\n".join(f"- `{format_report_path(path)}`" for path in source_files)
    weighted_line = (
        f"- weighted cross-cluster routing: "
        f"`{summary.weighted_cross_cluster_numerator} / "
        f"{summary.weighted_cross_cluster_denominator} = {weighted_ratio}`"
    )
    pi_line = (
        f"- public-information receiving share: "
        f"`{summary.public_information_receiving_count} / {summary.event_count}`"
    )
    lines = [
        "# NZ Summary Report",
        "",
        f"Generated: `{generated_at}`",
        "",
        "## Source files",
        "",
        files,
        "",
        "## Computed values",
        "",
        f"- event count: `{summary.event_count}`",
        f"- main interval count: `{summary.main_interval_count}`",
        f"- active units: `{summary.active_units} / 7`",
        f"- active edges: `{summary.active_edges}`",
        (
            f"- occupied-edge ratio: "
            f"`{summary.active_edges} / {POSSIBLE_DIRECTED_EDGES} = {occupied_ratio}`"
        ),
        weighted_line,
        (
            f"- issuing concentration: "
            f"`{summary.top_issuer} = {summary.top_issuer_count} / {summary.event_count}`"
        ),
        pi_line,
        f"- mean receiving breadth: `{summary.mean_receiving_breadth:.1f}`",
        f"- main interval `sigma3` events: `{window_summary.sigma3_event_count}`",
        f"- main interval PI-marked events: `{window_summary.public_information_marked_count}`",
        "",
        "## Assumptions",
        "",
        "- event metrics are derived from the public event ledger only",
        "- `sigma2` cluster mapping follows the current public research program",
        "- lag pairs are not recomputed in tranche 1",
        "",
        "## Mismatch section",
        "",
        mismatch_lines,
        "",
        "## Fit status",
        "",
        fit_status,
        "",
        "## Human validation required",
        "",
        "This output is read-only and provisional until a human reviews it.",
    ]
    return "\n".join(lines)


def compute_nz_lag_pairs(events: list[LedgerEvent]) -> list[tuple[str, str, str, int]]:
    event_index = {event.event_id: event for event in events}
    pair_specs = (
        ("Escalation staging", "nz-p-010", "nz-p-006"),
        ("Level 3 transition staging", "nz-p-012", "nz-p-013"),
        ("Level 2 preparation staging", "nz-p-027", "nz-b-002"),
        ("Transition-period planning to Level 2", "nz-b-006", "nz-b-002"),
        ("Level 2 staging", "nz-b-004", "nz-b-002"),
        ("Legal handoff into Level 2", "nz-b-005", "nz-b-002"),
    )
    pairs: list[tuple[str, str, str, int]] = []
    for label, start_id, end_id in pair_specs:
        start = event_index[start_id]
        end = event_index[end_id]
        start_date = datetime.strptime(start.timestamp_or_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end.timestamp_or_date, "%Y-%m-%d").date()
        pairs.append((label, start.event_id, end.event_id, (end_date - start_date).days))
    return pairs


def render_nz_lag_report(
    lag_pairs: list[tuple[str, str, str, int]],
    generated_at: str,
    source_files: list[Path],
) -> str:
    files = "\n".join(f"- `{format_report_path(path)}`" for path in source_files)
    gaps = [gap for _, _, _, gap in lag_pairs]
    sorted_gaps = sorted(gaps)
    rows = "\n".join(
        f"| {label} | `{start_id}` | `{end_id}` | `{gap}` |"
        for label, start_id, end_id, gap in lag_pairs
    )
    lines = [
        "# NZ Lag Surface Report",
        "",
        f"Generated: `{generated_at}`",
        "",
        "## Source files",
        "",
        files,
        "",
        "## Computed lag pairs",
        "",
        "| Pair | Start event | End event | Date-grain gap |",
        "|---|---|---|---:|",
        rows,
        "",
        "## Summary",
        "",
        f"- paired gaps: `{', '.join(str(gap) for gap in sorted_gaps)}` days",
        f"- median paired gap: `{median(gaps):g}` days",
        f"- observed range: `{min(gaps)}-{max(gaps)}` days",
        "",
        "## Assumptions",
        "",
        "- lag pairs follow the current route-local estimator implementation",
        "- only explicit public transition pairs are included",
        "- this report is a read-only support surface, not an auto-update mechanism",
        "",
        "## Fit status",
        "",
        (
            "Human review required. This report does not yet compare against a "
            "dedicated published lag-report surface."
        ),
        "",
        "## Human validation required",
        "",
        "This output is read-only and provisional until a human reviews it.",
    ]
    return "\n".join(lines)


def render_nz_window_report(
    window_summaries: dict[str, WindowSummary],
    generated_at: str,
    source_files: list[Path],
) -> str:
    files = "\n".join(f"- `{format_report_path(path)}`" for path in source_files)
    rows = []
    for label in ("Comparator A", "Main perturbation interval", "Comparator B"):
        summary = window_summaries[label]
        weighted_share = _format_ratio(
            summary.weighted_cross_cluster_numerator,
            summary.weighted_cross_cluster_denominator,
            2,
        )
        rows.append(
            f"| {label} | `{summary.event_count}` | `{summary.sigma3_event_count}` | "
            f"`{summary.public_information_marked_count}` | "
            f"`{summary.mean_receiving_breadth:.1f}` | "
            f"`{summary.active_units} / 7` | "
            f"`{summary.sec_issuing_count} / {summary.sec_issuing_denominator}` | "
            f"`{summary.weighted_cross_cluster_numerator} / "
            f"{summary.weighted_cross_cluster_denominator} = {weighted_share}` |"
        )
    table = "\n".join(rows)
    header = (
        "| Window | Events | `sigma3` events | PI-marked events | Mean breadth | "
        "Active units | SEC issue share | Weighted cross-cluster share |"
    )
    lines = [
        "# NZ Window Comparison Report",
        "",
        f"Generated: `{generated_at}`",
        "",
        "## Source files",
        "",
        files,
        "",
        "## Computed window table",
        "",
        header,
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        table,
        "",
        "## Assumptions",
        "",
        "- lag signals are not recomputed in tranche 1",
        "- windows are defined by the current NZ event-id prefixes",
        "",
        "## Fit status",
        "",
        "Human validation required.",
        "",
        "## Human validation required",
        "",
        "This output is read-only and provisional until a human reviews it.",
    ]
    return "\n".join(lines)
