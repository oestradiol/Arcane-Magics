from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]


class WWWMindGateResultTests(unittest.TestCase):
    def test_returned_lineage_passes_bounded_www_gate(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"result.json"
            proc=subprocess.run(
                [
                    sys.executable,
                    str(ROOT/"scripts/evaluate_www_mind_gate.py"),
                    "--gate",str(ROOT/"kernel/development/WWW_MIND_GATE.json"),
                    "--lineage",str(ROOT/"autonomy/evidence/network/36210844736/lineage-result.json"),
                    "--center-policy",str(ROOT/"kernel/development/NETWORK_CENTER_POLICY.json"),
                    "--output",str(out),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode,0,proc.stdout+proc.stderr)
            result=json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(result["status"],"PASS_BOUNDED_WWW_MIND_GATE")
            self.assertFalse(result["promotion_authority"])
            self.assertFalse(result["truth_authority"])
            self.assertEqual(result["failed_checks"],[])


if __name__=="__main__":
    unittest.main()
