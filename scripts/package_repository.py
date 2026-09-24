#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import fnmatch
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / (ROOT.name + ".zip")
SKIP_PATTERNS = [
    "*.aux", "*.log", "*.out", "*.toc", "*.fls", "*.fdb_latexmk",
    "*.bcf", "*.run.xml", "main.pdf", "*-SAVE-ERROR", "*.synctex.gz",
    "__pycache__/*", "*.pyc", ".pytest_cache/*", ".git/*",
]


def skip(rel: Path) -> bool:
    s = rel.as_posix()
    return any(
        fnmatch.fnmatch(rel.name, pattern) or fnmatch.fnmatch(s, pattern)
        for pattern in SKIP_PATTERNS
    )


with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
    for file in sorted(ROOT.rglob("*")):
        if not file.is_file():
            continue
        rel = file.relative_to(ROOT)
        if skip(rel):
            continue
        archive.write(file, Path(ROOT.name) / rel)

digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
sha = OUT.with_suffix(OUT.suffix + ".sha256")
sha.write_text(f"{digest}  {OUT.name}\n", encoding="utf-8")
print(OUT)
print(sha)
