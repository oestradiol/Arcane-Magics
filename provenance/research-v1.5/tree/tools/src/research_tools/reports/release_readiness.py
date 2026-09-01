from __future__ import annotations

from pathlib import Path

from research_tools.models.reports import ValidationResult
from research_tools.paths import format_optional_report_path, format_report_path


def render_release_readiness_report(
    generated_at: str,
    results: list[ValidationResult],
    source_files: list[Path],
) -> str:
    blockers = [result for result in results if result.status != "pass"]
    files = "\n".join(f"- `{format_report_path(path)}`" for path in source_files)
    blocker_lines = (
        "\n".join(
            f"- `{result.check_name}` [{result.status}] {result.message}"
            + (f" Expected `{result.expected}`." if result.expected else "")
            + (f" Found `{result.found}`." if result.found else "")
            + (
                f" Path `{format_optional_report_path(result.path)}`."
                if result.path
                else ""
            )
            for result in blockers
        )
        if blockers
        else "- none"
    )
    result_lines = "\n".join(
        f"- `{result.check_name}` [{result.status}] {result.message}"
        + (f" Expected `{result.expected}`." if result.expected else "")
        + (f" Found `{result.found}`." if result.found else "")
        + (
            f" Path `{format_optional_report_path(result.path)}`."
            if result.path
            else ""
        )
        for result in results
    )
    status_line = (
        "Zero unresolved release blockers."
        if not blockers
        else "Human review required before this can be treated as release-ready."
    )
    return f"""# Release Readiness Report

Generated: `{generated_at}`

## Source files

{files}

## Blocking status

{status_line}

## Blockers

{blocker_lines}

## Full results

{result_lines}

## Human validation required

This output is read-only and provisional until a human reviews it.
"""
