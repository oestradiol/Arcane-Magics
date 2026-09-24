from __future__ import annotations

import json
from pathlib import Path
import unittest

from kernel.development.edu17r1_repair_contract import (
    DevelopmentalOwnershipError,
    bind_candidate,
    canonical_sha256,
    load_parent,
    validate_candidate,
)


class EDU17R1RepairOwnershipContractTests(unittest.TestCase):
    def candidate(self) -> dict:
        parent, parent_sha = load_parent()
        return {
            "schema": "Venus.EDU17R1RepairCandidate.v0.1",
            "candidate_id": "TEST_SYNTHETIC_ONLY",
            "parent_carrier_id": parent["carrier_id"],
            "parent_state_sha256": parent_sha,
            "residual": "MENTION != INCIDENCE",
            "problem_statement": "synthetic contract test only",
            "discriminator": "synthetic discriminator",
            "machinery_change": {"kind": "synthetic_test_fixture"},
            "expected_changed_admissibility": "synthetic only",
            "non_goals": ["does not claim learner authorship"],
            "stop_conditions": ["stop after contract validation"],
            "implementation_identity": {
                "artifact": "tests/test_edu17r1_repair_contract.py",
                "sha256": "a" * 64,
                "version": "test-v1",
            },
            "author_controller_id": "SYNTHETIC_TEST_CONTROLLER_NOT_ADMITTED",
            "author_controller_state_sha256": "b" * 64,
            "hidden_evaluation_exposed": False,
            "external_model_supplied_substantive_repair": False,
            "promotion_authority": False,
        }

    def test_contract_binds_parent_and_residual(self):
        row = self.candidate()
        self.assertEqual(validate_candidate(row), [])
        receipt = bind_candidate(row)
        self.assertEqual(receipt["parent_carrier_id"], "EDU16-RC1")
        self.assertEqual(receipt["residual"], "MENTION != INCIDENCE")
        self.assertFalse(receipt["promotion_authority"])
        self.assertFalse(receipt["hidden_evaluation_exposed"])

    def test_external_model_authorship_fails_closed(self):
        row = self.candidate()
        row["external_model_supplied_substantive_repair"] = True
        errors = validate_candidate(row)
        self.assertTrue(any("externally supplied substantive repair" in e for e in errors))
        with self.assertRaises(DevelopmentalOwnershipError):
            bind_candidate(row)

    def test_hidden_exposure_before_authorship_fails_closed(self):
        row = self.candidate()
        row["hidden_evaluation_exposed"] = True
        errors = validate_candidate(row)
        self.assertTrue(any("before hidden #31 exposure" in e for e in errors))

    def test_wrong_parent_hash_fails_closed(self):
        row = self.candidate()
        row["parent_state_sha256"] = "0" * 64
        errors = validate_candidate(row)
        self.assertIn("candidate parent-state hash mismatch", errors)

    def test_candidate_receipt_does_not_make_synthetic_fixture_admitted(self):
        row = self.candidate()
        receipt = bind_candidate(row)
        self.assertEqual(receipt["author_controller_id"], "SYNTHETIC_TEST_CONTROLLER_NOT_ADMITTED")
        # The contract validates custody/shape only. Admission of a controller is
        # an external repository/governance fact and is intentionally not inferred.
        self.assertNotEqual(receipt["author_controller_id"], "EDU16-RC1")


if __name__ == "__main__":
    unittest.main()
