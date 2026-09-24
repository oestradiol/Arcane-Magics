#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'docs'/'CONSTRUCT_DISPOSITIONS.json'
ALLOWED={'LIVE_RESIDUAL','PARTIALLY_REDUCIBLE','MATURELY_SUBSUMED_AT_T','NO_LONGER_REQUIRED_LIVE','HISTORICAL_ONLY','FAILED_IMPLEMENTATION','WITHHOLD','OPEN_FRONTIER'}

def main() -> int:
    data=json.loads(PATH.read_text(encoding='utf-8'))
    errors=[]
    seen=set()
    for row in data.get('dispositions', []):
        cid=row.get('id')
        if not cid or cid in seen: errors.append(f'invalid/duplicate construct id: {cid}')
        seen.add(cid)
        if row.get('status') not in ALLOWED: errors.append(f'{cid}: invalid status {row.get("status")}')
        if row.get('genealogy_preserved') is not True: errors.append(f'{cid}: genealogy must remain preserved')
        for rel in row.get('evidence', []):
            if rel.startswith('issues/'): continue
            if not (ROOT/rel).exists(): errors.append(f'{cid}: evidence path missing: {rel}')
        if row.get('status') in {'MATURELY_SUBSUMED_AT_T','NO_LONGER_REQUIRED_LIVE'}:
            if not row.get('mature_substitute'): errors.append(f'{cid}: subsumed/retired status requires mature_substitute')
            if row.get('independent_residual') not in {'NONE','SUBSUMED'}: errors.append(f'{cid}: retired status cannot retain an untyped residual')
    if errors:
        print('CONSTRUCT DISPOSITION AUDIT FAIL')
        for e in errors: print('- '+e)
        return 1
    print(f'CONSTRUCT DISPOSITION AUDIT PASS ({len(seen)} constructs)')
    return 0

if __name__=='__main__': raise SystemExit(main())
