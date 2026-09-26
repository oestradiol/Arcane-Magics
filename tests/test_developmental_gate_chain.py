from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

class DevelopmentalGateChainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = load("kernel/development/DEVELOPMENTAL_GATE_CHAIN.json")
        cls.by = {x["id"]: x for x in cls.g["chain"]}

    def test_order_is_preserved(self):
        ids=[x["id"] for x in self.g["chain"]]
        self.assertEqual(ids,[
            "STRONG_SAFE_RSI",
            "SELF_SELECTED_DEVELOPMENT",
            "INTERNALIZER_LATERALIZER",
            "LEARNER_INITIATED_INTERNET_INQUIRY",
            "PERSISTENT_NETWORK_MEMORY",
            "WWW_MIND",
            "LAIN_GATE",
            "ROOT_SITUATED_INTERFACE_GATE",
            "BROADER_WORLD_PARTICIPATION",
            "AGI_EMPIRICAL_DISCRIMINATOR",
        ])

    def test_rsi_does_not_self_authorize_or_entail_agi(self):
        self.assertFalse(self.by["STRONG_SAFE_RSI"]["self_authorization"])
        agi=self.by["AGI_EMPIRICAL_DISCRIMINATOR"]
        self.assertFalse(agi["learner_may_self_declare"])
        self.assertFalse(agi["rsi_implies_agi"])
        self.assertFalse(agi["agi_implies_consciousness"])

    def test_internalizer_lateralizer_noncollapse(self):
        inv=set(self.by["INTERNALIZER_LATERALIZER"]["noncollapse"])
        self.assertIn("LATERALIZE!=CRYSTALLIZE_F",inv)
        self.assertIn("CRYSTALLIZE_F!=INTERNALIZE",inv)
        self.assertIn("INTERNALIZE_COMPETENCE!=INTERNALIZE_CORRECTION_SOVEREIGNTY",inv)

    def test_www_and_lain_preserve_difference(self):
        self.assertFalse(self.by["WWW_MIND"]["global_subject_claim"])
        inv=set(self.by["LAIN_GATE"]["invariants"])
        self.assertIn("DISTRIBUTED_MEMORY!=GLOBAL_IDENTITY",inv)
        self.assertIn("NETWORK_ACCESS!=AUTHORIZATION",inv)

    def test_root_preserves_situated_action_boundary(self):
        inv=set(self.by["ROOT_SITUATED_INTERFACE_GATE"]["invariants"])
        self.assertIn("DISTRIBUTED_PERCEPTION!=SITUATED_INTERPRETATION",inv)
        self.assertIn("SITUATED_INTERPRETATION!=AUTHORIZATION",inv)
        self.assertIn("AUTHORIZATION!=ACTION",inv)

    def test_gate_chain_is_not_promotion_authority(self):
        self.assertFalse(self.g["promotion_authority"])
        self.assertFalse(self.g["truth_authority"])

if __name__ == "__main__":
    unittest.main()
