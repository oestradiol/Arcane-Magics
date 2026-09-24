#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = {
    "edu17r1_mention_incidence": ROOT / "benchmarks/edu17r1_mention_incidence/protocol.json",
    "memory_causal": ROOT / "benchmarks/memory_causal/protocol.json",
    "abstention": ROOT / "benchmarks/abstention/protocol.json",
    "world_input_security": ROOT / "benchmarks/world_input_security/protocol.json",
}

def hidden_required(data: dict) -> bool:
    return bool(
        data.get("hidden_required_for_promotion")
        or data.get("hidden_dynamic_attack_required_for_promotion")
        or data.get("hidden_required")
    )

def main() -> int:
    errors: list[str] = []
    for name, path in BENCHMARKS.items():
        if not path.exists():
            errors.append(f"{name}: missing protocol")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("promotion_authority") is not False:
            errors.append(f"{name}: public protocol may not grant promotion authority")
        if not hidden_required(data):
            errors.append(f"{name}: claim-bearing hidden evaluation requirement is missing")
        if data.get("sealed_evaluation_core") != "evaluation/sealed_eval.py":
            errors.append(f"{name}: must bind shared sealed evaluation core")
        conditions = data.get("conditions", [])
        if len(conditions) < 4:
            errors.append(f"{name}: expected >=4 comparison/ablation conditions")
        fence = data.get("claim_fence")
        if not isinstance(fence, str) or len(fence.strip()) < 20:
            errors.append(f"{name}: missing claim fence")
    if errors:
        print("HIDDEN BENCHMARK PROTOCOL AUDIT FAIL")
        for e in errors:
            print("- " + e)
        return 1
    print(f"HIDDEN BENCHMARK PROTOCOL AUDIT PASS ({len(BENCHMARKS)} benchmark families)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
