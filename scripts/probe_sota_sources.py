#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'docs'/'SOTA_WATCH_STATE.json'
MAX_BYTES=1_048_576

def probe_url(url: str, *, opener=urlopen, max_bytes: int=MAX_BYTES) -> dict:
    req=Request(url,headers={'User-Agent':'Venus-Minerva-SOTA-Probe/0.1 (+https://github.com/oestradiol/Venus-Minerva)'})
    try:
        with opener(req,timeout=20) as response:
            body=response.read(max_bytes+1)
            truncated=len(body)>max_bytes
            body=body[:max_bytes]
            headers=response.headers
            return {
                'url':url,
                'ok':True,
                'status':getattr(response,'status',None),
                'final_url':response.geturl(),
                'etag':headers.get('ETag'),
                'last_modified':headers.get('Last-Modified'),
                'content_type':headers.get('Content-Type'),
                'observed_bytes':len(body),
                'truncated':truncated,
                'body_sha256':hashlib.sha256(body).hexdigest(),
            }
    except Exception as exc:
        return {'url':url,'ok':False,'error_type':type(exc).__name__,'error':str(exc)[:500]}

def build_report(state: dict, *, opener=urlopen, observed_at: str|None=None) -> dict:
    entries=[]
    for row in state.get('entries',[]):
        sources=[probe_url(url,opener=opener) for url in row.get('sources',[])]
        entries.append({
            'id':row.get('id'),
            'area':row.get('area'),
            'declared_last_checked':row.get('last_checked'),
            'declared_status':row.get('status'),
            'sources':sources,
            'all_reachable':all(s.get('ok') for s in sources) if sources else False,
        })
    return {
        'schema':'Venus.SOTASourceProbe.v0.1',
        'observed_at':observed_at or datetime.now(timezone.utc).isoformat(),
        'authority':False,
        'interpretation':'Observation/fingerprint only. Source change or reachability does not establish truth, validation, credit, or automatic repository reconciliation.',
        'entries':entries,
    }

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument('--state',default=str(STATE))
    p.add_argument('--output',default='SOTA_SOURCE_PROBE.json')
    args=p.parse_args()
    state=json.loads(Path(args.state).read_text(encoding='utf-8'))
    report=build_report(state)
    Path(args.output).write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    reachable=sum(e['all_reachable'] for e in report['entries'])
    print(f'SOTA SOURCE PROBE: {reachable}/{len(report["entries"])} entries fully reachable; authority=false')
    return 0

if __name__=='__main__': raise SystemExit(main())
