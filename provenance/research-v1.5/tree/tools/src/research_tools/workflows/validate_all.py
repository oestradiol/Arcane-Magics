from __future__ import annotations

from pathlib import Path

from research_tools.models.reports import ValidationResult
from research_tools.parse.source_registry import parse_source_registry, source_registry_index
from research_tools.paths import RepoPaths, format_optional_report_path, format_report_path
from research_tools.validate.archives import validate_archive_links
from research_tools.validate.knowledge import validate_knowledge_package
from research_tools.validate.links import validate_markdown_links
from research_tools.validate.release_hygiene import validate_release_hygiene
from research_tools.validate.route_consistency import (
    validate_australia_route,
    validate_nz_route,
    validate_taiwan_route,
)
from research_tools.validate.sources import validate_source_registry
from research_tools.validate.ground_truth import validate_ground_truth
from research_tools.validate.status_surfaces import validate_status_surfaces
from research_tools.validate.three_case_synthesis import validate_three_case_synthesis
from research_tools.validate.versions import validate_versions


def summarize_validation_results(results: list[ValidationResult]) -> tuple[int, int, int]:
    passed = sum(1 for result in results if result.status == "pass")
    failed = sum(1 for result in results if result.status == "fail")
    warned = sum(1 for result in results if result.status == "warn")
    return passed, failed, warned


def collect_validation_results(paths: RepoPaths) -> list[ValidationResult]:
    entries = parse_source_registry(paths.source_registry)
    source_index = source_registry_index(entries)
    results: list[ValidationResult] = []
    results.extend(validate_markdown_links(paths.research_root))
    results.extend(validate_source_registry(entries))
    results.extend(validate_archive_links(entries))
    results.extend(validate_nz_route(paths.nz_route_root, source_index))
    results.extend(validate_taiwan_route(paths.taiwan_route_root, source_index))
    results.extend(validate_australia_route(paths.australia_route_root, source_index))
    results.extend(validate_knowledge_package(paths.knowledge_root))
    results.extend(validate_versions(paths))
    results.extend(validate_status_surfaces(paths))
    results.extend(
        validate_three_case_synthesis(
            paths.suf_project_status,
            paths.nz_route_root / "event-ledger-seed.md",
            paths.taiwan_route_root / "taiwan-event-ledger-seed.md",
            paths.australia_route_root / "australia-event-ledger-seed.md",
        )
    )
    results.extend(validate_ground_truth(paths))
    results.extend(validate_release_hygiene(paths.research_root))
    return results


def render_validation_report(
    generated_at: str,
    results: list[ValidationResult],
    source_files: list[Path],
) -> str:
    passed, failed, warned = summarize_validation_results(results)
    files = "\n".join(f"- `{format_report_path(path)}`" for path in source_files)
    body = "\n".join(
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
    return f"""# Validation Report

Generated: `{generated_at}`

## Source files

{files}

## Summary

- passed: `{passed}`
- failed: `{failed}`
- warned: `{warned}`

## Results

{body}

## Human validation required

This output is read-only and provisional until a human reviews it.
"""
