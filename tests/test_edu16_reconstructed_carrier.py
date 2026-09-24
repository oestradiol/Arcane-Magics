from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "kernel" / "development" / "replay_edu16_reconstructed.py"
STATE_PATH = ROOT / "kernel" / "development" / "EDU16_RECONSTRUCTED_STATE.json"
MANIFEST_PATH = ROOT / "kernel" / "development" / "EDU16_RECONSTRUCTED_CARRIER_MANIFEST.json"


def load_module():
    spec = importlib.util.spec_from_file_location("edu16_reconstructed_replay", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class EDU16ReconstructedCarrierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()
        cls.state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_exact_reconstruction_matches_committed_state(self):
        state, digest = self.mod.replay()
        self.assertEqual(state, self.state)
        self.assertEqual(
            digest,
            self.manifest["expected_reconstructed_state_sha256"],
        )

    def test_restart_is_exact(self):
        first, first_digest = self.mod.replay()
        second, second_digest = self.mod.replay()
        self.assertEqual(first, second)
        self.assertEqual(first_digest, second_digest)

    def test_historical_event_replay_is_not_fabricated(self):
        historical = self.state["historical_equivalence"]
        self.assertFalse(historical["event_level_journal_equivalent"])
        self.assertFalse(historical["original_runner_recovered"])
        self.assertFalse(historical["original_journal_recovered"])
        self.assertEqual(historical["record_count"], 1703)
        self.assertEqual(len(self.state["checkpoints"]), 5)

    def test_world_and_evaluation_remain_external(self):
        policy = self.state["world_feed_policy"]
        self.assertEqual(policy["world_execution_owner"], "EXTERNAL_WORLD_INTERFACE")
        self.assertEqual(policy["evaluation_owner"], "INDEPENDENT_EVALUATOR")
        self.assertFalse(self.state["promotion_authority"])

    def test_source_vector_is_content_addressed(self):
        self.mod.verify_source_custody(self.manifest)
        self.assertEqual(
            self.mod.source_vector_sha256(self.manifest),
            self.manifest["source_vector_sha256"],
        )


if __name__ == "__main__":
    unittest.main()
