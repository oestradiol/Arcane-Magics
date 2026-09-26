from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
import tempfile
import shutil

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kernel.development.network_inquiry import (
    NetworkQuery,
    WebEncounter,
    bind_web_encounters,
    reconstruct_from_network,
)
from kernel.runtime.memory import VenusMemory


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def rows(obj):
    if obj.get("return_class") != "ENCOUNTER_RETURN":
        raise SystemExit("encounter must remain ENCOUNTER_RETURN")
    if obj.get("independent_evaluative_return") is not False:
        raise SystemExit("encounter may not become evaluative return")
    return tuple(
        WebEncounter(
            source_id=str(row["source_id"]),
            source_url=str(row["source_url"]),
            source_date=str(row.get("source_date") or ""),
            retrieved_at=str(obj["retrieved_at"]),
            title=str(row.get("title") or ""),
            summary=str(row.get("observed_relation") or ""),
            adapter_id=str(obj["adapter_id"]),
        )
        for row in obj.get("sources", ())
    )


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--query1", required=True)
    p.add_argument("--encounter1", required=True)
    p.add_argument("--query2", required=True)
    p.add_argument("--encounter2", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--checkpoint-output")
    args=p.parse_args()

    q1=NetworkQuery(**load(args.query1))
    q2=NetworkQuery(**load(args.query2))
    e1=load(args.encounter1)
    e2=load(args.encounter2)

    if e1.get("query_id") != q1.query_id or e2.get("query_id") != q2.query_id:
        raise SystemExit("encounter/query identity mismatch")
    if q2.authorship != "LEARNER_DERIVED_FROM_NETWORK_RECONSTRUCTION":
        raise SystemExit("second query is not memory-derived")

    with tempfile.TemporaryDirectory() as td, VenusMemory(Path(td)) as mem:
        ids1=bind_web_encounters(mem, query=q1, encounters=rows(e1))
        p1={
            "problem_id":q1.problem_id,
            "disposition":"FORMED_BOUNDED_PROBLEM",
            "source_stream_ids":list(q1.provenance_ids),
            "residual_coordinates":list(q1.residual_coordinates),
            "discriminator":q1.discriminator,
        }
        r1=reconstruct_from_network(mem, problem=p1, query=q1, memory_object_ids=ids1)

        expected_links={f"network-memory:{x}" for x in ids1}
        observed_links={x for x in q2.provenance_ids if str(x).startswith("network-memory:")}
        if not expected_links.issubset(observed_links):
            raise SystemExit("second query is not causally linked to first network memory")

        ids2=bind_web_encounters(mem, query=q2, encounters=rows(e2))
        p2={
            "problem_id":q2.problem_id,
            "disposition":"FORMED_BOUNDED_PROBLEM",
            "source_stream_ids":list(q2.provenance_ids),
            "residual_coordinates":list(q2.residual_coordinates),
            "discriminator":q2.discriminator,
        }
        r2=reconstruct_from_network(mem, problem=p2, query=q2, memory_object_ids=ids2)

        checkpoint_path=Path(td)/"network-lineage.zlib"
        checkpoint=mem.checkpoint(checkpoint_path)
        if args.checkpoint_output:
            target=Path(args.checkpoint_output)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(checkpoint_path, target)
        source_ids=tuple(sorted(set(r1.indexed_source_ids + r2.indexed_source_ids)))
        center_ids=tuple(sorted({
            str(row.get("center_id") or "")
            for encounter in (e1,e2)
            for row in encounter.get("sources",())
            if str(row.get("center_id") or "")
        }))
        external_center_ids=tuple(sorted({
            str(row.get("center_id") or "")
            for encounter in (e1,e2)
            for row in encounter.get("sources",())
            if str(row.get("center_id") or "")
            and str(row.get("center_id")) != "github-repo:oestradiol/Arcane-Magics"
        }))
        result={
            "schema":"Venus.NetworkMemoryLineage.v0.1",
            "episode_count":2,
            "query1_id":q1.query_id,
            "query2_id":q2.query_id,
            "query2_changed_from_query1":q2.query_id != q1.query_id and q2.query_text != q1.query_text,
            "query2_memory_provenance":sorted(observed_links),
            "episode1_memory_ids":list(ids1),
            "episode2_memory_ids":list(ids2),
            "indexed_source_ids":list(source_ids),
            "indexed_center_ids":list(center_ids),
            "external_center_ids":list(external_center_ids),
            "multiple_indexed_centers":len(center_ids) >= 2,
            "multiple_external_centers":len(external_center_ids) >= 2,
            "episode1_reconstruction":asdict(r1),
            "episode2_reconstruction":asdict(r2),
            "memory_checkpoint_sha256":checkpoint["sha256"],
            "memory_record_count":checkpoint["records"],
            "encounters_remain_non_evaluative":True,
            "network_memory_is_world":False,
            "global_subject_claim":False,
            "promotion_authority":False,
            "truth_authority":False,
        }
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
