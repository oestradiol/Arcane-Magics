from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from kernel.development.lateral_episode import propose_lateral_reconstruction


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--dataset",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()

    dataset=json.loads(Path(args.dataset).read_text(encoding="utf-8"))
    proposal=propose_lateral_reconstruction(dataset)
    result=asdict(proposal)
    result["dataset_ref"]=args.dataset
    result["prefreeze_ref"]="kernel/development/LATERAL_EPISODE_1_PREFREEZE.json"
    result["status"]="PROJECTION_AND_HOLDOUT_PREDICTIONS_FROZEN"
    result["truth_authority"]=False
    Path(args.output).write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    return 0


if __name__=="__main__":
    raise SystemExit(main())
