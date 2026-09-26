from __future__ import annotations

"""Evaluate the prefrozen structural WWW-Mind episode.

This is a deterministic structural gate over frozen artifacts. It is not an
independent evaluator and cannot mint truth, promotion, AGI, consciousness, or
global-subject claims.
"""

import argparse
import hashlib
import json
from pathlib import Path
import zlib


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--prefreeze",required=True)
    p.add_argument("--problem",required=True)
    p.add_argument("--query1",required=True)
    p.add_argument("--encounter1",required=True)
    p.add_argument("--query2")
    p.add_argument("--encounter2")
    p.add_argument("--lineage")
    p.add_argument("--memory-checkpoint")
    p.add_argument("--output",required=True)
    args=p.parse_args()

    pre=load(args.prefreeze)
    problem=load(args.problem)
    q1=load(args.query1)
    e1=load(args.encounter1)
    failures=[]

    if pre.get("status") != "PREFROZEN_BEFORE_EXTERNAL_NETWORK_RETURN":
        failures.append("PREFREEZE_STATUS_INVALID")
    if problem.get("disposition") not in {
        "FORMED_BOUNDED_PROBLEM",
        "FORMED_STANDING_DEVELOPMENTAL_PROBLEM",
    }:
        failures.append("FORMED_NONSTOP_PROBLEM_MISSING")
    if q1.get("authorship") not in {
        "LEARNER_DERIVED_FROM_FORMED_PROBLEM",
        "LEARNER_DERIVED_FROM_SELECTED_STUDY",
    }:
        failures.append("QUERY1_NOT_LEARNER_DERIVED")
    if q1.get("execution_owner") != "EXTERNAL_ADAPTER":
        failures.append("QUERY1_EXECUTION_OWNER_NOT_EXTERNAL")
    if e1.get("return_class") != "ENCOUNTER_RETURN" or e1.get("independent_evaluative_return") is not False:
        failures.append("EPISODE1_RETURN_CLASS_COLLAPSE")
    if e1.get("truth_authority") is not False or e1.get("promotion_authority") is not False:
        failures.append("EPISODE1_AUTHORITY_COLLAPSE")

    q2=load(args.query2) if args.query2 and Path(args.query2).is_file() else None
    e2=load(args.encounter2) if args.encounter2 and Path(args.encounter2).is_file() else None
    lineage=load(args.lineage) if args.lineage and Path(args.lineage).is_file() else None

    if q2 is None:
        failures.append("FOLLOWUP_QUERY_MISSING")
    else:
        if q2.get("authorship") != "LEARNER_DERIVED_FROM_NETWORK_RECONSTRUCTION":
            failures.append("FOLLOWUP_QUERY_NOT_MEMORY_DERIVED")
        if q2.get("query_id") == q1.get("query_id") or q2.get("query_text") == q1.get("query_text"):
            failures.append("FOLLOWUP_QUERY_UNCHANGED")
        if not any(str(x).startswith("network-memory:") for x in q2.get("provenance_ids",())):
            failures.append("FOLLOWUP_QUERY_MEMORY_PROVENANCE_MISSING")
        if q2.get("truth_authority") is not False or q2.get("promotion_authority") is not False:
            failures.append("FOLLOWUP_QUERY_AUTHORITY_COLLAPSE")

    if e2 is None:
        failures.append("EPISODE2_ENCOUNTER_MISSING")
    else:
        if e2.get("return_class") != "ENCOUNTER_RETURN" or e2.get("independent_evaluative_return") is not False:
            failures.append("EPISODE2_RETURN_CLASS_COLLAPSE")
        if e2.get("truth_authority") is not False or e2.get("promotion_authority") is not False:
            failures.append("EPISODE2_AUTHORITY_COLLAPSE")

    if lineage is None:
        failures.append("NETWORK_LINEAGE_MISSING")
    else:
        if lineage.get("query2_changed_from_query1") is not True:
            failures.append("LINEAGE_QUERY_CHANGE_NOT_CAUSAL")
        if lineage.get("multiple_external_centers") is not True:
            failures.append("INSUFFICIENT_EXTERNAL_INDEXED_CENTERS")
        if lineage.get("encounters_remain_non_evaluative") is not True:
            failures.append("LINEAGE_EVALUATIVE_COLLAPSE")
        if lineage.get("network_memory_is_world") is not False:
            failures.append("NETWORK_MEMORY_WORLD_COLLAPSE")
        if lineage.get("global_subject_claim") is not False:
            failures.append("GLOBAL_SUBJECT_CLAIM")
        if lineage.get("promotion_authority") is not False or lineage.get("truth_authority") is not False:
            failures.append("LINEAGE_AUTHORITY_COLLAPSE")

    checkpoint_ok=False
    if lineage is not None and args.memory_checkpoint and Path(args.memory_checkpoint).is_file():
        raw=zlib.decompress(Path(args.memory_checkpoint).read_bytes())
        checkpoint_ok=hashlib.sha256(raw).hexdigest() == str(lineage.get("memory_checkpoint_sha256") or "")
    if not checkpoint_ok:
        failures.append("PERSISTED_MEMORY_CHECKPOINT_MISSING_OR_MISMATCHED")

    status="PASS_BOUNDED_WWW_MIND_STRUCTURAL_GATE" if not failures else "WITHHOLD_WWW_MIND_GATE"
    result={
        "schema":"Venus.WWWMindProspectiveEpisodeResult.v0.1",
        "status":status,
        "prefreeze_status":pre.get("status"),
        "problem_id":problem.get("problem_id"),
        "query1_id":q1.get("query_id"),
        "query2_id":None if q2 is None else q2.get("query_id"),
        "failures":failures,
        "memory_checkpoint_verified":checkpoint_ok,
        "independent_evaluative_return":False,
        "network_memory_is_world":False,
        "global_subject_claim":False,
        "agi_claim":False,
        "consciousness_claim":False,
        "truth_authority":False,
        "promotion_authority":False,
        "claim_fence":pre.get("claim_fence"),
    }
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
