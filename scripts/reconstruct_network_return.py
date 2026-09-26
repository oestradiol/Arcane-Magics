from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
import tempfile

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


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--query", required=True)
    p.add_argument("--encounter", required=True)
    p.add_argument("--output", required=True)
    args=p.parse_args()

    qobj=json.loads(Path(args.query).read_text(encoding="utf-8"))
    query=NetworkQuery(**qobj)

    eobj=json.loads(Path(args.encounter).read_text(encoding="utf-8"))
    if eobj.get("return_class") != "ENCOUNTER_RETURN":
        raise SystemExit("network encounter must remain ENCOUNTER_RETURN")
    if eobj.get("independent_evaluative_return") is not False:
        raise SystemExit("network encounter may not become evaluative return")
    if eobj.get("query_id") != query.query_id:
        raise SystemExit("query/encounter identity mismatch")

    encounters=tuple(
        WebEncounter(
            source_id=str(row["source_id"]),
            source_url=str(row["source_url"]),
            source_date=str(row.get("source_date") or ""),
            retrieved_at=str(eobj["retrieved_at"]),
            title=str(row.get("title") or ""),
            summary=str(row.get("observed_relation") or ""),
            adapter_id=str(eobj["adapter_id"]),
        )
        for row in eobj.get("sources", ())
    )

    problem={
        "problem_id": query.problem_id,
        "disposition": "FORMED_BOUNDED_PROBLEM",
        "source_stream_ids": list(query.provenance_ids),
        "residual_coordinates": list(query.residual_coordinates),
        "discriminator": query.discriminator,
    }

    with tempfile.TemporaryDirectory() as td, VenusMemory(Path(td)) as memory:
        ids=bind_web_encounters(memory, query=query, encounters=encounters)
        reconstruction=reconstruct_from_network(
            memory,
            problem=problem,
            query=query,
            memory_object_ids=ids,
        )
        checkpoint=memory.checkpoint(Path(td) / "network-memory.zlib")
        result={
            "schema":"Venus.NetworkEpisodeResult.v0.1",
            "query":qobj,
            "encounter_digest_ids":list(ids),
            "reconstruction":asdict(reconstruction),
            "memory_checkpoint_sha256":checkpoint["sha256"],
            "memory_record_count":checkpoint["records"],
            "encounter_return_remains_non_evaluative":True,
            "promotion_authority":False,
            "truth_authority":False,
        }
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
