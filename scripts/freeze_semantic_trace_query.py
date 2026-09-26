from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from kernel.runtime.relation_trace import search_relation_trace
from kernel.runtime.vmk2 import digest


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--query",required=True)
    p.add_argument("--encounter",required=True)
    p.add_argument("--state",required=True)
    p.add_argument("--trace-output",required=True)
    p.add_argument("--query-output",required=True)
    args=p.parse_args()

    query=json.loads(Path(args.query).read_text(encoding="utf-8"))
    encounter=json.loads(Path(args.encounter).read_text(encoding="utf-8"))
    state=json.loads(Path(args.state).read_text(encoding="utf-8"))
    if encounter.get("return_class")!="ENCOUNTER_RETURN":
        raise SystemExit("episode-1 input must remain ENCOUNTER_RETURN")
    if encounter.get("query_id")!=query.get("query_id"):
        raise SystemExit("query/encounter identity mismatch")
    anchors=tuple(str(x) for x in query.get("study_terms",()) if str(x).strip())
    trace=search_relation_trace(state,anchors=anchors,sources=encounter.get("sources",()))
    trace_obj=asdict(trace)
    Path(args.trace_output).write_text(json.dumps(trace_obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if trace.status!="RELATION_TRACE_CANDIDATE_FROZEN":
        return 0

    terms=tuple(trace.terms)
    prefix=anchors[:3]
    query_text=" ".join((*prefix,*terms[:6])).strip()
    body={
        "schema":"Venus.NetworkQuery.v0.1",
        "problem_id":str(query["problem_id"]),
        "query_text":query_text,
        "residual_coordinates":tuple(query.get("residual_coordinates",())),
        "discriminator":str(query.get("discriminator") or ""),
        "provenance_ids":tuple(query.get("provenance_ids",()))
            +(f"relation-trace:{trace.trace_id}",)
            +tuple(f"episode1-source:{x.get('source_id')}" for x in encounter.get("sources",())),
        "study_context_digest":query.get("study_context_digest"),
        "study_terms":tuple(query.get("study_terms",())),
        "authorship":"LEARNER_DERIVED_FROM_STATE_OWNED_RELATION_TRACE",
        "execution_owner":"EXTERNAL_ADAPTER",
        "promotion_authority":False,
        "truth_authority":False,
    }
    out={**body,"query_id":digest(body)}
    Path(args.query_output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
