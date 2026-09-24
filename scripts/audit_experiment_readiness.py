#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

REQUIRED_RUN_FIELDS = [
    ('base_model.provider', lambda d: d.get('base_model',{}).get('provider')),
    ('base_model.model', lambda d: d.get('base_model',{}).get('model')),
    ('base_model.snapshot', lambda d: d.get('base_model',{}).get('snapshot')),
    ('base_model.reasoning_effort', lambda d: d.get('base_model',{}).get('reasoning_effort')),
    ('task_surface.hidden_split_hash', lambda d: d.get('task_surface',{}).get('hidden_split_hash')),
    ('task_surface.contamination_status', lambda d: d.get('task_surface',{}).get('contamination_status') not in (None,'UNKNOWN') and d.get('task_surface',{}).get('contamination_status')),
    ('shared_condition.information_bundle_hash', lambda d: d.get('shared_condition',{}).get('information_bundle_hash')),
    ('shared_condition.token_budget', lambda d: d.get('shared_condition',{}).get('token_budget') is not None),
    ('shared_condition.wall_clock_budget_seconds', lambda d: d.get('shared_condition',{}).get('wall_clock_budget_seconds') is not None),
    ('shared_condition.monetary_budget_usd', lambda d: d.get('shared_condition',{}).get('monetary_budget_usd') is not None),
    ('evaluator.identity', lambda d: d.get('evaluator',{}).get('identity')),
    ('evaluator.version', lambda d: d.get('evaluator',{}).get('version')),
]

def missing_run_fields(data: dict) -> list[str]:
    return [name for name,getter in REQUIRED_RUN_FIELDS if not getter(data)]

def validate_readiness(data: dict) -> list[str]:
    errors=[]
    readiness=data.get('readiness',{})
    executable=readiness.get('executable')
    status=str(data.get('status',''))
    missing=missing_run_fields(data)
    if executable is True:
        if missing:
            errors.append('manifest marked executable with missing run fields: '+', '.join(missing))
        if 'PREFREEZE' in status or 'TEMPLATE' in status:
            errors.append('prefreeze/template manifest cannot be executable')
    else:
        if not missing and status not in {'RUN_READY','EXECUTABLE'}:
            errors.append('all required run fields are frozen but manifest is still typed non-executable')
        declared=set(readiness.get('missing',[]))
        if status.startswith('PREFREEZE') and not declared:
            errors.append('prefreeze manifest must declare its missing dependencies')
    if data.get('promotion_authority') is not False:
        errors.append('manifest may not self-grant promotion authority')
    return errors

def main() -> int:
    if len(sys.argv)!=2:
        print('usage: audit_experiment_readiness.py PATH.json')
        return 2
    data=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    errors=validate_readiness(data)
    if errors:
        print('EXPERIMENT READINESS AUDIT FAIL')
        for e in errors: print('- '+e)
        return 1
    print('EXPERIMENT READINESS AUDIT PASS')
    return 0

if __name__=='__main__': raise SystemExit(main())
