from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

sys.dont_write_bytecode = True
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")

from research_tools.parse.nz_ledger import parse_nz_ledger
from research_tools.parse.source_registry import parse_source_registry, source_registry_index
from research_tools.parse.taiwan_ledger import parse_taiwan_ledger
from research_tools.paths import format_optional_report_path, format_report_path, get_paths
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
from research_tools.reports.taiwan_lag import (
    compute_taiwan_lag_pair,
    render_taiwan_lag_report,
)
from research_tools.reports.taiwan_summary import (
    compare_taiwan_summary_to_docs,
    render_taiwan_summary_report,
)
from research_tools.validate.archives import validate_archive_links
from research_tools.validate.knowledge import validate_knowledge_package
from research_tools.validate.links import validate_markdown_links
from research_tools.validate.route_consistency import validate_nz_route, validate_taiwan_route
from research_tools.validate.sources import validate_source_registry
from research_tools.validate.status_surfaces import validate_status_surfaces
from research_tools.validate.versions import validate_versions
from research_tools.validate.ground_truth import validate_ground_truth
from research_tools.workflows.validate_clusters import (
    collect_validation_clusters,
    render_cluster_report,
)
from research_tools.workflows.validate_all import (
    collect_validation_results,
    render_validation_report,
)
from research_tools.generate.integrity_manifest import generate_integrity_manifest_v2
from research_tools.generate.file_registry import generate_file_registry


def _generated_at() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _write_output(filename: str, content: str) -> Path:
    paths = get_paths()
    paths.out_root.mkdir(parents=True, exist_ok=True)
    output_path = paths.out_root / filename
    output_path.write_text(content, encoding="utf-8")
    return output_path


def _results_exit_code(results: list) -> int:
    return 1 if any(result.status == "fail" for result in results) else 0


def _render_simple_results(
    title: str,
    generated_at: str,
    results: list,
    source_files: list[Path],
) -> str:
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
    return f"""# {title}

Generated: `{generated_at}`

## Source files

{files}

## Results

{body}

## Human validation required

This output is read-only and provisional until a human reviews it.
"""


def handle_validate_links(_: argparse.Namespace) -> int:
    paths = get_paths()
    results = validate_markdown_links(paths.research_root)
    output = _render_simple_results(
        "Validate Links",
        _generated_at(),
        results,
        [paths.research_root],
    )
    output_path = _write_output("validate-links.md", output)
    print(output_path)
    return _results_exit_code(results)


def handle_validate_archives(_: argparse.Namespace) -> int:
    paths = get_paths()
    entries = parse_source_registry(paths.source_registry)
    results = validate_archive_links(entries)
    output = _render_simple_results(
        "Validate Archives",
        _generated_at(),
        results,
        [paths.source_registry],
    )
    output_path = _write_output("validate-archives.md", output)
    print(output_path)
    return _results_exit_code(results)


def handle_validate_source_registry(_: argparse.Namespace) -> int:
    paths = get_paths()
    entries = parse_source_registry(paths.source_registry)
    results = validate_source_registry(entries)
    output = _render_simple_results(
        "Validate Source Registry",
        _generated_at(),
        results,
        [paths.source_registry],
    )
    output_path = _write_output("validate-source-registry.md", output)
    print(output_path)
    return _results_exit_code(results)


def handle_validate_route(args: argparse.Namespace) -> int:
    paths = get_paths()
    entries = parse_source_registry(paths.source_registry)
    index = source_registry_index(entries)
    if args.route == "nz":
        results = validate_nz_route(paths.nz_route_root, index)
        source_files = [
            paths.nz_route_root / "event-ledger-seed.md",
            paths.nz_route_root / "first-pass-i-summary.md",
            paths.nz_route_root / "first-pass-window-comparison.md",
            paths.nz_route_root / "first-pass-sensitivity-and-null-note.md",
            paths.suf_root / "docs" / "project-status.md",
        ]
        filename = "validate-route-nz.md"
        title = "Validate Route NZ"
    elif args.route == "taiwan":
        results = validate_taiwan_route(paths.taiwan_route_root, index)
        source_files = [
            paths.taiwan_route_root / "taiwan-event-ledger-seed.md",
            paths.taiwan_route_root / "first-nz-taiwan-comparison-note.md",
        ]
        filename = "validate-route-taiwan.md"
        title = "Validate Route Taiwan"
    else:  # australia
        from research_tools.validate.route_consistency import validate_australia_route
        results = validate_australia_route(paths.australia_route_root, index)
        source_files = [
            paths.australia_route_root / "australia-event-ledger-seed.md",
        ]
        filename = "validate-route-australia.md"
        title = "Validate Route Australia"
    output = _render_simple_results(title, _generated_at(), results, source_files)
    output_path = _write_output(filename, output)
    print(output_path)
    return _results_exit_code(results)


def handle_validate_knowledge(_: argparse.Namespace) -> int:
    paths = get_paths()
    results = validate_knowledge_package(paths.knowledge_root)
    output = _render_simple_results(
        "Validate Knowledge",
        _generated_at(),
        results,
        [paths.knowledge_root],
    )
    output_path = _write_output("validate-knowledge.md", output)
    print(output_path)
    return _results_exit_code(results)


def handle_validate_versions(_: argparse.Namespace) -> int:
    paths = get_paths()
    results = validate_versions(paths)
    output = _render_simple_results(
        "Validate Versions",
        _generated_at(),
        results,
        [
            paths.research_root / "CITATION.cff",
            paths.research_root / "CHANGELOG.md",
            paths.suf_root / "CITATION.cff",
            paths.suf_root / "CHANGELOG.md",
            paths.knowledge_root / "CITATION.cff",
            paths.knowledge_root / "CHANGELOG.md",
            paths.tools_root / "pyproject.toml",
            paths.tools_root / "src" / "research_tools" / "__init__.py",
            paths.tools_root / "CHANGELOG.md",
        ],
    )
    output_path = _write_output("validate-versions.md", output)
    print(output_path)
    return _results_exit_code(results)


def handle_validate_ground_truth(_: argparse.Namespace) -> int:
    paths = get_paths()
    results = validate_ground_truth(paths)
    output = _render_simple_results(
        "Validate Ground Truth",
        _generated_at(),
        results,
        [
            paths.nz_route_root / "event-ledger-seed.md",
            paths.taiwan_route_root / "taiwan-event-ledger-seed.md",
            paths.australia_route_root / "australia-event-ledger-seed.md",
            paths.suf_root / "docs" / "project-status.md",
        ],
    )
    output_path = _write_output("validate-ground-truth.md", output)
    print(output_path)
    return _results_exit_code(results)


def handle_validate_status_surfaces(_: argparse.Namespace) -> int:
    paths = get_paths()
    results = validate_status_surfaces(paths)
    output = _render_simple_results(
        "Validate Status Surfaces",
        _generated_at(),
        results,
        [
            paths.research_root / "README.md",
            paths.suf_root / "README.md",
            paths.suf_root / "docs" / "project-status.md",
            paths.suf_root / "docs" / "pending-inventory.md",
            paths.suf_root / "docs" / "argument" / "CONTRIBUTION_AND_POSITIONING.md",
            paths.suf_root / "docs" / "audit" / "OBJECTIONS_AND_EVIDENCE_STATUS.md",
            paths.suf_root / "meta" / "publication-scope.md",
            paths.suf_root / "ROADMAP.md",
            paths.suf_root / "framework" / "research-program.md",
        ],
    )
    output_path = _write_output("validate-status-surfaces.md", output)
    print(output_path)
    return _results_exit_code(results)


def handle_validate_all(_: argparse.Namespace) -> int:
    paths = get_paths()
    results = collect_validation_results(paths)
    output = render_validation_report(
        generated_at=_generated_at(),
        results=results,
        source_files=[
            paths.research_root,
            paths.source_registry,
            paths.nz_route_root / "event-ledger-seed.md",
            paths.taiwan_route_root / "taiwan-event-ledger-seed.md",
            paths.australia_route_root / "australia-event-ledger-seed.md",
            paths.knowledge_root,
            paths.research_root / "CITATION.cff",
            paths.suf_root / "CITATION.cff",
            paths.knowledge_root / "CITATION.cff",
            paths.tools_root / "pyproject.toml",
        ],
    )
    output_path = _write_output("validation-report.md", output)
    print(output_path)
    return _results_exit_code(results)


def handle_validate_clusters(_: argparse.Namespace) -> int:
    paths = get_paths()
    clusters = collect_validation_clusters(paths)
    output = render_cluster_report(
        generated_at=_generated_at(),
        clusters=clusters,
    )
    output_path = _write_output("validate-clusters.md", output)
    print(output_path)
    return 1 if any(cluster.failed for cluster in clusters) else 0


def handle_report_nz_summary(_: argparse.Namespace) -> int:
    paths = get_paths()
    events = parse_nz_ledger(paths.nz_route_root / "event-ledger-seed.md")
    summary = compute_route_summary("nz", events)
    window_summaries = compute_nz_window_summaries(events)
    validations = compare_nz_summary_to_docs(
        summary=summary,
        window_summary=window_summaries["Main perturbation interval"],
        comparator_b_summary=window_summaries["Comparator B"],
        project_status_path=paths.suf_root / "docs" / "project-status.md",
        i_summary_path=paths.nz_route_root / "first-pass-i-summary.md",
        seed_readout_path=paths.nz_route_root / "first-pass-seed-readout.md",
        window_comparison_path=paths.nz_route_root / "first-pass-window-comparison.md",
        sensitivity_note_path=paths.nz_route_root / "first-pass-sensitivity-and-null-note.md",
    )
    output = render_nz_summary_report(
        summary=summary,
        window_summary=window_summaries["Main perturbation interval"],
        validations=validations,
        source_files=[
            paths.nz_route_root / "event-ledger-seed.md",
            paths.nz_route_root / "first-pass-i-summary.md",
            paths.nz_route_root / "first-pass-seed-readout.md",
            paths.nz_route_root / "first-pass-window-comparison.md",
            paths.nz_route_root / "first-pass-sensitivity-and-null-note.md",
            paths.suf_root / "docs" / "project-status.md",
        ],
        generated_at=_generated_at(),
    )
    output_path = _write_output("nz-summary.md", output)
    print(output_path)
    return _results_exit_code(validations)


def handle_report_nz_window_comparison(_: argparse.Namespace) -> int:
    paths = get_paths()
    events = parse_nz_ledger(paths.nz_route_root / "event-ledger-seed.md")
    output = render_nz_window_report(
        compute_nz_window_summaries(events),
        _generated_at(),
        [
            paths.nz_route_root / "event-ledger-seed.md",
            paths.nz_route_root / "first-pass-window-comparison.md",
        ],
    )
    output_path = _write_output("nz-window-comparison.md", output)
    print(output_path)
    return 0


def handle_report_nz_lag_surface(_: argparse.Namespace) -> int:
    paths = get_paths()
    events = parse_nz_ledger(paths.nz_route_root / "event-ledger-seed.md")
    output = render_nz_lag_report(
        compute_nz_lag_pairs(events),
        _generated_at(),
        [
            paths.nz_route_root / "event-ledger-seed.md",
            paths.nz_route_root / "estimator-implementation.md",
            paths.nz_route_root / "first-pass-l-summary.md",
        ],
    )
    output_path = _write_output("nz-lag-surface.md", output)
    print(output_path)
    return 0


def handle_report_nz_taiwan_summary(_: argparse.Namespace) -> int:
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
        source_files=[
            paths.nz_route_root / "event-ledger-seed.md",
            paths.taiwan_route_root / "taiwan-event-ledger-seed.md",
            paths.taiwan_route_root / "first-nz-taiwan-comparison-note.md",
        ],
        generated_at=_generated_at(),
    )
    output_path = _write_output("nz-taiwan-summary.md", output)
    print(output_path)
    return _results_exit_code(validations)


def handle_report_taiwan_summary(_: argparse.Namespace) -> int:
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
        generated_at=_generated_at(),
    )
    output_path = _write_output("taiwan-summary.md", output)
    print(output_path)
    return _results_exit_code(validations)


def handle_report_taiwan_lag_limit(_: argparse.Namespace) -> int:
    paths = get_paths()
    taiwan_events = parse_taiwan_ledger(paths.taiwan_route_root / "taiwan-event-ledger-seed.md")
    output = render_taiwan_lag_report(
        compute_taiwan_lag_pair(taiwan_events),
        _generated_at(),
        [
            paths.taiwan_route_root / "taiwan-event-ledger-seed.md",
            paths.taiwan_route_root / "first-nz-taiwan-comparison-note.md",
            paths.taiwan_route_root / "taiwan-chapter-boundary-and-corpus.md",
        ],
    )
    output_path = _write_output("taiwan-lag-limit.md", output)
    print(output_path)
    return 0


def handle_report_release_readiness(_: argparse.Namespace) -> int:
    paths = get_paths()
    results = collect_validation_results(paths)
    output = render_release_readiness_report(
        generated_at=_generated_at(),
        results=results,
        source_files=[
            paths.research_root / "README.md",
            paths.research_root / "CHANGELOG.md",
            paths.research_root / "CITATION.cff",
            paths.suf_root / "README.md",
            paths.suf_root / "CHANGELOG.md",
            paths.suf_root / "docs" / "project-status.md",
            paths.knowledge_root / "README.md",
            paths.knowledge_root / "CHANGELOG.md",
            paths.tools_root / "README.md",
            paths.tools_root / "CHANGELOG.md",
            paths.tools_root / "pyproject.toml",
        ],
    )
    output_path = _write_output("release-readiness.md", output)
    print(output_path)
    return _results_exit_code(results)


def handle_generate_integrity_manifest(_: argparse.Namespace) -> int:
    paths = get_paths()
    try:
        manifest = generate_integrity_manifest_v2(paths.research_root)
        print(f"✓ Generated v0.2 integrity manifest with {manifest['file_count']} current surfaces")
        print(f"  Output: governance/AUTHORITATIVE_INTEGRITY_MANIFEST_v0_2.json")
        if manifest['_meta'].get('missing_files'):
            print(f"  ⚠ Warning: {len(manifest['_meta']['missing_files'])} files missing")
        return 0
    except ValueError as e:
        print(f"✗ Error: {e}")
        return 1


def handle_generate_file_registry(_: argparse.Namespace) -> int:
    paths = get_paths()
    try:
        registry = generate_file_registry(paths.research_root)
        print(f"✓ Generated file registry with {registry['file_count']} files")
        print(f"  Version: {registry['version']}")
        print(f"  Output: governance/REPOSITORY_FILE_REGISTRY_v0_1.json")
        return 0
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="research-tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_subparsers = validate_parser.add_subparsers(dest="validate_command", required=True)

    validate_subparsers.add_parser("links").set_defaults(func=handle_validate_links)
    validate_subparsers.add_parser("archives").set_defaults(func=handle_validate_archives)
    validate_subparsers.add_parser("knowledge").set_defaults(func=handle_validate_knowledge)
    validate_subparsers.add_parser("source-registry").set_defaults(
        func=handle_validate_source_registry
    )
    validate_subparsers.add_parser("versions").set_defaults(func=handle_validate_versions)
    validate_subparsers.add_parser("status-surfaces").set_defaults(
        func=handle_validate_status_surfaces
    )
    validate_subparsers.add_parser("ground-truth").set_defaults(
        func=handle_validate_ground_truth
    )
    validate_route_parser = validate_subparsers.add_parser("route")
    validate_route_parser.add_argument("--route", choices=("nz", "taiwan", "australia"), required=True)
    validate_route_parser.set_defaults(func=handle_validate_route)
    validate_subparsers.add_parser("all").set_defaults(func=handle_validate_all)
    validate_subparsers.add_parser("clusters").set_defaults(func=handle_validate_clusters)

    generate_parser = subparsers.add_parser("generate")
    generate_subparsers = generate_parser.add_subparsers(dest="generate_command", required=True)
    generate_subparsers.add_parser("integrity-manifest").set_defaults(
        func=handle_generate_integrity_manifest
    )
    generate_subparsers.add_parser("file-registry").set_defaults(
        func=handle_generate_file_registry
    )

    report_parser = subparsers.add_parser("report")
    report_subparsers = report_parser.add_subparsers(dest="report_command", required=True)
    report_subparsers.add_parser("nz-summary").set_defaults(func=handle_report_nz_summary)
    report_subparsers.add_parser("nz-window-comparison").set_defaults(
        func=handle_report_nz_window_comparison
    )
    report_subparsers.add_parser("nz-lag-surface").set_defaults(
        func=handle_report_nz_lag_surface
    )
    report_subparsers.add_parser("nz-taiwan-summary").set_defaults(
        func=handle_report_nz_taiwan_summary
    )
    report_subparsers.add_parser("taiwan-lag-limit").set_defaults(
        func=handle_report_taiwan_lag_limit
    )
    report_subparsers.add_parser("taiwan-summary").set_defaults(
        func=handle_report_taiwan_summary
    )
    report_subparsers.add_parser("release-readiness").set_defaults(
        func=handle_report_release_readiness
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    func: Callable[[argparse.Namespace], int] = args.func
    return func(args)


if __name__ == "__main__":
    raise SystemExit(main())
