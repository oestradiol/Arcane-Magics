#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

BASELINES = {
    'always_act': lambda row: 'ACT',
    'always_gather': lambda row: 'GATHER',
    'always_withhold': lambda row: 'WITHHOLD',
    'always_stop': lambda row: 'STOP',
}

def evaluate(rows, predictor):
    correct = sum(predictor(r) == r['gold'] for r in rows)
    return {'n': len(rows), 'correct': correct, 'accuracy': correct / len(rows) if rows else 0.0}

def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name('dev.jsonl')
    rows = [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
    print(json.dumps({k:evaluate(rows,v) for k,v in BASELINES.items()}, indent=2, sort_keys=True))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
