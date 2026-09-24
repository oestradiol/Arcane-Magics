from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_venus_autonomous_cycle.py"
POLICY = ROOT / "kernel/development/INTERNAL_OSTAR_INTERNALIZED_POLICY.json"
LEARNING = ROOT / "kernel/development/AUTONOMOUS_LEARNING_STATE.json"


class AutonomousEntrypointTests(unittest.TestCase):
    def test_direct_script_invocation_can_import_kernel(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=20,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("--learning-state", proc.stdout)
        self.assertIn("--output", proc.stdout)

    def test_full_direct_cli_stops_behind_open_issue_carrier(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            issues = root / "issues.json"
            prs = root / "prs.json"
            history_prs = root / "history-prs.json"
            history_issues = root / "history-issues.json"
            roadmap = root / "roadmap.md"
            learning_out = root / "learning.json"
            cycle_out = root / "cycle.json"

            issues.write_text(json.dumps([{
                "number": 72,
                "title": "Safe Strong RSI",
                "body": "Open work.",
                "state": "OPEN",
                "updatedAt": "2026-09-24T22:00:00Z",
            }]), encoding="utf-8")
            prs.write_text("[]\n", encoding="utf-8")
            history_prs.write_text("[]\n", encoding="utf-8")
            history_issues.write_text(json.dumps([{
                "_carrier_kind": "ISSUE",
                "number": 300,
                "title": "venus: autonomous cycle pr-106",
                "state": "OPEN",
                "closedAt": None,
                "comments": [],
            }]), encoding="utf-8")
            roadmap.write_text("#72\n", encoding="utf-8")

            proc = subprocess.run(
                [
                    sys.executable, str(SCRIPT),
                    "--issues", str(issues),
                    "--prs", str(prs),
                    "--history-prs", str(history_prs),
                    "--history-issues", str(history_issues),
                    "--roadmap", str(roadmap),
                    "--policy", str(POLICY),
                    "--learning-state", str(LEARNING),
                    "--learning-output", str(learning_out),
                    "--output", str(cycle_out),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                timeout=20,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            cycle = json.loads(cycle_out.read_text(encoding="utf-8"))
            self.assertEqual(cycle["decision"], "STOP")
            self.assertIsNone(cycle["target_number"])

    def test_full_direct_cli_stops_behind_open_external_return(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            issues = root / "issues.json"
            prs = root / "prs.json"
            history = root / "history.json"
            roadmap = root / "roadmap.md"
            learning_out = root / "learning.json"
            cycle_out = root / "cycle.json"

            issues.write_text(json.dumps([{
                "number": 31,
                "title": "hidden semantic return",
                "body": "Awaiting external hidden return.",
                "state": "OPEN",
                "updatedAt": "2026-09-24T21:00:00Z",
            }]), encoding="utf-8")
            prs.write_text("[]\n", encoding="utf-8")
            history.write_text(json.dumps([{
                "number": 103,
                "title": "venus: autonomous cycle issue-31",
                "state": "OPEN",
                "mergedAt": None,
                "closedAt": None,
                "reviews": [],
            }]), encoding="utf-8")
            roadmap.write_text("#31\n", encoding="utf-8")

            proc = subprocess.run(
                [
                    sys.executable, str(SCRIPT),
                    "--issues", str(issues),
                    "--prs", str(prs),
                    "--history-prs", str(history),
                    "--roadmap", str(roadmap),
                    "--policy", str(POLICY),
                    "--learning-state", str(LEARNING),
                    "--learning-output", str(learning_out),
                    "--output", str(cycle_out),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                timeout=20,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            cycle = json.loads(cycle_out.read_text(encoding="utf-8"))
            self.assertEqual(cycle["decision"], "STOP")
            self.assertIsNone(cycle["target_number"])
            self.assertTrue(learning_out.is_file())


if __name__ == "__main__":
    unittest.main()
