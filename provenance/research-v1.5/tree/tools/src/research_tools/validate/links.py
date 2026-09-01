from __future__ import annotations

from pathlib import Path

from research_tools.models.reports import ValidationResult
from research_tools.parse.markdown_links import collect_markdown_links


def validate_markdown_links(root: Path) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    for link in collect_markdown_links(root):
        target = link.target
        if "://" in target or target.startswith("mailto:") or target.startswith("#"):
            continue
        clean_target = target.split("#", 1)[0]
        if not clean_target:
            continue
        resolved = (link.source_path.parent / clean_target).resolve()
        if not resolved.exists():
            results.append(
                ValidationResult(
                    check_name="markdown-link",
                    status="fail",
                    message="Relative Markdown target does not exist.",
                    path=str(link.source_path),
                    expected=clean_target,
                    found="missing",
                )
            )
    if not results:
        results.append(
            ValidationResult(
                check_name="markdown-link",
                status="pass",
                message="All relative Markdown links resolved.",
                path=str(root),
            )
        )
    return results
