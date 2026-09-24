from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kernel.development.autonomy_agency import make_agency_receipt, receipt_dict


def load(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--cycle", required=True)
    p.add_argument("--proposal", required=True)
    p.add_argument("--evidence", required=True)
    p.add_argument("--change", required=True)
    p.add_argument("--patch-plan", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    receipt = make_agency_receipt(
        cycle=load(args.cycle),
        proposal=load(args.proposal),
        evidence=load(args.evidence),
        change=load(args.change),
        patch_plan=load(args.patch_plan),
    )
    out = receipt_dict(receipt)
    Path(args.output).write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(out, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
