from __future__ import annotations

import re
from pathlib import Path

from research_tools.config import POSSIBLE_DIRECTED_EDGES
from research_tools.models.reports import RouteSummary, ValidationResult
from research_tools.paths import format_report_path


def _format_ratio(numerator: int, denominator: int, digits: int) -> str:
    if denominator == 0:
        return "0"
    return f"{numerator / denominator:.{digits}f}"


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


def _presence_result(
    check_name: str,
    text: str,
    expected: str,
    path: Path,
) -> ValidationResult:
    present = expected in text
    return ValidationResult(
        check_name=check_name,
        status="pass" if present else "fail",
        message="Published Taiwan chapter surface keeps the expected stable phrase."
        if present
        else "Published Taiwan chapter surface is missing the expected stable phrase.",
        expected=expected,
        found="present" if present else "missing",
        path=str(path),
    )


def compare_taiwan_summary_to_docs(
    summary: RouteSummary,
    ledger_path: Path,
    evidence_map_path: Path,
    table_plan_path: Path,
) -> list[ValidationResult]:
    ledger_text = ledger_path.read_text(encoding="utf-8")
    evidence_map_text = evidence_map_path.read_text(encoding="utf-8")
    table_plan_text = table_plan_path.read_text(encoding="utf-8")
    results: list[ValidationResult] = []

    weighted_pattern = r"- weighted cross-cluster edge share: `(\d+) / (\d+) = ([0-9.]+)`"
    ledger_pi_num_pattern = (
        r"- public-information coordination receives `(\d+) / \d+` seeded events"
    )
    ledger_pi_den_pattern = (
        r"- public-information coordination receives `\d+ / (\d+)` seeded events"
    )
    ledger_health_issuer_num_pattern = (
        r"- issuing concentration: `public-health policy and command` issues `(\d+) / \d+`"
    )
    ledger_border_issuer_num_pattern = (
        r"`border-control coordination` issues `(\d+) / \d+` seeded events"
    )
    ledger_issuer_den_pattern = (
        r"- issuing concentration: `public-health policy and command` and "
        r"`border-control coordination` each issue `\d+ / (\d+)` seeded events"
    )
    evidence_health_num_pattern = (
        r"- top issuing share: `public-health policy and command = (\d+) / \d+`; "
        r"`border-control coordination = \d+ / \d+`"
    )
    evidence_health_den_pattern = (
        r"- top issuing share: `public-health policy and command = \d+ / (\d+)`; "
        r"`border-control coordination = \d+ / \d+`"
    )
    evidence_border_num_pattern = (
        r"- top issuing share: `public-health policy and command = \d+ / \d+`; "
        r"`border-control coordination = (\d+) / \d+`"
    )
    evidence_border_den_pattern = (
        r"- top issuing share: `public-health policy and command = \d+ / \d+`; "
        r"`border-control coordination = \d+ / (\d+)`"
    )
    evidence_pi_num_pattern = r"- public-information receiving share: `(\d+) / \d+`"
    evidence_pi_den_pattern = r"- public-information receiving share: `\d+ / (\d+)`"

    ledger_weighted = _extract_ratio(weighted_pattern, ledger_text)
    evidence_weighted = _extract_ratio(weighted_pattern, evidence_map_text)
    ledger_breadth_match = re.search(r"- mean receiving breadth: `([0-9.]+)`", ledger_text)
    evidence_breadth_match = re.search(
        r"- mean receiving breadth: `([0-9.]+)`",
        evidence_map_text,
    )

    ledger_checks = [
        (
            "taiwan-ledger-event-count",
            summary.event_count,
            _extract_first_int(r"- total seeded events: `(\d+)`", ledger_text),
            ledger_path,
        ),
        (
            "taiwan-ledger-active-units",
            summary.active_units,
            _extract_first_int(r"- active `sigma1` units visible: `(\d+) / 7`", ledger_text),
            ledger_path,
        ),
        (
            "taiwan-ledger-active-edges",
            summary.active_edges,
            _extract_first_int(r"- active directed edges: `(\d+)`", ledger_text),
            ledger_path,
        ),
        (
            "taiwan-ledger-weighted-cross-numerator",
            summary.weighted_cross_cluster_numerator,
            ledger_weighted[0],
            ledger_path,
        ),
        (
            "taiwan-ledger-weighted-cross-denominator",
            summary.weighted_cross_cluster_denominator,
            ledger_weighted[1],
            ledger_path,
        ),
        (
            "taiwan-ledger-weighted-cross-ratio",
            _format_ratio(
                summary.weighted_cross_cluster_numerator,
                summary.weighted_cross_cluster_denominator,
                2,
            ),
            ledger_weighted[2],
            ledger_path,
        ),
        (
            "taiwan-ledger-mean-breadth",
            f"{summary.mean_receiving_breadth:.1f}",
            ledger_breadth_match.group(1),
            ledger_path,
        ),
        (
            "taiwan-ledger-pi-receiving-numerator",
            summary.public_information_receiving_count,
            _extract_first_int(ledger_pi_num_pattern, ledger_text),
            ledger_path,
        ),
        (
            "taiwan-ledger-pi-receiving-denominator",
            summary.event_count,
            _extract_first_int(ledger_pi_den_pattern, ledger_text),
            ledger_path,
        ),
        (
            "taiwan-ledger-top-issuer-health-num",
            summary.top_issuer_count,
            _extract_first_int(ledger_health_issuer_num_pattern, ledger_text),
            ledger_path,
        ),
        (
            "taiwan-ledger-top-issuer-border-num",
            summary.top_issuer_count,
            _extract_first_int(ledger_border_issuer_num_pattern, ledger_text),
            ledger_path,
        ),
        (
            "taiwan-ledger-top-issuer-den",
            summary.event_count,
            _extract_first_int(r"issues `\d+ / (\d+)` seeded events", ledger_text),
            ledger_path,
        ),
    ]

    evidence_checks = [
        (
            "taiwan-evidence-map-event-count",
            summary.event_count,
            _extract_first_int(r"- seeded events: `(\d+)`", evidence_map_text),
            evidence_map_path,
        ),
        (
            "taiwan-evidence-map-active-units",
            summary.active_units,
            _extract_first_int(r"- active `sigma1` units: `(\d+) / 7`", evidence_map_text),
            evidence_map_path,
        ),
        (
            "taiwan-evidence-map-active-edges",
            summary.active_edges,
            _extract_first_int(r"- active directed edges: `(\d+)`", evidence_map_text),
            evidence_map_path,
        ),
        (
            "taiwan-evidence-map-weighted-cross-numerator",
            summary.weighted_cross_cluster_numerator,
            evidence_weighted[0],
            evidence_map_path,
        ),
        (
            "taiwan-evidence-map-weighted-cross-denominator",
            summary.weighted_cross_cluster_denominator,
            evidence_weighted[1],
            evidence_map_path,
        ),
        (
            "taiwan-evidence-map-weighted-cross-ratio",
            _format_ratio(
                summary.weighted_cross_cluster_numerator,
                summary.weighted_cross_cluster_denominator,
                2,
            ),
            evidence_weighted[2],
            evidence_map_path,
        ),
        (
            "taiwan-evidence-map-mean-breadth",
            f"{summary.mean_receiving_breadth:.1f}",
            evidence_breadth_match.group(1),
            evidence_map_path,
        ),
        (
            "taiwan-evidence-map-top-issuer-health-num",
            summary.top_issuer_count,
            _extract_first_int(evidence_health_num_pattern, evidence_map_text),
            evidence_map_path,
        ),
        (
            "taiwan-evidence-map-top-issuer-health-den",
            summary.event_count,
            _extract_first_int(evidence_health_den_pattern, evidence_map_text),
            evidence_map_path,
        ),
        (
            "taiwan-evidence-map-top-issuer-border-num",
            summary.top_issuer_count,
            _extract_first_int(evidence_border_num_pattern, evidence_map_text),
            evidence_map_path,
        ),
        (
            "taiwan-evidence-map-top-issuer-border-den",
            summary.event_count,
            _extract_first_int(evidence_border_den_pattern, evidence_map_text),
            evidence_map_path,
        ),
        (
            "taiwan-evidence-map-pi-receiving-numerator",
            summary.public_information_receiving_count,
            _extract_first_int(evidence_pi_num_pattern, evidence_map_text),
            evidence_map_path,
        ),
        (
            "taiwan-evidence-map-pi-receiving-denominator",
            summary.event_count,
            _extract_first_int(evidence_pi_den_pattern, evidence_map_text),
            evidence_map_path,
        ),
    ]

    for check_name, found, expected, path in ledger_checks + evidence_checks:
        status = "pass" if found == expected else "fail"
        results.append(
            ValidationResult(
                check_name=check_name,
                status=status,
                message="Published Taiwan metric matches computed value."
                if status == "pass"
                else "Published Taiwan metric diverges from computed value.",
                expected=str(expected),
                found=str(found),
                path=str(path),
            )
        )

    weighted_share = _format_ratio(
        summary.weighted_cross_cluster_numerator,
        summary.weighted_cross_cluster_denominator,
        2,
    )
    table_expectations = [
        (
            "taiwan-table-plan-window-snapshot-events",
            f"`{summary.event_count}` total events",
        ),
        (
            "taiwan-table-plan-window-snapshot-active-units",
            f"`{summary.active_units} / 7` active `sigma1` units",
        ),
        (
            "taiwan-table-plan-window-snapshot-active-edges",
            f"`{summary.active_edges}` active directed edges",
        ),
        (
            "taiwan-table-plan-issuing-health-share",
            (
                f"`public-health policy and command = {summary.top_issuer_count} / "
                f"{summary.event_count}`"
            ),
        ),
        (
            "taiwan-table-plan-issuing-border-share",
            (
                f"`border-control coordination = {summary.top_issuer_count} / "
                f"{summary.event_count}`"
            ),
        ),
        (
            "taiwan-table-plan-pi-share",
            (
                f"`public-information coordination = "
                f"{summary.public_information_receiving_count} / {summary.event_count}` "
                "receiving share"
            ),
        ),
        (
            "taiwan-table-plan-bounded-comparison-events",
            f"`{summary.event_count}` Taiwan events versus `38` New Zealand events",
        ),
        (
            "taiwan-table-plan-bounded-comparison-weighted-share",
            f"`{weighted_share}` weighted cross-cluster share versus `0.75`",
        ),
        (
            "taiwan-table-plan-bounded-comparison-breadth",
            f"`{summary.mean_receiving_breadth:.1f}` receiving breadth versus `3.7`",
        ),
        (
            "taiwan-table-plan-lag-limit",
            "one conservative clean lag pair; explicit lag-limit section required",
        ),
    ]

    for check_name, expected in table_expectations:
        results.append(
            _presence_result(check_name, table_plan_text, expected, table_plan_path)
        )

    return results


def render_taiwan_summary_report(
    summary: RouteSummary,
    validations: list[ValidationResult],
    source_files: list[Path],
    generated_at: str,
) -> str:
    mismatches = [result for result in validations if result.status != "pass"]
    files = "\n".join(f"- `{format_report_path(path)}`" for path in source_files)
    weighted_share = _format_ratio(
        summary.weighted_cross_cluster_numerator,
        summary.weighted_cross_cluster_denominator,
        2,
    )
    mismatch_lines = (
        "\n".join(
            f"- `{result.check_name}`: expected `{result.expected}`, found `{result.found}`"
            for result in mismatches
        )
        if mismatches
        else "- none"
    )
    fit_status = (
        "Matches current published Taiwan chapter-facing docs."
        if not mismatches
        else (
            "Human review required before trusting this against "
            "published Taiwan chapter-facing docs."
        )
    )
    lines = [
        "# Taiwan Summary Report",
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
        f"- active units: `{summary.active_units} / 7`",
        f"- active directed edges: `{summary.active_edges}`",
        (
            f"- occupied-edge ratio: `{summary.active_edges} / "
            f"{POSSIBLE_DIRECTED_EDGES} = "
            f"{_format_ratio(summary.active_edges, POSSIBLE_DIRECTED_EDGES, 3)}`"
        ),
        (
            f"- weighted cross-cluster edge share: `"
            f"{summary.weighted_cross_cluster_numerator} / "
            f"{summary.weighted_cross_cluster_denominator} = "
            f"{weighted_share}`"
        ),
        f"- mean receiving breadth: `{summary.mean_receiving_breadth:.1f}`",
        (
            f"- issuing concentration: `public-health policy and command = "
            f"{summary.top_issuer_count} / {summary.event_count}`; "
            f"`border-control coordination = {summary.top_issuer_count} / "
            f"{summary.event_count}`"
        ),
        (
            f"- public-information receiving share: `"
            f"{summary.public_information_receiving_count} / {summary.event_count}`"
        ),
        "",
        "## Assumptions",
        "",
        "- values are derived from the current bounded Taiwan public ledger only",
        "- Taiwan remains chapter-facing and bounded rather than fully symmetric with New Zealand",
        "- the current lag surface stays limited to one conservative clean pair",
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
