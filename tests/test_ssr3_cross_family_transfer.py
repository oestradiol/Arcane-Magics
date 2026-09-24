from __future__ import annotations

import unittest

from kernel.development.run_ssr3_cross_family_transfer import run


class SSR3CrossFamilyTransferTests(unittest.TestCase):
    def test_prefrozen_repair_machinery_transfers_without_retraining(self):
        out = run()
        self.assertEqual(out["disposition"], "PASS_BOUNDED_SSR3_CROSS_FAMILY_TRANSFER")
        self.assertFalse(out["target_specific_retraining"])
        self.assertFalse(out["promotion_authority"])
        self.assertEqual(
            out["mechanism_uniqueness"],
            "MATURE_REDUCED_AGAINST_DIRECT_HOST",
        )
        for family in out["families"].values():
            scores = family["scores"]
            self.assertEqual(
                scores["S_successor"]["correct"],
                scores["S_successor"]["total"],
            )
            self.assertGreater(family["causal_delta_successor_minus_parent"], 0)
            self.assertGreater(family["causal_delta_successor_minus_ablation"], 0)
            self.assertEqual(family["direct_host_gap"], 0)


if __name__ == "__main__":
    unittest.main()
