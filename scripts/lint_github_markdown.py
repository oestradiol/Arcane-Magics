#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]

EVIDENCE_DIRS = {"provenance"}
GENERATED_FORUM = ("preprints", "lesswrong", "generated")

# Full LaTeX remains legal in monograph .tex sources. These checks apply to
# reader-facing Markdown rendered by GitHub/forum surfaces.
UNSUPPORTED_PUBLIC_MATH = re.compile(
    r"\\operatorname\b|\\label\s*\{|\\eqref\s*\{|\\ref\s*\{"
)
PANDOC_RESIDUE = re.compile(
    r'data-reference-type=|data-reference=|<div\b|</div>|<figure\b|</figure>|<figcaption\b|</figcaption>',
    re.I,
)
ORPHAN_THEOREM_LABEL = re.compile(
    r"^\*\*(Definition|Proposition|Theorem|Corollary|Example|Remark|Hypothesis|Criterion)\.\*\*\s*$"
)
TEX_OUTSIDE_MATH = re.compile(
    r"\\(boxed|mathcal|mathrm|mathsf|text|begin|end|leftrightarrow|rightarrow|Rightarrow|Gamma|Delta|rho|Sigma|Phi|neq|sim|quad|land)\b"
)
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def is_evidence(path: Path) -> bool:
    parts = set(path.relative_to(ROOT).parts)
    return bool(parts & EVIDENCE_DIRS)


def is_public_surface(path: Path) -> bool:
    r = path.relative_to(ROOT)
    p = r.parts
    if len(p) == 1:
        return True
    if p[0] in {"docs", "review", "licenses"}:
        return True
    if p[0] == "monographs" and path.name == "README.md":
        return True
    if p[:3] == GENERATED_FORUM:
        return True
    if p[:2] == ("preprints", "lesswrong"):
        return True
    if r.as_posix() in {
        "kernel/README.md",
        "kernel/CURRENT_STATE.md",
        "kernel/WORLDMIND.md",
        "provenance/DEVELOPMENTAL_LINEAGE.md",
    }:
        return True
    return False


def normalize_target(md: Path, raw: str) -> Path:
    raw = unquote(raw.strip().strip("<>"))
    raw = raw.split("#", 1)[0].split("?", 1)[0]
    if raw.startswith("/"):
        return ROOT / raw.lstrip("/")
    return (md.parent / raw).resolve()


def inspect_basic(md: Path) -> list[str]:
    errors: list[str] = []
    text = md.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    fence_open = False
    fence_start = 0

    for i, line in enumerate(lines, 1):
        if re.match(r"^\s*```", line):
            fence_open = not fence_open
            if fence_open:
                fence_start = i

    if fence_open:
        errors.append(f"{rel(md)}:{fence_start}: unclosed fenced block")

    if is_public_surface(md):
        for match in LINK.finditer(text):
            raw = match.group(1)
            if not raw or raw.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = normalize_target(md, raw)
            if not target.exists():
                errors.append(f"{rel(md)}: broken relative link {raw!r}")

    return errors


def inspect_public(md: Path) -> list[str]:
    errors: list[str] = []
    text = md.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    in_fence = False
    fence_lang = ""
    display_math = False

    for i, line in enumerate(lines, 1):
        fence = re.match(r"^\s*```([A-Za-z0-9_-]*)\s*$", line)
        if fence:
            if in_fence:
                in_fence = False
                fence_lang = ""
            else:
                in_fence = True
                fence_lang = fence.group(1).lower()
            continue

        if in_fence:
            if fence_lang == "math" and UNSUPPORTED_PUBLIC_MATH.search(line):
                errors.append(f"{rel(md)}:{i}: unsupported public math macro in math fence")
            continue

        generated_forum = md.relative_to(ROOT).parts[:3] == GENERATED_FORUM
        if generated_forum and PANDOC_RESIDUE.search(line):
            errors.append(f"{rel(md)}:{i}: raw Pandoc/HTML residue in generated forum export")

        if generated_forum and ORPHAN_THEOREM_LABEL.match(line.strip()):
            errors.append(f"{rel(md)}:{i}: orphan theorem-environment label")

        n_display = line.count("$$")
        active_math = display_math or n_display > 0
        if active_math and UNSUPPORTED_PUBLIC_MATH.search(line):
            errors.append(f"{rel(md)}:{i}: unsupported public math macro")
        if n_display % 2:
            display_math = not display_math

        if line.strip() in {r"\[", r"\]"}:
            errors.append(f"{rel(md)}:{i}: use $$ or a math fence, not \\[ / \\]")

        scrubbed = re.sub(r"`[^`]*`", "", line)
        scrubbed = re.sub(r"\$\$.*?\$\$", "", scrubbed)
        scrubbed = re.sub(r"\$[^$]+\$", "", scrubbed)
        if not display_math and TEX_OUTSIDE_MATH.search(scrubbed):
            errors.append(f"{rel(md)}:{i}: TeX command appears outside math/code")

    if display_math:
        errors.append(f"{rel(md)}: unclosed $$ display math")

    if md.relative_to(ROOT).parts[:3] == GENERATED_FORUM:
        if re.search(r"\[(?:eq|sec|prop|fig|tab):[^\]]+\]", text):
            errors.append(f"{rel(md)}: unresolved LaTeX cross-reference token remains")
        if re.search(r"(^|\n)99(\n|$)", text):
            errors.append(f"{rel(md)}: stray bibliography counter residue")

    return errors


def inspect_state_consistency() -> list[str]:
    errors: list[str] = []

    checks = {
        "monographs/04_VENUS/README.md": [
            ("EDU16", "Venus monograph README must name EDU16"),
        ],
        "kernel/CURRENT_STATE.md": [
            ("R226", "current state must expose R226 boundary"),
            ("IG10", "current state must expose IG10 ancestry"),
            ("EDU16", "current state must expose EDU16 head"),
        ],
        "provenance/DEVELOPMENTAL_LINEAGE.md": [
            ("R226", "lineage must expose R226"),
            ("IG10", "lineage must expose IG10"),
            ("EDU16", "lineage must expose EDU16"),
        ],
    }

    for path, required in checks.items():
        p = ROOT / path
        if not p.exists():
            errors.append(f"missing state surface {path}")
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for token, message in required:
            if token not in text:
                errors.append(f"{path}: {message}")

    vocab = (ROOT / "NxRxI_VOCABULARY_CENTER.md").read_text(encoding="utf-8", errors="replace")
    if "N x R x I = Name/Notation x Register x Index" in vocab:
        errors.append("NxRxI_VOCABULARY_CENTER.md: false NxRxI backronym")

    for p in ROOT.rglob("*.md"):
        if not is_public_surface(p):
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if "GitHub Models as the default reasoning carrier" in text or "openai/gpt-4.1" in text:
            errors.append(f"{rel(p)}: abandoned external-model controller language remains")

    return errors


def main() -> int:
    md_files = sorted(ROOT.rglob("*.md"))
    errors: list[str] = []

    for md in md_files:
        errors.extend(inspect_basic(md))
        if is_public_surface(md):
            errors.extend(inspect_public(md))

    errors.extend(inspect_state_consistency())

    if errors:
        print("MARKDOWN / READER-SURFACE AUDIT FAIL")
        for error in errors:
            print("- " + error)
        return 1

    public_count = sum(1 for p in md_files if is_public_surface(p))
    evidence_count = sum(1 for p in md_files if is_evidence(p))
    print(
        f"MARKDOWN / READER-SURFACE AUDIT PASS "
        f"({len(md_files)} Markdown files; {public_count} strict public surfaces; "
        f"{evidence_count} provenance files basic-checked)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
