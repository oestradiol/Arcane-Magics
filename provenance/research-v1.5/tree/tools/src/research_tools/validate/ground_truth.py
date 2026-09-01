"""Ground-truth validator: verify surface claims against ledger reality.

This validator addresses the critique that existing validators only check consistency
between surfaces ("does doc A match doc B?") rather than correctness ("does doc A
match the actual ledger data?").
"""

from __future__ import annotations

import re
from pathlib import Path

from research_tools.models.reports import ValidationResult
from research_tools.parse.nz_ledger import parse_nz_ledger
from research_tools.parse.taiwan_ledger import parse_taiwan_ledger
from research_tools.parse.australia_ledger import parse_australia_ledger
from research_tools.paths import RepoPaths

# Patterns to extract claimed event counts from prose
EVENT_COUNT_PATTERNS = [
    re.compile(r"(\d+)[\s-]event"),  # "76-event", "76 event"
    re.compile(r"(\d+)\s+events"),   # "76 events"
    re.compile(r"`(\d+)`[\s-]event"),  # "`76`-event"
]


def _extract_claimed_counts(text: str) -> dict[str, int]:
    """Extract claimed event counts from text.

    Returns mapping of context -> count for disambiguation.
    """
    counts: dict[str, int] = {}

    # Look for explicit total claims
    total_matches = [
        ("three-case synthesis", re.search(r"three-case[^)]+\((\d+)\s+events?\)", text, re.IGNORECASE)),
        ("synthesis total", re.search(r"synthesis[^)]+\((\d+)\s+events?\)", text, re.IGNORECASE)),
        ("total events", re.search(r"(?:total|combined|aggregate)[^)]+\((\d+)\s+events?\)", text, re.IGNORECASE)),
    ]

    for label, match in total_matches:
        if match:
            counts[label] = int(match.group(1))

    # Look for individual route claims
    route_patterns = [
        ("nz", r"New Zealand[^)]+?(\d+)[\s-]event"),
        ("taiwan", r"Taiwan[^)]+?(\d+)[\s-]event"),
        ("australia", r"Australia[^)]+?(\d+)[\s-]event"),
        ("nz_backtick", r"`(\d+)`[\s-]event[^)]+New Zealand"),
        ("taiwan_backtick", r"`(\d+)`[\s-]event[^)]+Taiwan"),
        ("australia_backtick", r"`(\d+)`[\s-]event[^)]+Australia"),
    ]

    for label, pattern in route_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            counts[label] = int(match.group(1))

    return counts


def validate_ground_truth(paths: RepoPaths) -> list[ValidationResult]:
    """Validate that status surfaces match actual ledger data.

    This is the "ground truth" validator that checks prose claims against
    the actual event counts in the ledgers.
    """
    results: list[ValidationResult] = []

    # Parse actual ledger data
    nz_events = parse_nz_ledger(paths.nz_route_root / "event-ledger-seed.md")
    taiwan_events = parse_taiwan_ledger(paths.taiwan_route_root / "taiwan-event-ledger-seed.md")
    australia_events = parse_australia_ledger(paths.australia_route_root / "australia-event-ledger-seed.md")

    actual_counts = {
        "nz": len(nz_events),
        "taiwan": len(taiwan_events),
        "australia": len(australia_events),
        "total": len(nz_events) + len(taiwan_events) + len(australia_events),
    }

    # Read project-status.md
    project_status_path = paths.suf_root / "docs" / "project-status.md"
    project_status_text = project_status_path.read_text(encoding="utf-8")

    # Check explicit total claim in project-status.md
    # Format: "three-case synthesis (76 events)"
    total_claim_match = re.search(
        r"three-case[^)]+?\((\d+)\s+events?\)",
        project_status_text,
        re.IGNORECASE,
    )

    if total_claim_match:
        claimed_total = int(total_claim_match.group(1))
        if claimed_total == actual_counts["total"]:
            results.append(ValidationResult(
                check_name="ground-truth-total-events",
                status="pass",
                message=f"Project status correctly claims {actual_counts['total']} total events.",
                path=str(project_status_path),
                expected=str(actual_counts["total"]),
                found=str(claimed_total),
            ))
        else:
            results.append(ValidationResult(
                check_name="ground-truth-total-events",
                status="fail",
                message=(
                    f"Project status claims {claimed_total} total events "
                    f"but ledgers contain {actual_counts['total']} events "
                    f"(NZ {actual_counts['nz']} + Taiwan {actual_counts['taiwan']} + "
                    f"Australia {actual_counts['australia']})."
                ),
                path=str(project_status_path),
                expected=str(actual_counts["total"]),
                found=str(claimed_total),
            ))
    else:
        results.append(ValidationResult(
            check_name="ground-truth-total-events",
            status="fail",
            message="Could not find explicit three-case synthesis event count claim.",
            path=str(project_status_path),
            expected=f"pattern 'three-case ... ({actual_counts['total']} events)'",
            found="not found",
        ))

    # Check individual route claims
    # Look for specific patterns like "`38`-event New Zealand" or "`**`20`-event** bounded Taiwan"
    route_patterns = [
        ("nz", actual_counts["nz"], r"`(\d+)`[\s-]event\s+New Zealand"),
        ("taiwan", actual_counts["taiwan"], r"`(\d+)`[\s-]event\s+bounded\s+Taiwan"),
        ("australia", actual_counts["australia"], r"`(\d+)`[\s-]event\s+Australia\s+federal"),
    ]

    for route, actual, pattern in route_patterns:
        match = re.search(pattern, project_status_text, re.IGNORECASE)
        if match:
            claimed = int(match.group(1))
            if claimed == actual:
                results.append(ValidationResult(
                    check_name=f"ground-truth-{route}-events",
                    status="pass",
                    message=f"Project status correctly claims {actual} {route} events.",
                    path=str(project_status_path),
                    expected=str(actual),
                    found=str(claimed),
                ))
            else:
                results.append(ValidationResult(
                    check_name=f"ground-truth-{route}-events",
                    status="fail",
                    message=(
                        f"Project status claims {claimed} {route} events "
                        f"but ledger contains {actual} events."
                    ),
                    path=str(project_status_path),
                    expected=str(actual),
                    found=str(claimed),
                ))
        else:
            results.append(ValidationResult(
                check_name=f"ground-truth-{route}-events",
                status="fail",
                message=f"Could not find {route} event count claim with backtick format.",
                path=str(project_status_path),
                expected=f"`{actual}`-event ... {route}",
                found="not found",
            ))

    return results
