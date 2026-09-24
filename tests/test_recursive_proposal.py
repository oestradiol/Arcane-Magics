from pathlib import Path
import json
import tempfile
import unittest

from kernel.development.recursive_proposal import (
    RecursiveProposalError,
    derive_mismatches,
    generate_candidate,
    load_typed_residual,
    select_family,
)
from kernel.development.edu17r1_repair_contract import validate_candidate


class RecursiveProposalTests(unittest.TestCase):
    def test_current_residual_selects_relation_binding(self):
        residual = load_typed_residual()
        self.assertEqual(derive_mismatches(residual), ("surface_without_target_relation",))
        self.assertEqual(select_family(residual).id, "RELATION_BINDING")

    def test_generated_candidate_satisfies_ownership_contract(self):
        candidate = generate_candidate()
        self.assertEqual(validate_candidate(candidate), [])
        self.assertEqual(candidate["author_controller_id"], "EDU16-RC1::RECURSIVE_PROPOSAL_V0.1")
        self.assertFalse(candidate["hidden_evaluation_exposed"])
        self.assertFalse(candidate["external_model_supplied_substantive_repair"])
        self.assertFalse(candidate["promotion_authority"])
        self.assertEqual(candidate["machinery_change"]["kind"], "typed_relation_admission_gate")

    def test_surface_label_is_not_part_of_repair_selection(self):
        residual = load_typed_residual()
        changed = json.loads(json.dumps(residual))
        changed["distinction"] = "arbitrary renamed surface symbol != arbitrary target relation"
        changed["returned_failure"] = "renamed prose"
        self.assertEqual(select_family(changed).id, "RELATION_BINDING")

    def test_no_live_mismatch_stops(self):
        residual = load_typed_residual()
        residual = json.loads(json.dumps(residual))
        residual["observations"]["required_target_relation_present"] = True
        with self.assertRaisesRegex(RecursiveProposalError, "STOP_NO_LIVE_REPAIR_MISMATCH"):
            select_family(residual)

    def test_multiple_axes_withhold(self):
        residual = load_typed_residual()
        residual = json.loads(json.dumps(residual))
        residual["observations"]["source_binding_present"] = False
        with self.assertRaisesRegex(RecursiveProposalError, "WITHHOLD_MULTI_AXIS_REPAIR_AMBIGUITY"):
            select_family(residual)

    def test_hidden_exposure_fails_closed(self):
        residual = load_typed_residual()
        residual["hidden_evaluation_exposed"] = True
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "residual.json"
            p.write_text(json.dumps(residual), encoding="utf-8")
            with self.assertRaisesRegex(RecursiveProposalError, "hidden evaluation"):
                generate_candidate(residual_path=p)


if __name__ == "__main__":
    unittest.main()
