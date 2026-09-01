from __future__ import annotations
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / "src"))

from research_tools.validate.governance import validate_repository_minimality


def run_audit():
    repo_root = BASE.parent
    results = validate_repository_minimality(repo_root)
    failed = [r for r in results if r.status == "fail"]
    return {
        "status": "PASS" if not failed else "FAIL",
        "total_checks": len(results),
        "failed_checks": len(failed),
        "results": [r.__dict__ for r in results],
    }


if __name__ == "__main__":
    report = run_audit()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report["status"] == "PASS" else 1)
