from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from kernel.runtime.relation_trace import search_relation_trace


def signature(trace):
    return {
        "status": trace.status,
        "config_id": trace.config_id,
        "terms": list(trace.terms),
        "relations": [
            {
                "term": r.term,
                "anchor_terms": list(r.anchor_terms),
                "source_support": r.source_support,
                "anchor_degree": r.anchor_degree,
                "title_support": r.title_support,
            }
            for r in trace.relations
        ],
    }


def scrub_anchor_tokens(rows, anchor_terms):
    pats=[re.compile(r"(?i)(?<![A-Za-z])"+re.escape(x)+r"(?![A-Za-z])") for x in anchor_terms]
    out=[]
    for row in rows:
        row=dict(row)
        for key in ("title","observed_relation","summary"):
            value=str(row.get(key) or "")
            for pat in pats:
                value=pat.sub("opaqueanchor",value)
            if key in row:
                row[key]=value
        out.append(row)
    return out


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--query",required=True)
    p.add_argument("--encounter",required=True)
    p.add_argument("--state",required=True)
    p.add_argument("--learning-state",required=False)
    p.add_argument("--output",required=True)
    args=p.parse_args()

    query=json.loads(Path(args.query).read_text(encoding="utf-8"))
    encounter=json.loads(Path(args.encounter).read_text(encoding="utf-8"))
    state=json.loads(Path(args.state).read_text(encoding="utf-8"))
    learning_state=(
        json.loads(Path(args.learning_state).read_text(encoding="utf-8"))
        if args.learning_state else None
    )
    anchors=tuple(str(x) for x in query.get("study_terms",()) if str(x).strip())
    sources=[dict(x) for x in encounter.get("sources",())]

    original=search_relation_trace(state,anchors=anchors,learning_state=learning_state,sources=sources)
    original_sig=signature(original)

    reversed_trace=search_relation_trace(state,anchors=anchors,learning_state=learning_state,sources=list(reversed(sources)))
    order_invariant=signature(reversed_trace)==original_sig

    renamed=[]
    for i,row in enumerate(sources):
        row=dict(row)
        row["source_id"]=f"opaque-source-{i:03d}"
        row["irrelevant_probe_metadata"]={"slot":len(sources)-i}
        renamed.append(row)
    renamed_trace=search_relation_trace(state,anchors=anchors,learning_state=learning_state,sources=renamed)
    source_identity_invariant=signature(renamed_trace)==original_sig

    scrubbed=scrub_anchor_tokens(sources,original.anchor_terms)
    scrubbed_trace=search_relation_trace(state,anchors=anchors,learning_state=learning_state,sources=scrubbed)
    relevant_perturbation_changes=signature(scrubbed_trace)!=original_sig

    nuisance_pass=order_invariant and source_identity_invariant
    passed=(
        original.status=="RELATION_TRACE_CANDIDATE_FROZEN"
        and nuisance_pass
        and relevant_perturbation_changes
    )
    out={
        "schema":"Venus.NetworkSemanticTraceAbstractionProbeResult.v0.1",
        "status":"PASS_BOUNDED_B1_STRUCTURAL_ABSTRACTION" if passed else "WITHHOLD_B1_ABSTRACTION",
        "original_trace_id":original.trace_id,
        "original_signature":original_sig,
        "source_order_invariant":order_invariant,
        "opaque_source_identity_invariant":source_identity_invariant,
        "relevant_anchor_perturbation_changes_trace":relevant_perturbation_changes,
        "nuisance_invariance_pass":nuisance_pass,
        "general_semantics_claim":False,
        "cross_language_abstraction_claim":False,
        "internalization_claim":False,
        "independent_evaluation":False,
        "promotion_authority":False,
        "truth_authority":False,
        "claim_fence":"This is a bounded B1 structural probe over one returned encounter. It shows nuisance invariance plus sensitivity to a relevant anchor perturbation; it does not establish general semantic abstraction, B2 downstream causal use, B3 internalization, truth, or promotion."
    }
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
