from __future__ import annotations

from pathlib import Path, PurePosixPath

IGNORED_PATH_PARTS = {
    ".git",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
}

IGNORED_SUFFIXES = {
    ".pyc",
}

IGNORED_EXACT_FILENAMES = {
    ".DS_Store",
}

IGNORED_PREFIXES = (
    "tools/out/",
)


def is_truth_file(rel: str) -> bool:
    if any(rel.startswith(prefix) for prefix in IGNORED_PREFIXES):
        return False

    path = PurePosixPath(rel)
    if any(part in IGNORED_PATH_PARTS for part in path.parts):
        return False

    if path.suffix in IGNORED_SUFFIXES:
        return False

    if path.name in IGNORED_EXACT_FILENAMES:
        return False

    return True


def iter_truth_files(repo_root: Path) -> list[str]:
    files: list[str] = []
    for path in sorted(repo_root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(repo_root).as_posix()
        if is_truth_file(rel):
            files.append(rel)
    return files
