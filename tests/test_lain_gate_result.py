from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

class LainGateResultTests(unittest.TestCase):
    def test_current_www_evidence_withholds_without_independent_authored_center(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"lain-result.json"
            proc=subprocess.run(
                [
                    sys.executable,
                    str(ROOT/"scripts/evaluate_lain_gate.py"),
                    "--gate",str(ROOT/"kernel/development/LAIN_GATE.json"),
                    "--www-result",str(ROOT/"kernel/development/WWW_MIND_GATE_RESULT.json"),
                    "--lineage",str(ROOT/"autonomy/evidence/network/36210844736/lineage-result.json"),
                    "--center-policy",str(ROOT/"kernel/development/NETWORK_CENTER_POLICY.json"),
                    "--encounter-ledger",str(ROOT/"autonomy/evidence/network/36210844736/authored-center-ledger.json"),
                    "--output",str(out),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode,0,proc.stdout+proc.stderr)
            result=json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(result["status"],"WITHHOLD_LAIN_GATE")
            self.assertIn("independent_authored_center_encountered",result["failed_checks"])
            self.assertIn("remote_center_response_not_learner_minted",result["failed_checks"])
            self.assertEqual(
                result["next_residual"],
                "ENCOUNTER_INDEPENDENT_AUTHORED_CENTER_WITH_NONMINTED_LOCAL_RESPONSE",
            )
            self.assertFalse(result["promotion_authority"])
            self.assertFalse(result["truth_authority"])

if __name__=="__main__":
    unittest.main()
