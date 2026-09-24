#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
STATUS=ROOT/'kernel'/'custody'/'EDU16_CUSTODY_STATUS.json'

def main() -> int:
    data=json.loads(STATUS.read_text(encoding='utf-8'))
    errors=[]
    auth=data['authority']
    current=(ROOT/'kernel'/'CURRENT_STATE.md').read_text(encoding='utf-8', errors='replace')
    receipt=(ROOT/'provenance'/'developmental'/'EDU'/'EDU16_WORLD_FEED_SAMPLING_POLICY_RESULT.md').read_text(encoding='utf-8', errors='replace')
    for token in (str(auth['records']),auth['head'],auth['sha256'],auth['verdict']):
        if token not in current: errors.append('CURRENT_STATE missing EDU16 custody token: '+token)
        if token not in receipt: errors.append('EDU16 receipt missing custody token: '+token)
    exe=data['executable_custody']
    if exe.get('git_replayable_runtime') is not False:
        errors.append('EDU16 must not be marked Git-replayable without exact runner/journal custody')
    if data['runtime_base'].get('id') != 'IG10' or data['runtime_base'].get('git_reconstructible') is not True:
        errors.append('IG10 replayable runtime base boundary lost')
    recovery=ROOT/data['evidence_custody']['recovery_manifest']
    if not recovery.exists(): errors.append('recovery manifest missing')
    if errors:
        print('EDU16 CUSTODY BOUNDARY FAIL')
        for e in errors: print('- '+e)
        return 1
    print('EDU16 CUSTODY BOUNDARY PASS: exact evidence / non-replayable EDU16 runtime remain distinct')
    return 0

if __name__=='__main__': raise SystemExit(main())
