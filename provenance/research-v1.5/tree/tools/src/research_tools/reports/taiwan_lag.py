from __future__ import annotations

from datetime import datetime
from pathlib import Path

from research_tools.models.ledger import LedgerEvent
from research_tools.paths import format_report_path

TAIWAN_LAG_PAIR = (
    "Bounded quarantine-routing lag pair",
    "tw-p-002",
    "tw-p-010",
)


def compute_taiwan_lag_pair(events: list[LedgerEvent]) -> tuple[str, str, str, int]:
    event_index = {event.event_id: event for event in events}
    label, start_id, end_id = TAIWAN_LAG_PAIR
    start = event_index[start_id]
    end = event_index[end_id]
    start_date = datetime.strptime(start.timestamp_or_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(end.timestamp_or_date, "%Y-%m-%d").date()
    return (label, start.event_id, end.event_id, (end_date - start_date).days)


def render_taiwan_lag_report(
    lag_pair: tuple[str, str, str, int],
    generated_at: str,
    source_files: list[Path],
) -> str:
    label, start_id, end_id, gap = lag_pair
    files = "\n".join(f"- `{format_report_path(path)}`" for path in source_files)
    current_limit_line = (
        "- this report records the current lag limit rather than implying a "
        "settled Taiwan `L` surface"
    )
    fit_status = (
        "Human review required. This report documents the current Taiwan lag "
        "limit and does not claim more than one clean pair."
    )
    lines = [
        "# Taiwan Lag-Limit Report",
        "",
        f"Generated: `{generated_at}`",
        "",
        "## Source files",
        "",
        files,
        "",
        "## Current publishable lag pair",
        "",
        "| Pair | Start event | End event | Date-grain gap |",
        "|---|---|---|---:|",
        f"| {label} | `{start_id}` | `{end_id}` | `{gap}` |",
        "",
        "## Current limit",
        "",
        "- only one conservative clean Taiwan lag pair is currently publishable",
        "- no second clean pair is yet strong enough for a serious cross-case `L` comparison",
        current_limit_line,
        "",
        "## Assumptions",
        "",
        "- the lag pair follows the current bounded Taiwan public ledger only",
        "- the pair is read as a cautious decision-to-observed-implementation support surface",
        "- this report is read-only and does not promote a stronger comparative claim by itself",
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
