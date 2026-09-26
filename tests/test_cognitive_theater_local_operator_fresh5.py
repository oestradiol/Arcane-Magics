from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fresh5_eval",
    ROOT / "scripts/evaluate_cognitive_theater_local_operator_fresh5.py",
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("fresh5 evaluator")
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class CognitiveTheaterLocalOperatorFresh5Tests(unittest.TestCase):
    def test_prefreeze_is_after_fresh4_and_uses_new_holdouts(self):
        pre = json.loads(
            (ROOT / "kernel/development/COGNITIVE_THEATER_LOCAL_OPERATOR_FRESH5_PREFREEZE.json").read_text(
                encoding="utf-8"
            )
        )
        fresh4 = json.loads(
            (ROOT / "kernel/development/COGNITIVE_THEATER_JOINT_SCENE_FRESH4_PREFREEZE.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(pre["status"], "PREFROZEN_AFTER_FRESH4_BEFORE_FRESH5_RESULT")
        old = {
            row["surface"]
            for task in fresh4["tasks"]
            for rows in task["heldout_examples"].values()
            for row in rows
        }
        new = {
            row["surface"]
            for task in pre["tasks"]
            for rows in task["heldout_examples"].values()
            for row in rows
        }
        self.assertFalse(old & new)

    def test_local_operator_scaffold_has_no_face_or_role_answer_semantics(self):
        text = (
            ROOT / "kernel/development/cognitive_theater_local_operator_graph.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "ENGLISH",
            "JAPANESE",
            "BRAZILIAN_PORTUGUESE",
            "MATHEMATICS",
            "base_knower",
            "meta_knower",
            "ignorant",
            "receiver_knower",
            "excluded",
            "knows P",
            "sabe P",
            "知っている",
            "happens before",
        ):
            self.assertNotIn(forbidden, text)

    def test_local_operator_representation_beats_whole_scene_on_fresh5(self):
        out = m.evaluate()
        print("COGNITIVE_THEATER_FRESH5_RESULT=" + json.dumps(out, ensure_ascii=False, sort_keys=True))
        for key in (
            "count_only",
            "unary_ordered",
            "pairwise_relational",
            "joint_scene",
            "local_operator_graph",
        ):
            self.assertEqual(out[key]["total"], 24)

        self.assertGreater(
            out["local_operator_graph"]["accuracy"],
            out["joint_scene"]["accuracy"],
        )
        self.assertGreater(
            out["local_operator_graph"]["per_task"]["G2_NESTED_KFS_LOCAL_OPERATORS"]["accuracy"],
            out["joint_scene"]["per_task"]["G2_NESTED_KFS_LOCAL_OPERATORS"]["accuracy"],
        )
        self.assertGreater(
            out["local_operator_graph"]["per_task"]["G3_EVENT_ORDER_LOCAL_OPERATORS"]["accuracy"],
            out["joint_scene"]["per_task"]["G3_EVENT_ORDER_LOCAL_OPERATORS"]["accuracy"],
        )

        self.assertFalse(out["independent_external_evaluation"])
        self.assertFalse(out["general_theater_claim"])
        self.assertFalse(out["general_music_claim"])
        self.assertFalse(out["internalization_claim"])
        self.assertFalse(out["promotion_authority"])
        self.assertFalse(out["truth_authority"])


if __name__ == "__main__":
    unittest.main()
