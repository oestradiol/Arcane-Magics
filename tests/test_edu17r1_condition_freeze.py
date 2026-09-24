from __future__ import annotations
import unittest
from scripts.audit_edu17r1_condition_freeze import audit

class EDU17R1ConditionFreezeTests(unittest.TestCase):
    def test_prefrozen_condition_set_is_bound_and_matched(self):
        out=audit()
        self.assertEqual(out["status"],"PASS_CONDITION_IMPLEMENTATIONS_PREFROZEN")
        self.assertTrue(all(out["gates"].values()))
        self.assertFalse(out["hidden_labels_exposed"])
        self.assertFalse(out["promotion_authority"])

if __name__=="__main__":
    unittest.main()
