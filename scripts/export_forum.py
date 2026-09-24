#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "preprints" / "lesswrong" / "generated"

BOX = {
    "claimbox": "Claim boundary",
    "readerbox": "Reader reconstruction",
    "devilbox": "Devil's Audit",
    "mythosbox": "Mythos register",
    "translationbox": "Vocabulary bridge",
    "center": "",
    "definition": "Definition",
    "proposition": "Proposition",
    "theorem": "Theorem",
    "corollary": "Corollary",
    "proof": "Proof",
    "example": "Example",
    "remark": "Remark",
    "hypothesis": "Hypothesis",
    "criterion": "Criterion",
    "readercheck": "Reader reconstruction",
    "statusnote": "Status",
    "devilaudit": "Devil's Audit",
    "mythosregister": "Mythos register",
    "cruxbox": "Crux / falsifier",
    "tcolorbox": "Claim/register note",
    "thebibliography": "",
}


def normalize_forum_markdown(body: str) -> str:
    for cls, title in BOX.items():
        body = re.sub(
            rf'<div class="{re.escape(cls)}">\s*',
            (f"**{title}.**\n\n" if title else ""),
            body,
        )

    body = re.sub(r"\\operatorname\{([^{}]+)\}", r"\\mathrm{\1}", body)
    body = re.sub(r"\\label\{[^{}]+\}", "", body)
    body = re.sub(
        r'<a href="#[^"]+" data-reference-type="(?:eqref|ref)" data-reference="[^"]+">([^<]*)</a>',
        r"\1",
        body,
    )
    body = re.sub(r"\\(?:eqref|ref)\{[^{}]+\}", "the referenced result", body)
    body = re.sub(r"\[(?:eq|sec|prop|fig|tab):[^\]]+\]", "the referenced result", body)
    body = re.sub(
        r"^\*\*(?:Definition|Proposition|Theorem|Corollary|Example|Remark|Hypothesis|Criterion)\.\*\*\s*$",
        "",
        body,
        flags=re.MULTILINE,
    )
    body = re.sub(r"</?div[^>]*>", "", body)
    body = re.sub(r"</?figure[^>]*>", "", body)
    body = re.sub(r"<figcaption>(.*?)</figcaption>", r"*\1*", body, flags=re.DOTALL)
    body = re.sub(r"(^|\n)99(\n|$)", r"\1\2", body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip() + "\n"
    return body


def export_one(name: str) -> Path:
    src = ROOT / "monographs" / name / "main.tex"
    dst = OUT / f"{name.lower()}.md"
    subprocess.run(
        ["pandoc", "-f", "latex", "-t", "gfm", "--wrap=none", str(src), "-o", str(dst)],
        check=True,
    )
    body = normalize_forum_markdown(dst.read_text(encoding="utf-8", errors="replace"))
    pre = (
        "**Epistemic status:** Discussion draft. Claim strength and register follow "
        "the manuscript. Project vocabulary may be replaced by the ordinary referent "
        "without changing the claim. Verify equations, citations, and footnotes against "
        "the paper before posting.\n\n"
    )
    dst.write_text(pre + body, encoding="utf-8")
    return dst


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ["01_OFE", "02_ECLIPSIS", "03_ARCANE_MAGICS", "04_VENUS"]:
        print(export_one(name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
