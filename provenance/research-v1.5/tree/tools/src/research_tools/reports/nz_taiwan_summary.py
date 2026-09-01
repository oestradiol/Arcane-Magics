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


def _format_issuing_concentration(summary: RouteSummary) -> str:
    if len(summary.top_issuers) == 1:
        return f"{summary.top_issuer} = {summary.top_issuer_count} / {summary.event_count}"
    joined = " / ".join(summary.top_issuers)
    return f"{joined} = {summary.top_issuer_count} / {summary.event_count} each"


def compare_nz_taiwan_summary_to_docs(
    nz_summary: RouteSummary,
    taiwan_summary: RouteSummary,
    comparison_note_path: Path,
) -> list[ValidationResult]:
    nz_occupied = (
        f"{nz_summary.active_edges} / {POSSIBLE_DIRECTED_EDGES} = "
        f"{_format_ratio(nz_summary.active_edges, POSSIBLE_DIRECTED_EDGES, 3)}"
    )
    taiwan_occupied = (
        f"{taiwan_summary.active_edges} / {POSSIBLE_DIRECTED_EDGES} = "
        f"{_format_ratio(taiwan_summary.active_edges, POSSIBLE_DIRECTED_EDGES, 3)}"
    )
    nz_weighted = (
        f"{nz_summary.weighted_cross_cluster_numerator} / "
        f"{nz_summary.weighted_cross_cluster_denominator} = "
        f"{_format_ratio(
            nz_summary.weighted_cross_cluster_numerator,
            nz_summary.weighted_cross_cluster_denominator,
            2,
        )}"
    )
    taiwan_weighted = (
        f"{taiwan_summary.weighted_cross_cluster_numerator} / "
        f"{taiwan_summary.weighted_cross_cluster_denominator} = "
        f"{_format_ratio(
            taiwan_summary.weighted_cross_cluster_numerator,
            taiwan_summary.weighted_cross_cluster_denominator,
            2,
        )}"
    )
    nz_issuing = _format_issuing_concentration(nz_summary)
    taiwan_issuing = _format_issuing_concentration(taiwan_summary)
    text = comparison_note_path.read_text(encoding="utf-8")
    rows = {
        "seeded events": (nz_summary.event_count, taiwan_summary.event_count),
        "active `sigma1` units": (
            f"{nz_summary.active_units} / 7",
            f"{taiwan_summary.active_units} / 7",
        ),
        "active directed edges": (nz_summary.active_edges, taiwan_summary.active_edges),
        "occupied-edge ratio": (nz_occupied, taiwan_occupied),
        "weighted cross-cluster routing": (nz_weighted, taiwan_weighted),
        "mean receiving breadth": (
            f"{nz_summary.mean_receiving_breadth:.1f}",
            f"{taiwan_summary.mean_receiving_breadth:.1f}",
        ),
        "issuing concentration": (nz_issuing, taiwan_issuing),
        "public-information receiving share": (
            f"{nz_summary.public_information_receiving_count} / {nz_summary.event_count}",
            f"{taiwan_summary.public_information_receiving_count} / {taiwan_summary.event_count}",
        ),
    }
    results: list[ValidationResult] = []
    for label, (expected_nz, expected_taiwan) in rows.items():
        match = re.search(
            rf"\| {re.escape(label)} \| `([^`]+)` \| `([^`]+)` \|",
            text,
        )
        if not match:
            results.append(
                ValidationResult(
                    check_name=f"nz-taiwan-{label}",
                    status="fail",
                    message="Comparison row not found.",
                    expected=f"{expected_nz} / {expected_taiwan}",
                    found="missing",
                )
            )
            continue
        found_nz_raw, found_taiwan_raw = match.group(1), match.group(2)
        if isinstance(expected_nz, int):
            found_nz: str | int = int(found_nz_raw)
        else:
            found_nz = found_nz_raw
        if isinstance(expected_taiwan, int):
            found_taiwan: str | int = int(found_taiwan_raw)
        else:
            found_taiwan = found_taiwan_raw
        status = "pass" if found_nz == expected_nz and found_taiwan == expected_taiwan else "fail"
        results.append(
            ValidationResult(
                check_name=f"nz-taiwan-{label}",
                status=status,
                message="Published NZ-Taiwan row matches computed values."
                if status == "pass"
                else "Published NZ-Taiwan row diverges from computed values.",
                expected=f"{expected_nz} | {expected_taiwan}",
                found=f"{found_nz} | {found_taiwan}",
            )
        )
    return results


def render_nz_taiwan_report(
    nz_summary: RouteSummary,
    taiwan_summary: RouteSummary,
    validations: list[ValidationResult],
    source_files: list[Path],
    generated_at: str,
) -> str:
    mismatches = [result for result in validations if result.status != "pass"]
    nz_occupied = (
        f"{nz_summary.active_edges} / {POSSIBLE_DIRECTED_EDGES} = "
        f"{_format_ratio(nz_summary.active_edges, POSSIBLE_DIRECTED_EDGES, 3)}"
    )
    taiwan_occupied = (
        f"{taiwan_summary.active_edges} / {POSSIBLE_DIRECTED_EDGES} = "
        f"{_format_ratio(taiwan_summary.active_edges, POSSIBLE_DIRECTED_EDGES, 3)}"
    )
    nz_weighted = (
        f"{nz_summary.weighted_cross_cluster_numerator} / "
        f"{nz_summary.weighted_cross_cluster_denominator} = "
        f"{_format_ratio(
            nz_summary.weighted_cross_cluster_numerator,
            nz_summary.weighted_cross_cluster_denominator,
            2,
        )}"
    )
    taiwan_weighted = (
        f"{taiwan_summary.weighted_cross_cluster_numerator} / "
        f"{taiwan_summary.weighted_cross_cluster_denominator} = "
        f"{_format_ratio(
            taiwan_summary.weighted_cross_cluster_numerator,
            taiwan_summary.weighted_cross_cluster_denominator,
            2,
        )}"
    )
    nz_issuing = _format_issuing_concentration(nz_summary)
    taiwan_issuing = _format_issuing_concentration(taiwan_summary)
    mismatch_lines = (
        "\n".join(
            f"- `{result.check_name}`: expected `{result.expected}`, found `{result.found}`"
            for result in mismatches
        )
        if mismatches
        else "- none"
    )
    files = "\n".join(f"- `{format_report_path(path)}`" for path in source_files)
    fit_status = (
        "Matches current published docs."
        if not mismatches
        else "Human review required before trusting this against published docs."
    )
    mean_breadth_line = (
        f"| mean receiving breadth | `{nz_summary.mean_receiving_breadth:.1f}` | "
        f"`{taiwan_summary.mean_receiving_breadth:.1f}` |"
    )
    pi_line = (
        f"| public-information receiving share | "
        f"`{nz_summary.public_information_receiving_count} / {nz_summary.event_count}` | "
        f"`{taiwan_summary.public_information_receiving_count} / {taiwan_summary.event_count}` |"
    )
    lines = [
        "# NZ-Taiwan Summary Report",
        "",
        f"Generated: `{generated_at}`",
        "",
        "## Source files",
        "",
        files,
        "",
        "## Computed comparison",
        "",
        "| Readout | New Zealand baseline | Taiwan bounded comparator |",
        "|---|---|---|",
        f"| seeded events | `{nz_summary.event_count}` | `{taiwan_summary.event_count}` |",
        (
            f"| active `sigma1` units | `{nz_summary.active_units} / 7` | "
            f"`{taiwan_summary.active_units} / 7` |"
        ),
        (
            f"| active directed edges | `{nz_summary.active_edges}` | "
            f"`{taiwan_summary.active_edges}` |"
        ),
        f"| occupied-edge ratio | `{nz_occupied}` | `{taiwan_occupied}` |",
        f"| weighted cross-cluster routing | `{nz_weighted}` | `{taiwan_weighted}` |",
        mean_breadth_line,
        f"| issuing concentration | `{nz_issuing}` | `{taiwan_issuing}` |",
        pi_line,
        "",
        "## Assumptions",
        "",
        "- Taiwan is still bounded and thinner than the New Zealand route",
        (
            "- lag comparison remains limited because only one conservative clean "
            "Taiwan lag pair is currently publishable"
        ),
        "- values are derived from current public ledgers only",
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
