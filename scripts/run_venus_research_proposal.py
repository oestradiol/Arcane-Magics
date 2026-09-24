from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kernel.development.autonomous_proposal import make_research_proposal, proposal_dict
from kernel.development.autonomous_evidence import evidence_dict, run_proposal_checks
from kernel.development.autonomous_study import StudyTarget, run_bounded_reproduction


def _find_target(rows, number: int):
    for row in rows:
        if int(row["number"]) == number:
            return row
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycle", required=True)
    parser.add_argument("--issues", required=True)
    parser.add_argument("--prs", required=True)
    parser.add_argument("--proposal-output", required=True)
    parser.add_argument("--evidence-output", required=True)
    parser.add_argument("--execution-output", required=True)
    args = parser.parse_args()

    cycle = json.loads(Path(args.cycle).read_text(encoding="utf-8"))
    proposal = make_research_proposal(cycle)
    proposal_obj = proposal_dict(proposal)
    Path(args.proposal_output).write_text(
        json.dumps(proposal_obj, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    evidence = run_proposal_checks(proposal_obj, cwd=ROOT)
    Path(args.evidence_output).write_text(
        json.dumps(evidence_dict(evidence), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    reproduction_status = None
    reproduction_passed = True
    if proposal.study_method == "REPRODUCTION":
        kind = str(proposal.target_kind).upper()
        rows = json.loads(
            Path(args.issues if kind == "ISSUE" else args.prs).read_text(encoding="utf-8")
        )
        row = _find_target(rows, proposal.target_number)
        if row is None:
            raise SystemExit(
                f"selected target missing from frozen snapshot: {kind} #{proposal.target_number}"
            )
        receipt = run_bounded_reproduction(
            ROOT,
            cycle_id=proposal.cycle_id,
            target=StudyTarget(
                kind=kind,
                number=proposal.target_number,
                title=str(row.get("title") or ""),
                body=str(row.get("body") or ""),
            ),
        )
        Path(args.execution_output).write_text(
            json.dumps(asdict(receipt), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        reproduction_status = receipt.status
        reproduction_passed = receipt.status == "PASS_REPRODUCED_CURRENT_MAIN"

    print(json.dumps({
        "proposal_id": proposal.proposal_id,
        "proposal_disposition": proposal.disposition,
        "evidence_id": evidence.evidence_id,
        "evidence_status": evidence.status,
        "reproduction_status": reproduction_status,
    }, sort_keys=True))
    return 0 if evidence.all_local_checks_passed and reproduction_passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
