from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

# GitHub Actions invokes this file directly as:
#   python scripts/run_venus_research_proposal.py ...
# Direct-script execution puts scripts/ rather than the repository root first on
# sys.path, so bootstrap the checked-out repository before importing kernel.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kernel.development.autonomous_proposal import make_research_proposal, proposal_dict
from kernel.development.autonomous_evidence import evidence_dict, run_proposal_checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycle", required=True)
    parser.add_argument("--proposal-output", required=True)
    parser.add_argument("--evidence-output", required=True)
    parser.add_argument("--check-catalog", required=False)
    args = parser.parse_args()

    cycle = json.loads(Path(args.cycle).read_text(encoding="utf-8"))
    catalog = (
        json.loads(Path(args.check_catalog).read_text(encoding="utf-8"))
        if args.check_catalog else None
    )
    proposal = make_research_proposal(cycle, check_catalog=catalog)
    Path(args.proposal_output).write_text(
        json.dumps(proposal_dict(proposal), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    evidence = run_proposal_checks(proposal_dict(proposal), cwd=ROOT)
    Path(args.evidence_output).write_text(
        json.dumps(evidence_dict(evidence), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "proposal_id": proposal.proposal_id,
        "proposal_disposition": proposal.disposition,
        "evidence_id": evidence.evidence_id,
        "evidence_status": evidence.status,
    }, sort_keys=True))
    return 0 if evidence.all_local_checks_passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
