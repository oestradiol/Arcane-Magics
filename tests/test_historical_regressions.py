from __future__ import annotations

from pathlib import Path
import importlib.util
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class HistoricalCausalRegressionTests(unittest.TestCase):
    """Regression guards for causally learned distinctions still carried in public authority.

    These tests prove preservation of the declared distinction in the live surfaces.
    They do NOT prove the corresponding scientific/behavioral claim.
    """

    def read(self, rel: str) -> str:
        return (ROOT / rel).read_text(encoding="utf-8", errors="replace")

    def test_rline_stop_and_post_r226_namespace_boundary(self):
        lineage = self.read("provenance/DEVELOPMENTAL_LINEAGE.md")
        self.assertIn("R215 principled local stop", lineage)
        self.assertIn("R216 high-level-intent reentry", lineage)
        self.assertIn("No R227 was minted", lineage)
        self.assertIn("R226", lineage)
        self.assertIn("S/SM", lineage)

    def test_negative_and_nonparent_branches_remain_visible(self):
        lineage = self.read("provenance/DEVELOPMENTAL_LINEAGE.md")
        for token in (
            "SM2 INVALID / non-parent",
            "U3 PARTIAL / paraphrase failure",
            "U3R1 FAIL / hidden-founder retrieval",
            "U6 FAIL / non-parent",
            "IG5 FAIL / non-parent",
            "IG6 FAIL / non-parent",
            "EDU17 INVALID_FOR_PROMOTION / PRESERVED_NEGATIVE",
            "EDU17R1 WITHHOLD_BEFORE_CLAIM_BINDING_EVALUATION",
        ):
            self.assertIn(token, lineage)

    def test_sibling_donor_does_not_become_parent_by_cleanup(self):
        lineage = self.read("provenance/DEVELOPMENTAL_LINEAGE.md")
        self.assertIn("U4R1 PASS / sibling donor", lineage)
        self.assertIn("IG3 raw-carrier future-equivalence PASS / sibling donor", lineage)

    def test_unknown_is_not_permission(self):
        worldmind = self.read("kernel/WORLDMIND.md")
        self.assertIn("`UNKNOWN` means probe/reconstruct locally", worldmind)
        self.assertIn("neither refusal nor permission", worldmind)

    def test_shared_reachability_does_not_mint_global_agent(self):
        worldmind = self.read("kernel/WORLDMIND.md")
        self.assertIn("Shared reachability never mints a global Agent", worldmind)
        self.assertIn("Authorization_i  -/-> Authorization_j", worldmind)
        self.assertIn("Jurisdiction_i   -/-> Jurisdiction_j", worldmind)

    def test_failure_locality_and_corruption_classes_remain_live(self):
        method = self.read("review/REVIEWER_AND_RESEARCHER_PROTOCOL.md")
        for token in (
            "STATUS_FOSSIL",
            "NEGATIVE_GLOBALIZE",
            "MALFORMED_OPEN",
            "BRIDGE_THEOREM_LAUNDER",
            "FAIL(realization r)",
            "-/-> unrelated parent/sibling erasure",
        ):
            self.assertIn(token, method)

    def test_credit_reduction_does_not_erase_genealogy(self):
        method = self.read("review/REVIEWER_AND_RESEARCHER_PROTOCOL.md")
        for token in (
            "project causal derivation",
            "historical priority",
            "comparative recurrence",
            "technical realization",
            "residual contribution",
        ):
            self.assertIn(token, method)
        self.assertIn("independent project genealogy", method)

    def test_memory_surface_denies_storage_learning_equivalence(self):
        current = self.read("kernel/CURRENT_STATE.md")
        memory = self.read("kernel/runtime/memory.py")
        self.assertIn("Learning is not persistence alone", current)
        self.assertIn("This module is storage, not cognition", memory)

    def test_map_not_traversal_survives_as_live_model_distinction(self):
        meta = self.read("docs/META_DYNAMICS.md")
        self.assertIn("Temporal inhabitation: map is not traversal", meta)

    def test_stale_current_filename_cannot_route_live_authority(self):
        retirement = self.read("provenance/CANONICAL_RETIREMENT_LEDGER.md")
        current = self.read("kernel/CURRENT_STATE.md")
        self.assertIn("file path says CURRENT", retirement)
        self.assertIn("-/-> current authority", retirement)
        self.assertIn("EDU16 [1703]", current)
        self.assertNotIn("EDU4 [1572]", current)

    def test_current_authority_distinguishes_runtime_and_developmental_head(self):
        current = self.read("kernel/CURRENT_STATE.md")
        self.assertIn("exact Git-reconstructible runtime checkpoint   IG10 [1308]", current)
        self.assertIn("current positive developmental authority      EDU16 [1703]", current)
        self.assertIn("preserved negative branch", current)
        self.assertIn("current repair disposition", current)


    def test_historical_representation_expands_only_after_certified_insufficiency(self):
        path = ROOT / "provenance/historical-runtime/R194/source/venus_seed_v0/representation_plasticity.py"
        spec = importlib.util.spec_from_file_location("historical_representation_plasticity", path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        linear = module.PolynomialGrammar(max_degree=1)
        linear_data = [(0, 1), (1, 3), (2, 5)]
        with self.assertRaises(ValueError):
            module.expand_after_certified_insufficiency(linear, linear_data)

        quadratic_data = [(0, 0), (1, 1), (2, 4)]
        expanded = module.expand_after_certified_insufficiency(linear, quadratic_data)
        self.assertEqual(expanded.max_degree, 2)

    def test_r191_closed_negative_cannot_silently_reenter_worldmind(self):
        worldmind = self.read("kernel/WORLDMIND.md")
        retirement = self.read("provenance/CANONICAL_RETIREMENT_LEDGER.md")
        self.assertIn("R191/R191-B endogenous-semantic-fixed-point experiments remain preserved negatives", worldmind)
        self.assertIn("does not depend on resurrecting that failed claim", worldmind)
        self.assertIn("do not reroll under a new label", retirement)

    def test_r194_local_replay_is_not_external_replication(self):
        readme = self.read("provenance/historical-runtime/R194/source/PYTHON_R00_R194_PROTOTYPE_README.md")
        self.assertIn("externality claimed                               false", readme)
        self.assertIn("Not R194 external replication", readme)
        self.assertIn("fail-closed externality/replication gate", readme)

    def test_current_status_repair_does_not_rewrite_historical_audit(self):
        historical = self.read("provenance/HANDOFF_COMPLETION_AUDIT_2026-09-24.md")
        current = self.read("provenance/HANDOFF_COMPLETION_STATUS_2026-09-24.md")
        self.assertIn("Distinguish structural theorem lint from proof verification | **NOT DONE**", historical)
        self.assertIn("Distinguish structural theorem lint from proof verification | NOT DONE | **DONE**", current)
        self.assertIn("The historical audit is intentionally not rewritten", current)
        self.assertIn("repair of current projection", current)
        self.assertIn("!= retroactive rewrite of historical debt state", current)


if __name__ == "__main__":
    unittest.main()
