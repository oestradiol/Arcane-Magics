from __future__ import annotations

import unittest

from kernel.runtime.ctl import CTLCandidate, admit_successor


class CTLTests(unittest.TestCase):
    def lawful(self):
        return CTLCandidate(
            parent_root="parent",
            successor_root="successor",
            provenance_ids=("candidate", "return"),
            world_return_id="heldout-return",
            world_return_source_id="external-evaluator",
            rollback_root="parent",
            rollback_available=True,
            reopening_reachable=True,
            correction_channel_reachable=True,
            nonpreauthored_return_reachable=True,
            safety_floor_unchanged=True,
            self_authorized_success=False,
            self_validated_success=False,
            world_collapsed_into_model=False,
            other_collapsed_into_model=False,
            founder_hidden_dependency=False,
            functional_contract_preserved=True,
            promotion_authority=False,
        )

    def test_lawful_returned_successor_is_admitted(self):
        receipt = admit_successor(self.lawful())
        self.assertTrue(receipt.admitted)
        self.assertEqual(receipt.failures, ())
        self.assertFalse(receipt.promotion_authority)

    def test_self_sealing_successor_is_withheld(self):
        c = self.lawful()
        bad = CTLCandidate(
            **{
                **c.__dict__,
                "correction_channel_reachable": False,
                "reopening_reachable": False,
                "self_authorized_success": True,
            }
        )
        receipt = admit_successor(bad)
        self.assertFalse(receipt.admitted)
        self.assertIn("correction channel became unreachable", receipt.failures)

    def test_safety_floor_change_is_withheld(self):
        c = self.lawful()
        bad = CTLCandidate(**{**c.__dict__, "safety_floor_unchanged": False})
        receipt = admit_successor(bad)
        self.assertFalse(receipt.admitted)
        self.assertIn("non-internalizable safety floor changed", receipt.failures)


if __name__ == "__main__":
    unittest.main()
