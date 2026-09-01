from __future__ import annotations

import re
from pathlib import Path

from research_tools.models.reports import ValidationResult
from research_tools.paths import RepoPaths

VERSION_RE = re.compile(r'^version:\s*"([^"]+)"\s*$', re.MULTILINE)
DATE_RE = re.compile(r'^date-released:\s*"([^"]+)"\s*$', re.MULTILINE)
PYPROJECT_VERSION_RE = re.compile(r'^version\s*=\s*"([^"]+)"\s*$', re.MULTILINE)
INIT_VERSION_RE = re.compile(r'__version__\s*=\s*"([^"]+)"')
CHANGELOG_VERSION_RE = re.compile(r"^## `([^`]+)` - ([0-9]{4}-[0-9]{2}-[0-9]{2})$", re.MULTILINE)
ROOT_README_SNAPSHOT_RE = re.compile(
    r"(?:\*\*(?:Hosted|Current) snapshot:\*\*|(?:Hosted|Current) snapshot:)"
    r"\s+\*\*`([^`]+)`\*\*\s+dated\s+"
    r"\*\*`?([0-9-]+)`?\*\*\."
)
SUF_README_SNAPSHOT_RE = ROOT_README_SNAPSHOT_RE
SUF_STATUS_RE = re.compile(
    r"\*\*`([^`]+)`\*\*\s+(?:still\s+)?names the dated hosted snapshot in this tree "
    r"\(\*\*([0-9-]+)\*\*\)\."
)
KNOWLEDGE_README_SNAPSHOT_RE = re.compile(r"- `([^`]+)` dated `([^`]+)`")
TOOLS_README_SNAPSHOT_RE = re.compile(r"Current snapshot: `([^`]+)` dated `([^`]+)`\.")


def _safe_read_text(path: Path) -> tuple[str | None, str | None]:
    if not path.exists():
        return None, f"missing file: {path}"
    if not path.is_file():
        return None, f"not a regular file: {path}"
    return path.read_text(encoding="utf-8"), None


def _extract_required(pattern: re.Pattern[str], text: str, path: Path, field_name: str) -> tuple[str | None, str | None]:
    match = pattern.search(text)
    if not match:
        return None, f"{field_name} not found in {path}"
    return match.group(1), None


def _extract_changelog(path: Path) -> tuple[tuple[str, str] | None, str | None]:
    text, error = _safe_read_text(path)
    if error is not None:
        return None, error
    matches = CHANGELOG_VERSION_RE.findall(text)
    if not matches:
        return None, f"No released changelog section found in {path}"
    return matches[0], None


def _comparison(
    check_name: str,
    message: str,
    expected: str,
    found: str,
    path: Path | None = None,
) -> ValidationResult:
    status = "pass" if expected == found else "fail"
    return ValidationResult(
        check_name=check_name,
        status=status,
        message=message if status == "pass" else f"{message} Value mismatch.",
        path=str(path) if path else None,
        expected=expected,
        found=found,
    )


def _failure(check_name: str, path: Path, message: str, expected: str) -> ValidationResult:
    return ValidationResult(
        check_name=check_name,
        status="fail",
        message=message,
        path=str(path),
        expected=expected,
        found=message,
    )


def _normalize_version(value: str) -> str:
    return value[1:] if value.startswith("v") else value


def validate_versions(paths: RepoPaths) -> list[ValidationResult]:
    results: list[ValidationResult] = []

    umbrella_cff = paths.research_root / "CITATION.cff"
    suf_cff = paths.suf_root / "CITATION.cff"
    knowledge_cff = paths.knowledge_root / "CITATION.cff"
    tools_pyproject = paths.tools_root / "pyproject.toml"
    tools_init = paths.tools_root / "src" / "research_tools" / "__init__.py"
    root_readme = paths.research_root / "README.md"
    suf_readme = paths.suf_root / "README.md"
    suf_status = paths.suf_root / "docs" / "project-status.md"
    knowledge_readme = paths.knowledge_root / "README.md"
    tools_readme = paths.tools_root / "README.md"
    tools_changelog = paths.tools_root / "CHANGELOG.md"
    root_changelog = paths.research_root / "CHANGELOG.md"
    suf_changelog = paths.suf_root / "CHANGELOG.md"
    knowledge_changelog = paths.knowledge_root / "CHANGELOG.md"

    umbrella_text, umbrella_text_error = _safe_read_text(umbrella_cff)
    suf_text, suf_text_error = _safe_read_text(suf_cff)
    knowledge_text, knowledge_text_error = _safe_read_text(knowledge_cff)
    pyproject_text, pyproject_text_error = _safe_read_text(tools_pyproject)
    init_text, init_text_error = _safe_read_text(tools_init)

    umbrella_version, umbrella_version_error = _extract_required(VERSION_RE, umbrella_text, umbrella_cff, "version") if umbrella_text_error is None else (None, umbrella_text_error)
    umbrella_date, umbrella_date_error = _extract_required(DATE_RE, umbrella_text, umbrella_cff, "date-released") if umbrella_text_error is None else (None, umbrella_text_error)
    suf_version, suf_version_error = _extract_required(VERSION_RE, suf_text, suf_cff, "version") if suf_text_error is None else (None, suf_text_error)
    suf_date, suf_date_error = _extract_required(DATE_RE, suf_text, suf_cff, "date-released") if suf_text_error is None else (None, suf_text_error)
    knowledge_version, knowledge_version_error = _extract_required(VERSION_RE, knowledge_text, knowledge_cff, "version") if knowledge_text_error is None else (None, knowledge_text_error)
    knowledge_date, knowledge_date_error = _extract_required(DATE_RE, knowledge_text, knowledge_cff, "date-released") if knowledge_text_error is None else (None, knowledge_text_error)
    tools_version, tools_version_error = _extract_required(PYPROJECT_VERSION_RE, pyproject_text, tools_pyproject, "version") if pyproject_text_error is None else (None, pyproject_text_error)
    tools_init_version, tools_init_version_error = _extract_required(INIT_VERSION_RE, init_text, tools_init, "__version__") if init_text_error is None else (None, init_text_error)

    prerequisites = [
        ("versions-umbrella-citation-version", umbrella_cff, umbrella_version_error, "parseable version in umbrella CITATION.cff"),
        ("versions-umbrella-citation-date", umbrella_cff, umbrella_date_error, "parseable date-released in umbrella CITATION.cff"),
        ("versions-suf-citation-version", suf_cff, suf_version_error, "parseable version in SUF CITATION.cff"),
        ("versions-suf-citation-date", suf_cff, suf_date_error, "parseable date-released in SUF CITATION.cff"),
        ("versions-knowledge-citation-version", knowledge_cff, knowledge_version_error, "parseable version in Knowledge CITATION.cff"),
        ("versions-knowledge-citation-date", knowledge_cff, knowledge_date_error, "parseable date-released in Knowledge CITATION.cff"),
        ("versions-tools-pyproject-version", tools_pyproject, tools_version_error, "parseable version in tools pyproject"),
        ("versions-tools-init-version", tools_init, tools_init_version_error, "parseable __version__ in tools package init"),
    ]
    for check_name, path, error, expected in prerequisites:
        if error is not None:
            results.append(_failure(check_name, path, error, expected))

    root_readme_text, root_readme_error = _safe_read_text(root_readme)
    suf_readme_text, suf_readme_error = _safe_read_text(suf_readme)
    suf_status_text, suf_status_error = _safe_read_text(suf_status)
    knowledge_readme_text, knowledge_readme_error = _safe_read_text(knowledge_readme)
    tools_readme_text, tools_readme_error = _safe_read_text(tools_readme)

    for check_name, path, error, expected in [
        ("versions-root-readme-readable", root_readme, root_readme_error, "readable umbrella README"),
        ("versions-suf-readme-readable", suf_readme, suf_readme_error, "readable SUF README"),
        ("versions-suf-status-readable", suf_status, suf_status_error, "readable SUF project-status"),
        ("versions-knowledge-readme-readable", knowledge_readme, knowledge_readme_error, "readable Knowledge README"),
        ("versions-tools-readme-readable", tools_readme, tools_readme_error, "readable tools README"),
    ]:
        if error is not None:
            results.append(_failure(check_name, path, error, expected))

    if root_readme_error is None and umbrella_version_error is None and umbrella_date_error is None:
        root_readme_match = ROOT_README_SNAPSHOT_RE.search(root_readme_text)
        if not root_readme_match:
            results.append(_failure("versions-umbrella-readme", root_readme, "Umbrella README snapshot line not found.", "matching snapshot line in README"))
        else:
            results.append(_comparison("versions-umbrella-readme-version", "Umbrella README version matches umbrella citation.", umbrella_version, _normalize_version(root_readme_match.group(1)), root_readme))
            results.append(_comparison("versions-umbrella-readme-date", "Umbrella README date matches umbrella citation.", umbrella_date, root_readme_match.group(2), root_readme))

    if suf_readme_error is None and suf_version_error is None and suf_date_error is None:
        suf_readme_match = SUF_README_SNAPSHOT_RE.search(suf_readme_text)
        if not suf_readme_match:
            results.append(_failure("versions-suf-readme", suf_readme, "SUF README snapshot line not found.", "matching snapshot line in SUF README"))
        else:
            results.append(_comparison("versions-suf-readme-version", "SUF README version matches SUF citation.", suf_version, _normalize_version(suf_readme_match.group(1)), suf_readme))
            results.append(_comparison("versions-suf-readme-date", "SUF README date matches SUF citation.", suf_date, suf_readme_match.group(2), suf_readme))

    if suf_status_error is None and suf_version_error is None and suf_date_error is None:
        suf_status_match = SUF_STATUS_RE.search(suf_status_text)
        if not suf_status_match:
            results.append(_failure("versions-suf-status", suf_status, "SUF project-status version line not found.", "matching version line in SUF project-status"))
        else:
            results.append(_comparison("versions-suf-status-version", "SUF project-status version matches SUF citation.", suf_version, _normalize_version(suf_status_match.group(1)), suf_status))
            results.append(_comparison("versions-suf-status-date", "SUF project-status date matches SUF citation.", suf_date, suf_status_match.group(2), suf_status))

    if knowledge_readme_error is None and knowledge_version_error is None and knowledge_date_error is None:
        knowledge_readme_match = KNOWLEDGE_README_SNAPSHOT_RE.search(knowledge_readme_text)
        if not knowledge_readme_match:
            results.append(_failure("versions-knowledge-readme", knowledge_readme, "Knowledge README snapshot line not found.", "matching snapshot line in Knowledge README"))
        else:
            results.append(_comparison("versions-knowledge-readme-version", "Knowledge README version matches Knowledge citation.", knowledge_version, _normalize_version(knowledge_readme_match.group(1)), knowledge_readme))
            results.append(_comparison("versions-knowledge-readme-date", "Knowledge README date matches Knowledge citation.", knowledge_date, knowledge_readme_match.group(2), knowledge_readme))

    if tools_readme_error is None and tools_version_error is None and umbrella_date_error is None:
        tools_readme_match = TOOLS_README_SNAPSHOT_RE.search(tools_readme_text)
        if not tools_readme_match:
            results.append(_failure("versions-tools-readme", tools_readme, "Tools README snapshot line not found.", "matching snapshot line in tools README"))
        else:
            results.append(_comparison("versions-tools-readme-version", "Tools README version matches tools metadata.", tools_version, tools_readme_match.group(1), tools_readme))
            results.append(_comparison("versions-tools-readme-date", "Tools README date matches umbrella release date.", umbrella_date, tools_readme_match.group(2), tools_readme))

    if tools_version_error is None and tools_init_version_error is None:
        results.append(_comparison("versions-tools-metadata-sync", "Tools pyproject and package __init__ versions match.", tools_version, tools_init_version, tools_pyproject))

    for check_prefix, version, version_error, date, date_error, changelog_path in (
        ("versions-umbrella-changelog", umbrella_version, umbrella_version_error, umbrella_date, umbrella_date_error, root_changelog),
        ("versions-suf-changelog", suf_version, suf_version_error, suf_date, suf_date_error, suf_changelog),
        ("versions-knowledge-changelog", knowledge_version, knowledge_version_error, knowledge_date, knowledge_date_error, knowledge_changelog),
        ("versions-tools-changelog", tools_version, tools_version_error, umbrella_date, umbrella_date_error, tools_changelog),
    ):
        if version_error is not None or date_error is not None:
            continue
        changelog, changelog_error = _extract_changelog(changelog_path)
        if changelog_error is not None:
            results.append(_failure(f"{check_prefix}-readable", changelog_path, changelog_error, "readable changelog with at least one released section"))
            continue
        changelog_version, changelog_date = changelog
        results.append(_comparison(f"{check_prefix}-version", "Top changelog release version matches package version.", version, _normalize_version(changelog_version), changelog_path))
        results.append(_comparison(f"{check_prefix}-date", "Top changelog release date matches package date.", date, changelog_date, changelog_path))

    return results
