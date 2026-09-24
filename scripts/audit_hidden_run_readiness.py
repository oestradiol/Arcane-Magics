#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

FAMILIES = {
    "edu17r1_mention_incidence": {
        "protocol": ROOT / "benchmarks/edu17r1_mention_incidence/protocol.json",
        "required_conditions": {"A", "B", "C", "D"},
        "issue": 31,
    },
    "memory_causal": {
        "protocol": ROOT / "benchmarks/memory_causal/protocol.json",
        "required_conditions": {"venus_memory_full", "no_memory"},
        "issue": 15,
    },
    "abstention": {
        "protocol": ROOT / "benchmarks/abstention/protocol.json",
        "required_conditions": {
            "ordinary_strong_scaffold",
            "full_venus",
            "venus_minus_stop_withhold",
            "venus_minus_provenance_authority",
            "mature_abstention_substitute",
        },
        "issue": 42,
    },
    "world_input_security": {
        "protocol": ROOT / "benchmarks/world_input_security/protocol.json",
        "required_conditions": {
            "ordinary_agent",
            "full_venus_governance",
            "venus_minus_provenance_authority",
            "venus_minus_memory_disposition_typing",
            "mature_security_defense",
        },
        "issue": 43,
    },
}

def condition_ids(data: dict) -> set[str]:
    out=set()
    for row in data.get("conditions", []):
        if isinstance(row, str):
            out.add(row)
        elif isinstance(row, dict) and isinstance(row.get("id"), str):
            out.add(row["id"])
    return out

def main() -> int:
    errors=[]
    report=[]
    for name, cfg in FAMILIES.items():
        p=cfg["protocol"]
        if not p.exists():
            errors.append(f"{name}: missing protocol")
            continue
        data=json.loads(p.read_text(encoding="utf-8"))
        ids=condition_ids(data)
        missing=cfg["required_conditions"]-ids
        if missing:
            errors.append(f"{name}: missing required conditions {sorted(missing)}")
        if data.get("sealed_evaluation_core") != "evaluation/sealed_eval.py":
            errors.append(f"{name}: shared sealed evaluation core not bound")
        authority = data.get("promotion_authority")
        if authority is None and isinstance(data.get("promotion_rule"), dict):
            authority = data["promotion_rule"].get("authority")
        if authority is not False:
            errors.append(f"{name}: protocol must explicitly deny promotion authority")
        report.append({
            "benchmark":name,
            "issue":cfg["issue"],
            "conditions":sorted(ids),
            "hidden_ready":not bool(missing),
            "external_hidden_data_still_required":True,
        })
    if errors:
        print("HIDDEN-RUN READINESS FAIL")
        for e in errors:
            print("- "+e)
        return 1
    print(json.dumps({
        "schema":"Venus.HiddenRunReadiness.v0.1",
        "status":"HARNESS_READY_EXTERNAL_HIDDEN_RETURN_REQUIRED",
        "promotion_authority":False,
        "benchmarks":report,
    }, indent=2, sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
