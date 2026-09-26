from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kernel.development.network_inquiry import (
    NetworkQuery,
    NetworkReconstruction,
    form_followup_network_query,
)


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--result", required=True)
    p.add_argument("--output", required=True)
    args=p.parse_args()

    obj=json.loads(Path(args.result).read_text(encoding="utf-8"))
    prior=NetworkQuery(**obj["query"])
    recon=NetworkReconstruction(**obj["reconstruction"])
    follow=form_followup_network_query(prior_query=prior,reconstruction=recon)
    Path(args.output).write_text(
        json.dumps(asdict(follow), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
