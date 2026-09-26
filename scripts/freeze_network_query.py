from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kernel.development.network_inquiry import form_network_query, bind_network_execution_context
from kernel.development.autonomous_worker import load_work_items
from kernel.development.autonomous_problem_formation import snapshot_to_incidence


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--problem", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--issues")
    p.add_argument("--prs")
    p.add_argument("--context-output")
    p.add_argument("--repository", default="oestradiol/Arcane-Magics")
    args=p.parse_args()

    problem=json.loads(Path(args.problem).read_text(encoding="utf-8"))
    query=form_network_query(problem)
    Path(args.output).write_text(
        json.dumps(query.__dict__, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if args.context_output:
        if not args.issues or not args.prs:
            raise SystemExit("--context-output requires --issues and --prs")
        issues=load_work_items(args.issues, "ISSUE")
        prs=load_work_items(args.prs, "PR")
        wanted=set(problem.get("source_stream_ids") or ())
        carrier_keys=[]
        for item in tuple(issues) + tuple(prs):
            row=snapshot_to_incidence((item,))[0]
            if row.stream_id in wanted:
                carrier_keys.append((item.kind, item.number))
        if not carrier_keys:
            raise SystemExit("no carrier locator resolves learner problem provenance")
        context=bind_network_execution_context(
            query=query,
            carrier_keys=carrier_keys,
            repository_full_name=args.repository,
        )
        Path(args.context_output).write_text(
            json.dumps(context.__dict__, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
