from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


@dataclass(frozen=True)
class MarkdownLink:
    source_path: Path
    label: str
    target: str


def iter_markdown_links(text: str) -> list[tuple[str, str]]:
    return [(match.group(1), match.group(2)) for match in LINK_RE.finditer(text)]


def collect_markdown_links(root: Path) -> list[MarkdownLink]:
    links: list[MarkdownLink] = []
    for path in sorted(root.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for label, target in iter_markdown_links(text):
            links.append(MarkdownLink(source_path=path, label=label, target=target))
    return links
