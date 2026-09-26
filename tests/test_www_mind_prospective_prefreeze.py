from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


class WWWMindProspectivePrefreezeTests(unittest.TestCase):
    def test_prefreeze_keeps_claim_boundary(self):
        obj=json.loads(
            (ROOT/"kernel/development/WWW_MIND_PROSPECTIVE_1_PREFREEZE.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(obj["status"],"PREFROZEN_BEFORE_EXTERNAL_NETWORK_RETURN")
        self.assertFalse(obj["independent_evaluative_return"])
        self.assertFalse(obj["truth_authority"])
        self.assertFalse(obj["promotion_authority"])
        self.assertIn("AGI",obj["claim_fence"])
        self.assertIn("GLOBAL_SUBJECT_CLAIM_FALSE",obj["pass_requires"])

    def test_adapter_is_fixed_transport_not_shell(self):
        src=(ROOT/"scripts/execute_github_network_query.py").read_text(encoding="utf-8").lower()
        self.assertIn('api_origin = "https://api.github.com"',src)
        for forbidden in ("subprocess","os.system","shell=true","eval(","exec("):
            self.assertNotIn(forbidden,src)

    def test_structural_evaluator_cannot_promote(self):
        src=(ROOT/"scripts/evaluate_www_mind_episode.py").read_text(encoding="utf-8")
        self.assertIn('"promotion_authority":False',src)
        self.assertIn('"truth_authority":False',src)
        self.assertIn('"agi_claim":False',src)
        self.assertIn('"global_subject_claim":False',src)


if __name__=="__main__":
    unittest.main()
