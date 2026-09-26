from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fresh6_eval",
    ROOT / "scripts/evaluate_cognitive_theater_explicit_state_fresh6.py",
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("fresh6 evaluator")
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class CognitiveTheaterExplicitStateFresh6Tests(unittest.TestCase):
    def test_prefreeze_hides_task_and_relation_identity_at_evaluation(self):
        pre = json.loads(
            (ROOT / "kernel/development/COGNITIVE_THEATER_EXPLICIT_STATE_FRESH6_PREFREEZE.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(pre["evaluation_input"], ["face_id", "raw_surface_only"])
        self.assertIn("task_id", pre["forbidden_evaluation_inputs"])
        self.assertIn("relation_id", pre["forbidden_evaluation_inputs"])
        self.assertIn("teacher_state_target", pre["forbidden_evaluation_inputs"])

    def test_composer_source_has_no_face_or_role_semantics(self):
        text = (
            ROOT / "kernel/development/cognitive_theater_state_composer.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "ENGLISH",
            "JAPANESE",
            "BRAZILIAN_PORTUGUESE",
            "MATHEMATICS",
            "base_knower",
            "meta_knower",
            "receiver_knower",
            "excluded",
            "knows P",
            "sabe P",
            "知っている",
            "happens before",
            "relation_id",
        ):
            self.assertNotIn(forbidden, text)

    def test_explicit_state_discriminator_and_interventions(self):
        out = m.evaluate()
        print("COGNITIVE_THEATER_FRESH6_RESULT=" + json.dumps(out, ensure_ascii=False, sort_keys=True))

        self.assertEqual(out["total"], 24)
        self.assertGreater(
            out["task_binding_accuracy"],
            out["joint_task_binding_accuracy"],
        )
        self.assertGreaterEqual(out["explicit_state_accuracy"], 22 / 24)
        self.assertEqual(
            out["gauge_pairs_identical_state"],
            out["gauge_pairs_total"],
        )
        self.assertTrue(all(x["endpoint_changed"] for x in out["kfs_interventions"]))
        self.assertTrue(out["history_intervention"]["same_endpoint"])
        self.assertTrue(out["history_intervention"]["history_changed"])

        self.assertFalse(out["task_id_visible_at_evaluation"])
        self.assertFalse(out["relation_id_visible_at_evaluation"])
        self.assertFalse(out["teacher_state_target_visible_at_evaluation"])
        self.assertFalse(out["independent_external_evaluation"])
        self.assertFalse(out["source_removal_pass"])
        self.assertFalse(out["general_theater_claim"])
        self.assertFalse(out["general_music_claim"])
        self.assertFalse(out["internalization_claim"])
        self.assertFalse(out["promotion_authority"])
        self.assertFalse(out["truth_authority"])


if __name__ == "__main__":
    unittest.main()
