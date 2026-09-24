#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"docs/UX_BLIND_READER_PROTOCOL.json"
REQUIRED_IDS={f"UX{i:02d}" for i in range(1,11)}

def main() -> int:
    errors=[]
    if not PATH.exists():
        errors.append("missing UX blind-reader protocol")
        data={}
    else:
        data=json.loads(PATH.read_text(encoding="utf-8"))
    if data.get("schema")!="Venus.BlindReaderUXProtocol.v0.1":
        errors.append("wrong UX protocol schema")
    if data.get("entrypoint")!="README.md":
        errors.append("blind-reader entrypoint must remain README.md")
    if data.get("max_intentional_hops")!=2:
        errors.append("two-hop navigation contract changed without protocol revision")
    if data.get("promotion_authority") is not False:
        errors.append("UX protocol may not grant promotion authority")
    tasks=data.get("tasks",[])
    ids={row.get("id") for row in tasks}
    missing=sorted(REQUIRED_IDS-ids)
    if missing:
        errors.append("missing frozen UX tasks: "+", ".join(missing))
    for row in tasks:
        evidence=row.get("evidence")
        if not evidence:
            errors.append(f"{row.get('id')}: missing evidence route")
            continue
        for raw in [x.strip() for x in evidence.split(";")]:
            p=ROOT/raw
            if not p.exists():
                errors.append(f"{row.get('id')}: evidence path missing: {raw}")
    if errors:
        print("BLIND-READER UX PROTOCOL AUDIT FAIL")
        for e in errors: print("- "+e)
        return 1
    print(f"BLIND-READER UX PROTOCOL AUDIT PASS ({len(tasks)} tasks)")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
