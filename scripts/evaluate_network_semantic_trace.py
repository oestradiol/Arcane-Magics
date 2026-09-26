from __future__ import annotations

import argparse
import json
from pathlib import Path


def metrics(query:dict, encounter:dict)->dict:
    anchors=tuple(str(x) for x in query.get("study_terms",()) if str(x).strip())
    sources=tuple(encounter.get("sources",()))
    matched=[tuple(str(x) for x in row.get("relevance_matches",())) for row in sources]
    covered=sorted({x for row in matched for x in row})
    total=sum(len(x) for x in matched)
    mean=(total/len(sources)) if sources else 0.0
    external=len(set(encounter.get("external_center_ids",())))
    return {
        "source_count":len(sources),
        "external_center_count":external,
        "anchor_coverage_count":len(covered),
        "anchor_total":len(set(anchors)),
        "mean_relevance_matches":mean,
        "query_token_count":len(str(query.get("query_text") or "").split()),
        "covered_anchors":covered,
    }


def score(m:dict)->tuple:
    return (
        int(m["anchor_coverage_count"]),
        float(m["mean_relevance_matches"]),
        int(m["external_center_count"]),
        -int(m["query_token_count"]),
    )


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--prefreeze",required=True)
    p.add_argument("--baseline-query",required=True)
    p.add_argument("--baseline-encounter",required=True)
    p.add_argument("--candidate-query",required=True)
    p.add_argument("--candidate-encounter",required=True)
    p.add_argument("--trace",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    pref=json.loads(Path(args.prefreeze).read_text(encoding="utf-8"))
    bq=json.loads(Path(args.baseline_query).read_text(encoding="utf-8"))
    be=json.loads(Path(args.baseline_encounter).read_text(encoding="utf-8"))
    cq=json.loads(Path(args.candidate_query).read_text(encoding="utf-8"))
    ce=json.loads(Path(args.candidate_encounter).read_text(encoding="utf-8"))
    trace=json.loads(Path(args.trace).read_text(encoding="utf-8"))

    bm=metrics(bq,be); cm=metrics(cq,ce)
    bs=score(bm); cs=score(cm)
    eligible=cm["external_center_count"]>=2
    improved=eligible and cs>bs
    status="PASS_BOUNDED_RELATION_TRACE_QUERY" if improved else "WITHHOLD_NO_RETURNED_GAIN_OVER_LEXICAL_BASELINE"
    out={
        "schema":"Venus.NetworkSemanticTraceComparatorResult.v0.1",
        "prefreeze_schema":pref.get("schema"),
        "status":status,
        "baseline_query_id":bq.get("query_id"),
        "candidate_query_id":cq.get("query_id"),
        "trace_id":trace.get("trace_id"),
        "trace_config_id":trace.get("config_id"),
        "baseline_metrics":bm,
        "candidate_metrics":cm,
        "baseline_score":list(bs),
        "candidate_score":list(cs),
        "candidate_external_center_floor_met":eligible,
        "strict_returned_gain":improved,
        "independent_evaluation":False,
        "internalization_claim":False,
        "general_semantics_claim":False,
        "promotion_authority":False,
        "truth_authority":False,
        "claim_fence":pref.get("claim_fence"),
    }
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
