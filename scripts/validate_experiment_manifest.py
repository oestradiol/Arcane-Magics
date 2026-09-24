#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

REQUIRED_CONDITIONS = {'A','B','C','D','E'}

def validate(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get('schema') != 'Venus.MatchedExperimentManifest.v0.1':
        errors.append('wrong schema')
    ids = {c.get('id') for c in data.get('conditions', [])}
    missing = REQUIRED_CONDITIONS - ids
    if missing:
        errors.append('missing conditions: ' + ','.join(sorted(missing)))
    shared = data.get('shared_condition', {})
    for key in ('token_budget','wall_clock_budget_seconds','monetary_budget_usd','retries'):
        if key not in shared:
            errors.append('missing shared budget field: ' + key)
    prereg = data.get('preregistration', {})
    if prereg.get('no_post_exposure_repair') is not True:
        errors.append('no_post_exposure_repair must be true')
    for key in ('success','failure','withhold','primary_metrics'):
        if key not in prereg:
            errors.append('missing preregistration field: ' + key)
    evaluator = data.get('evaluator', {})
    if evaluator.get('owner') != 'INDEPENDENT_EVALUATOR':
        errors.append('evaluator owner must be INDEPENDENT_EVALUATOR')
    if evaluator.get('separated_from_execution') is not True:
        errors.append('evaluator must be separated from execution')
    custody = data.get('custody', {})
    if custody.get('negative_results_retained') is not True:
        errors.append('negative results must be retained')
    if data.get('promotion_authority') is not False:
        errors.append('experiment manifest cannot self-grant promotion authority')
    return errors

def main() -> int:
    if len(sys.argv) != 2:
        print('usage: validate_experiment_manifest.py PATH.json')
        return 2
    path=Path(sys.argv[1])
    data=json.loads(path.read_text(encoding='utf-8'))
    errors=validate(data)
    if errors:
        print('EXPERIMENT MANIFEST FAIL')
        for e in errors:
            print('- '+e)
        return 1
    print('EXPERIMENT MANIFEST PASS')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
