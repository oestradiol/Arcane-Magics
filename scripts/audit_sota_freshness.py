#!/usr/bin/env python3
from __future__ import annotations

from datetime import date
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'docs' / 'SOTA_WATCH_STATE.json'

def main() -> int:
    data=json.loads(STATE.read_text(encoding='utf-8'))
    today=date.fromisoformat(os.environ.get('VENUS_AUDIT_DATE', date.today().isoformat()))
    errors=[]
    warnings=[]
    for row in data.get('entries', []):
        checked=date.fromisoformat(row['last_checked'])
        age=(today-checked).days
        limit=int(row['stale_after_days'])
        if age > limit:
            errors.append(f"{row['id']}: stale by {age-limit}d (age={age}d, limit={limit}d)")
        if not row.get('sources'):
            errors.append(f"{row['id']}: no primary/source URL registered")
        if not row.get('distinction'):
            errors.append(f"{row['id']}: missing Venus-relevant distinction")
        if row.get('status') == 'RECONCILE':
            warnings.append(f"{row['id']}: reconciliation queue remains open")
    if warnings:
        print('SOTA RECONCILIATION QUEUE')
        for w in warnings: print('- '+w)
    if errors:
        print('SOTA FRESHNESS AUDIT FAIL')
        for e in errors: print('- '+e)
        return 1
    print(f"SOTA FRESHNESS AUDIT PASS ({len(data.get('entries', []))} entries; date={today})")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
