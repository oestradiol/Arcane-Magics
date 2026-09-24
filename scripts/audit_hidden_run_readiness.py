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
        "condition_freeze": ROOT / "benchmarks/edu17r1_mention_incidence/CONDITION_IMPLEMENTATIONS.json",
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
        implementation_ready=True
        freeze_path=cfg.get("condition_freeze")
        if freeze_path is not None:
            if not freeze_path.exists():
                errors.append(f"{name}: missing frozen condition implementation manifest")
                implementation_ready=False
            else:
                freeze=json.loads(freeze_path.read_text(encoding="utf-8"))
                frozen=set((freeze.get("conditions") or {}).keys())
                if frozen != cfg["required_conditions"]:
                    errors.append(f"{name}: frozen condition set mismatch {sorted(frozen)}")
                    implementation_ready=False
                if freeze.get("status") != "PREFROZEN_BEFORE_HIDDEN_SPLIT":
                    errors.append(f"{name}: condition implementations not prefrozen")
                    implementation_ready=False
                if freeze.get("hidden_split_authored") is not False or freeze.get("hidden_labels_exposed") is not False:
                    errors.append(f"{name}: hidden boundary already violated in condition freeze")
                    implementation_ready=False
        report.append({
            "benchmark":name,
            "issue":cfg["issue"],
            "conditions":sorted(ids),
            "implementation_ready":implementation_ready,
            "hidden_ready":not bool(missing) and implementation_ready,
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
