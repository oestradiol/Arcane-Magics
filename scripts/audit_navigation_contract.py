#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / 'README.md'

REQUIRED_DIRECT = {
    'docs/START_HERE.md': 'start-here hub',
    'kernel/CURRENT_STATE.md': 'current authority',
    'docs/EARNED_MILESTONES.md': 'earned results',
    'docs/TESTS.md': 'tests/evidence',
    'docs/EVALUATION_CONSTITUTION.md': 'evaluation',
    'docs/FRONTIER_RESEARCH.md': 'frontier program',
}

REQUIRED_START_HERE = {
    '../kernel/CURRENT_STATE.md': 'current authority',
    'EARNED_MILESTONES.md': 'earned results',
    'TESTS.md': 'tests/evidence',
    'EVALUATION_CONSTITUTION.md': 'evaluation',
    'PUBLIC_VALUE.md': 'plain-language value',
    '../provenance/DEVELOPMENTAL_LINEAGE.md': 'lineage',
}

LINK = re.compile(r'\[[^\]]+\]\(([^)]+)\)')

def link_paths(path: Path) -> set[str]:
    text = path.read_text(encoding='utf-8', errors='replace')
    return {m.group(1).split('#', 1)[0] for m in LINK.finditer(text)}

def main() -> int:
    errors: list[str] = []
    if not README.exists():
        print('NAVIGATION CONTRACT FAIL: missing README.md')
        return 1
    start = ROOT / 'docs' / 'START_HERE.md'
    if not start.exists():
        errors.append('missing docs/START_HERE.md')
    readme_links = link_paths(README)
    for target, purpose in REQUIRED_DIRECT.items():
        if target not in readme_links:
            errors.append(f'README missing direct {purpose} route: {target}')
    if start.exists():
        start_links = link_paths(start)
        for target, purpose in REQUIRED_START_HERE.items():
            if target not in start_links:
                errors.append(f'START_HERE missing {purpose} route: {target}')

    # The README must keep the shortest reproduction commands discoverable.
    readme_text = README.read_text(encoding='utf-8', errors='replace')
    for token in ('python -m kernel.runtime.current', 'make audit'):
        if token not in readme_text:
            errors.append(f'README missing reproduction command: {token}')

    # Test hub must expose the control matrices directly.
    tests = ROOT / 'docs' / 'TESTS.md'
    if tests.exists():
        tlinks = link_paths(tests)
        for target in ('../provenance/HISTORICAL_DISTINCTION_TEST_MATRIX.json', 'TEST_COVERAGE_MATRIX.md'):
            if target not in tlinks:
                errors.append(f'TESTS hub missing control surface: {target}')
    else:
        errors.append('missing docs/TESTS.md')

    if errors:
        print('NAVIGATION CONTRACT FAIL')
        for error in errors:
            print('- ' + error)
        return 1
    print('NAVIGATION CONTRACT PASS')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
