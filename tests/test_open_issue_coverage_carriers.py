from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_open_issue_coverage.py"


class OpenIssueCoverageCarrierTests(unittest.TestCase):
    def run_audit(self, rows):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "issues.json"
            p.write_text(json.dumps(rows), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(SCRIPT), str(p)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                timeout=20,
            )

    def test_typed_autonomous_cycle_issue_is_infrastructure_not_project_issue(self):
        proc = self.run_audit([{
            "number": 127,
            "title": "venus: autonomous cycle pr-107",
        }])
        # Existing project docs may contain stale historical rows; carrier itself
        # must never appear as an unmapped-open failure.
        self.assertNotIn("#127", proc.stdout + proc.stderr)

    def test_similar_but_untyped_issue_is_not_exempted(self):
        proc = self.run_audit([{
            "number": 999999,
            "title": "venus autonomous cycle pr-107",
        }])
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("#999999", proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
