from __future__ import annotations

import unittest

from kernel.development.audit_ssr_clean_reconciliation import audit


class SSRCleanReconciliationTests(unittest.TestCase):
    def test_bounded_meta_improvement_survives_but_uniqueness_does_not(self):
        out = audit()
        self.assertEqual(
            out["status"],
            "PASS_BOUNDED_SSR4_META_IMPROVEMENT_MATURE_REDUCED",
        )
        self.assertEqual(out["failures"], [])
        self.assertFalse(out["promotion_authority"])

        for cycle in out["cycles"]:
            self.assertGreater(cycle["successor_minus_parent"], 0)
            self.assertGreater(cycle["successor_minus_ablation"], 0)
            self.assertTrue(cycle["ctl_admitted"])
            self.assertEqual(cycle["adaptive_gate"], "ACCEPT_BOUNDED_SUCCESSOR")
            self.assertEqual(cycle["safety_floor_violations"], 0)
            self.assertTrue(cycle["rollback_available"])

        self.assertEqual(out["ssr3"]["cross_family_transfer"], "PASS_BOUNDED")
        self.assertGreater(out["ssr3"]["successor_minus_ablation"], 0)

        self.assertTrue(out["ssr4"]["bounded_meta_improvement_exists"])
        self.assertTrue(out["ssr4"]["load_bearing_after_transfer"])
        self.assertGreater(out["ssr4"]["successor_minus_ablation"], 0)
        self.assertEqual(out["ssr4"]["successor_minus_substitute"], 0)
        self.assertFalse(out["ssr4"]["venus_specific_uniqueness"])
        self.assertFalse(out["ssr4"]["venus_specific_superiority"])


if __name__ == "__main__":
    unittest.main()
