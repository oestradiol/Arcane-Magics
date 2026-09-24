from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from kernel.development.autonomous_study import StudyTarget, make_study_packet


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--target", required=True)
    p.add_argument("--root", default=".")
    p.add_argument("--output", required=True)
    args = p.parse_args()

    obj = json.loads(Path(args.target).read_text(encoding="utf-8"))
    target = StudyTarget(
        kind=str(obj["kind"]),
        number=int(obj["number"]),
        title=str(obj["title"]),
        body=str(obj.get("body", "")),
        method=str(obj["method"]),
        changed_files=tuple(str(x) for x in obj.get("changed_files", ())),
        failed_checks=tuple(str(x) for x in obj.get("failed_checks", ())),
        pending_checks=tuple(str(x) for x in obj.get("pending_checks", ())),
        review_states=tuple(str(x) for x in obj.get("review_states", ())),
        comment_count=int(obj.get("comment_count", 0)),
        label_count=int(obj.get("label_count", 0)),
        merge_state=obj.get("merge_state"),
    )
    packet = make_study_packet(Path(args.root), target)
    Path(args.output).write_text(
        json.dumps(asdict(packet), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(asdict(packet), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
