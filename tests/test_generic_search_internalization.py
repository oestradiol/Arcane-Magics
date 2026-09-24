from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from kernel.runtime.internalized_search import Observation, search
from kernel.runtime.internalizer import SubstrateRole, internalize, make_artifact


ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "kernel/development/GENERIC_RESIDUAL_SEARCH_INTERNALIZED_STATE.json"


class GenericSearchConsumptionTests(unittest.TestCase):
    def setUp(self):
        self.state = json.loads(STATE.read_text(encoding="utf-8"))

    def test_post_consumption_executor_has_no_donor_or_scaffold_dependency(self):
        import kernel.runtime.internalized_search as mod
        src = inspect.getsource(mod)
        self.assertNotIn("recursive_proposal", src)
        self.assertNotIn("grammar_expansion", src)
        self.assertNotIn("historical-runtime", src)

    def test_internalized_state_reproduces_unique_xor_capability(self):
        rows = (
            Observation((0, 0), 0, "world-1"),
            Observation((0, 1), 1, "world-2"),
            Observation((1, 0), 1, "world-3"),
            Observation((1, 1), 0, "world-4"),
        )
        out = search(self.state["program"], rows)
        self.assertEqual(out.status, "UNIQUE_BOUNDED_PROGRAM_CANDIDATE")
        self.assertEqual(len(out.candidates), 1)

    def test_internalized_state_withholds_when_return_is_insufficient(self):
        out = search(
            self.state["program"],
            (Observation((0, 0), 0, "world-1"),),
        )
        self.assertTrue(out.status.startswith("WITHHOLD_"))
        self.assertIsNotNone(out.next_discriminator)

    def test_internalization_receipt_keeps_world_and_authority_external(self):
        scaffold = make_artifact(
            role=SubstrateRole.SCAFFOLD,
            payload={
                "source": self.state["origin"]["source"],
                "donor_git_blob_sha": self.state["origin"]["donor_git_blob_sha"],
            },
            source_id="git-scaffold",
            provenance_ids=("R194-grammar", "PR85-generic-search"),
        )
        receipt = internalize(
            scaffold,
            internalized_capability_payload=self.state,
            original_scaffold_removed=True,
            function_preserved_after_removal=True,
            fresh_world_return_required=True,
        )
        self.assertTrue(receipt.original_scaffold_removed)
        self.assertTrue(receipt.function_preserved_after_removal)
        self.assertTrue(receipt.fresh_world_return_required)
        self.assertFalse(receipt.authority_inherited)
        self.assertFalse(receipt.jurisdiction_inherited)
        self.assertFalse(receipt.evaluator_independence_inherited)

    def test_hidden_evaluation_remains_nonconsumable(self):
        with self.assertRaises(Exception):
            search(
                self.state["program"],
                (
                    Observation((0, 0), 0, "world-1"),
                    Observation((1, 1), 0, "world-2"),
                ),
                hidden_evaluation_exposed=True,
            )


if __name__ == "__main__":
    unittest.main()
