from __future__ import annotations

import re
from pathlib import Path

from research_tools.models.reports import ValidationResult

PLACEHOLDER_RE = re.compile(r"\b(TODO|FIXME)\b")
ABSOLUTE_PATH_RE = re.compile(r"(/home/|/Users/|file://|vscode://)")
CROSS_REPO_RE = re.compile(r"\b(AKS|Dotfiles|Aistra|Internal/)\b")
IGNORED_DIR_NAMES = {".venv", ".pytest_cache", ".ruff_cache", "__pycache__", "out"}
# knowledge/map/ atlas nodes may reference "AKS" etc. as domain topics, not as cross-repo leaks
CROSS_REPO_EXCLUDED_PREFIXES = ("knowledge/",)


def validate_release_hygiene(research_root: Path) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    placeholder_hits: list[str] = []
    cross_repo_hits: list[str] = []
    absolute_path_hits: list[str] = []

    for path in research_root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIR_NAMES for part in path.parts):
            continue
        if path.suffix not in {".md", ".py", ".toml", ".cff"}:
            continue
        text = path.read_text(encoding="utf-8")
        if path.suffix in {".md", ".toml", ".cff"} and PLACEHOLDER_RE.search(text):
            placeholder_hits.append(str(path))
        if path.suffix in {".md", ".toml", ".cff"} and CROSS_REPO_RE.search(text):
            rel = path.relative_to(research_root).as_posix()
            if not any(rel.startswith(p) for p in CROSS_REPO_EXCLUDED_PREFIXES):
                cross_repo_hits.append(str(path))
        if path.suffix in {".md", ".toml", ".cff"} and ABSOLUTE_PATH_RE.search(text):
            absolute_path_hits.append(str(path))

    checks = (
        (
            "release-hygiene-placeholders",
            placeholder_hits,
            "No unresolved TODO/FIXME residue remains in public repo files.",
            "Unresolved TODO/FIXME residue remains in public repo files.",
        ),
        (
            "release-hygiene-cross-repo-refs",
            cross_repo_hits,
            "No cross-repo references (AKS, Dotfiles, Aistra, Internal/) leak into the Research repo.",
            "Cross-repo references leak into the Research repo.",
        ),
        (
            "release-hygiene-absolute-paths",
            absolute_path_hits,
            "No local absolute filesystem paths remain in public repo prose or metadata.",
            "Local absolute filesystem paths remain in public repo prose or metadata.",
        ),
    )

    for check_name, hits, pass_message, fail_message in checks:
        results.append(
            ValidationResult(
                check_name=check_name,
                status="pass" if not hits else "fail",
                message=pass_message if not hits else fail_message,
                found=", ".join(hits) if hits else "none",
            )
        )

    return results
