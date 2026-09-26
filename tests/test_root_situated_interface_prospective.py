from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


class RootSituatedInterfaceProspectiveTests(unittest.TestCase):
    def test_prefreeze_preserves_membrane_and_claim_fence(self):
        obj=json.loads(
            (ROOT/"kernel/development/ROOT_SITUATED_INTERFACE_PROSPECTIVE_1_PREFREEZE.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(obj["status"],"PREFROZEN_BEFORE_FRESH_PAGES_BUILD")
        inv=set(obj["noncollapse"])
        for required in (
            "DISTRIBUTED_PERCEPTION!=SITUATED_INTERPRETATION",
            "SITUATED_INTERPRETATION!=AUTHORIZATION",
            "AUTHORIZATION!=ACTION",
            "PUBLIC_CONTROL_SURFACE!=SOVEREIGN_CONTROLLER",
            "ROOT_SITUATED_INTERFACE_PASS!=BROADER_WORLD_PARTICIPATION",
        ):
            self.assertIn(required,inv)
        self.assertFalse(obj["truth_authority"])
        self.assertFalse(obj["promotion_authority"])

    def test_evaluator_cannot_promote_interface_to_action_or_agi(self):
        src=(ROOT/"scripts/evaluate_root_situated_interface_gate.py").read_text(encoding="utf-8")
        for text in (
            '"authorized_external_action_claim":False',
            '"broader_world_participation_claim":False',
            '"agi_claim":False',
            '"consciousness_claim":False',
            '"truth_authority":False',
            '"promotion_authority":False',
        ):
            self.assertIn(text,src)

    def test_pages_source_equivalence_is_explicit_not_commit_identity(self):
        obj=json.loads(
            (ROOT/"kernel/development/ROOT_SITUATED_INTERFACE_PROSPECTIVE_1_PREFREEZE.json")
            .read_text(encoding="utf-8")
        )
        carrier=obj["root_carrier"]
        self.assertNotEqual(carrier["pages_source_commit"],carrier["current_main_at_freeze"])
        self.assertTrue(carrier["relevant_surface_equivalence"]["unchanged_since_pages_source"])


if __name__=="__main__":
    unittest.main()
