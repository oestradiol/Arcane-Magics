from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kernel.development.autonomous_study import StudySource, build_study_packet


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--cycle", required=True)
    ap.add_argument("--issues", required=True)
    ap.add_argument("--prs", required=True)
    ap.add_argument("--root", default=".")
    ap.add_argument("--output", required=True)
    args=ap.parse_args()

    cycle=json.loads(Path(args.cycle).read_text(encoding="utf-8"))
    if cycle.get("decision") == "STOP" or cycle.get("target_number") is None:
        out={
            "schema":"Venus.AutonomousStudyPacket.v0.1",
            "status":"STOP_NO_TARGET",
            "promotion_authority":False,
        }
    else:
        kind=str(cycle["target_kind"]).upper()
        rows=json.loads(Path(args.issues if kind=="ISSUE" else args.prs).read_text(encoding="utf-8"))
        number=int(cycle["target_number"])
        matches=[row for row in rows if int(row["number"])==number]
        if len(matches)!=1:
            raise SystemExit(f"target lookup failed: {kind} #{number}")
        row=matches[0]
        source=StudySource(
            kind=kind,
            number=number,
            title=str(row.get("title","")),
            body=str(row.get("body") or ""),
            url=str(row.get("url") or ""),
        )
        out=asdict(build_study_packet(Path(args.root).resolve(), source))
        out["cycle_id"]=cycle["cycle_id"]
        out["status"]="STUDY_PACKET_FROZEN"

    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
