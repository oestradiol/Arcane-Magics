"""Ground-truth validator for three-case synthesis (76-event claim)."""

from __future__ import annotations

import re
from pathlib import Path

from research_tools.models.reports import ValidationResult
from research_tools.parse.australia_ledger import parse_australia_ledger
from research_tools.parse.nz_ledger import parse_nz_ledger
from research_tools.parse.taiwan_ledger import parse_taiwan_ledger


def _extract_expected_count(pattern: str, text: str, default: int | None = None) -> int:
    """Extract first integer matching pattern from text."""
    match = re.search(pattern, text)
    if match:
        return int(match.group(1))
    if default is not None:
        return default
    raise ValueError(f"Pattern not found: {pattern}")


def validate_three_case_synthesis(
    project_status_path: Path,
    nz_ledger_path: Path,
    taiwan_ledger_path: Path,
    australia_ledger_path: Path,
) -> list[ValidationResult]:
    """
    Validate that the 76-event synthesis claim matches actual ledger counts.

    Checks:
    - NZ ledger count matches prose claim in project-status
    - Taiwan ledger count matches prose claim in project-status
    - Australia ledger count matches prose claim in project-status (if present)
    - Sum of actual counts equals the claimed 76-event total
    """
    results: list[ValidationResult] = []

    # Parse actual ledger counts (ground truth)
    nz_events = parse_nz_ledger(nz_ledger_path)
    taiwan_events = parse_taiwan_ledger(taiwan_ledger_path)
    australia_events = parse_australia_ledger(australia_ledger_path)

    nz_actual = len(nz_events)
    taiwan_actual = len(taiwan_events)
    australia_actual = len(australia_events)
    actual_total = nz_actual + taiwan_actual + australia_actual

    # Parse project-status.md for claimed counts
    project_status_text = project_status_path.read_text(encoding="utf-8")

    # Extract claimed counts from project-status.md prose
    try:
        nz_claimed = _extract_expected_count(
            r"a `\d+`-event New Zealand.*?`(\d+)`-event.*?NZ", project_status_text
        )
    except ValueError:
        # Fallback: look for simpler pattern
        try:
            nz_claimed = _extract_expected_count(
                r"New Zealand.*?`(\d+)`-event", project_status_text
            )
        except ValueError:
            nz_claimed = None

    try:
        taiwan_claimed = _extract_expected_count(
            r"a `\d+`-event bounded Taiwan comparator.*?`(\d+)`", project_status_text
        )
    except ValueError:
        try:
            taiwan_claimed = _extract_expected_count(
                r"Taiwan comparator completed with \*\*`(\d+)`", project_status_text
            )
        except ValueError:
            taiwan_claimed = None

    try:
        australia_claimed = _extract_expected_count(
            r"an `\d+`-event Australia federal comparator.*?`(\d+)`", project_status_text
        )
    except ValueError:
        try:
            australia_claimed = _extract_expected_count(
                r"Australia federal comparator completed with \*\*`(\d+)`", project_status_text
            )
        except ValueError:
            australia_claimed = None

    # Extract the 76-event synthesis claim
    try:
        claimed_total = _extract_expected_count(
            r"three-case bounded synthesis \((\d+) events\)", project_status_text
        )
    except ValueError:
        try:
            claimed_total = _extract_expected_count(
                r"three-case.*?\((\d+) events\)", project_status_text
            )
        except ValueError:
            claimed_total = None

    # Validate individual route counts against claims
    if nz_claimed is not None:
        results.append(
            ValidationResult(
                check_name="ground_truth-nz-event-count",
                status="pass" if nz_actual == nz_claimed else "fail",
                message="NZ ledger event count matches project-status claim."
                if nz_actual == nz_claimed
                else "NZ ledger event count diverges from project-status claim.",
                expected=str(nz_claimed),
                found=str(nz_actual),
                path=str(nz_ledger_path),
            )
        )

    if taiwan_claimed is not None:
        results.append(
            ValidationResult(
                check_name="ground_truth-taiwan-event-count",
                status="pass" if taiwan_actual == taiwan_claimed else "fail",
                message="Taiwan ledger event count matches project-status claim."
                if taiwan_actual == taiwan_claimed
                else "Taiwan ledger event count diverges from project-status claim.",
                expected=str(taiwan_claimed),
                found=str(taiwan_actual),
                path=str(taiwan_ledger_path),
            )
        )

    if australia_claimed is not None:
        results.append(
            ValidationResult(
                check_name="ground_truth-australia-event-count",
                status="pass" if australia_actual == australia_claimed else "fail",
                message="Australia ledger event count matches project-status claim."
                if australia_actual == australia_claimed
                else "Australia ledger event count diverges from project-status claim.",
                expected=str(australia_claimed),
                found=str(australia_actual),
                path=str(australia_ledger_path),
            )
        )

    # Validate the 76-event synthesis math
    if claimed_total is not None:
        results.append(
            ValidationResult(
                check_name="ground_truth-three-case-synthesis-total",
                status="pass" if actual_total == claimed_total else "fail",
                message=f"Three-case synthesis total matches claim ({actual_total} = {claimed_total})."
                if actual_total == claimed_total
                else f"Three-case synthesis total diverges from claim.",
                expected=str(claimed_total),
                found=str(actual_total),
                path=str(project_status_path),
            )
        )

    # Always report the actual counts as info
    results.append(
        ValidationResult(
            check_name="ground_truth-actual-counts",
            status="pass",
            message=f"Actual ledger counts: NZ={nz_actual}, Taiwan={taiwan_actual}, Australia={australia_actual}, Total={actual_total}",
        )
    )

    return results
