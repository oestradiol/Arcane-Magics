#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {'.git', 'arxiv_packages', 'tex_bundles', 'archaeology', 'current-developmental-receipts'}
MATH_COMMAND = re.compile(r'\\(boxed|mathcal|operatorname|begin|end|leftrightarrow|rightarrow|nrightarrow|Gamma|Delta|delta|rho|Sigma|Phi|neq|sim|quad|land)\\b')
LINK = re.compile(r'\\[[^\\]]+\\]\\(([^)]+)\\)')

def skipped(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)

def normalize_target(md: Path, raw: str) -> Path:
    raw = raw.split('#', 1)[0].split('?', 1)[0]
    if raw.startswith('/'):
        return ROOT / raw.lstrip('/')
    return (md.parent / raw).resolve()

def inspect(md: Path) -> list[str]:
    errors: list[str] = []
    text = md.read_text(encoding='utf-8', errors='replace')
    lines = text.splitlines()
    in_fence = False
    display_dollar_open = False

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        fence = re.match(r'^\\s*```([A-Za-z0-9_-]*)\\s*$', line)
        if fence:
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        dollars = line.count('$')
        in_display_here = display_dollar_open or dollars > 0
        if dollars % 2 == 1:
            display_dollar_open = not display_dollar_open
        if stripped == '[' and i < len(lines):
            nxt = lines[i].strip()
            if MATH_COMMAND.search(nxt) or re.search(r'\\b(mathcal|operatorname|Gamma|Delta)\\b', nxt):
                errors.append(f'{md.relative_to(ROOT)}:{i}: malformed pseudo-math block; use ```math or $$')
        if stripped in {'\\\\[', '\\\\]'}:
            errors.append(f'{md.relative_to(ROOT)}:{i}: use ```math or $$, not \\[ / \\]')
        scrubbed = re.sub(r'`[^`]*`', '', line)
        scrubbed = re.sub(r'\\$`.*?`\\$', '', scrubbed)
        scrubbed = re.sub(r'\\$[^$]+\\$', '', scrubbed)
        if not in_display_here and MATH_COMMAND.search(scrubbed):
            errors.append(f'{md.relative_to(ROOT)}:{i}: TeX command appears outside GitHub math/code')

    if in_fence:
        errors.append(f'{md.relative_to(ROOT)}: unclosed fenced code block')
    if display_dollar_open:
        errors.append(f'{md.relative_to(ROOT)}: unclosed $$ display-math block')

    for match in LINK.finditer(text):
        raw = match.group(1).strip().strip('<>')
        if not raw or raw.startswith(('http://', 'https://', 'mailto:', '#')):
            continue
        target = normalize_target(md, raw)
        if not target.exists():
            errors.append(f'{md.relative_to(ROOT)}: broken relative link {raw!r}')

    return errors

def public_surface(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    parts = rel.parts
    if len(parts) == 1:
        return True
    if parts[0] in {'docs', 'review', 'licenses'}:
        return True
    if parts[0] == 'monographs' and path.name == 'README.md':
        return True
    if parts[0] == 'preprints' and parts[1] == 'lesswrong':
        return True
    if rel.as_posix() in {
        'prototype/README.md',
        'prototype/CURRENT_STATE.md',
        'prototype/stable-executable/README.md',
    }:
        return True
    return False


def main() -> int:
    files = [p for p in ROOT.rglob('*.md') if not skipped(p) and public_surface(p)]
    errors: list[str] = []
    for md in files:
        errors.extend(inspect(md))
    if errors:
        print('GITHUB MARKDOWN LINT FAIL')
        for error in errors:
            print('- ' + error)
        return 1
    print(f'GITHUB MARKDOWN LINT PASS ({len(files)} Markdown files)')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
