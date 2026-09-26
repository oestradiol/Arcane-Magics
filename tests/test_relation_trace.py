from __future__ import annotations

import json
from pathlib import Path
import unittest

from kernel.runtime.relation_trace import search_relation_trace

ROOT=Path(__file__).resolve().parents[1]
STATE=json.loads((ROOT/"kernel/development/NETWORK_SEMANTIC_TRACE_SEARCH_STATE.json").read_text(encoding="utf-8"))

class RelationTraceTests(unittest.TestCase):
    def test_relation_trace_prefers_anchor_connected_cross_source_terms(self):
        sources=(
            {"source_id":"s1","title":"memory causal abstraction","observed_relation":"memory trace preserves causal relation"},
            {"source_id":"s2","title":"lifelong memory relation","observed_relation":"memory abstraction changes lifelong retrieval"},
        )
        out=search_relation_trace(STATE,anchors=("memory","lifelong","learning"),sources=sources)
        self.assertEqual(out.status,"RELATION_TRACE_CANDIDATE_FROZEN")
        self.assertIn("abstraction",out.terms)
        row=next(x for x in out.relations if x.term=="abstraction")
        self.assertGreaterEqual(row.source_support,1)
        self.assertGreaterEqual(row.anchor_degree,1)
        self.assertFalse(out.future_return_input)
        self.assertFalse(out.hidden_evaluation_input)
        self.assertFalse(out.promotion_authority)

    def test_returned_learning_explores_less_tried_expressible_config(self):
        sources=(
            {"source_id":"s1","title":"memory causal abstraction relation","observed_relation":"memory lifelong abstraction relation"},
            {"source_id":"s2","title":"lifelong memory abstraction bridge","observed_relation":"memory lifelong abstraction bridge"},
        )
        learning={
            "trace_config_success":{"CROSS_SOURCE_BRIDGE":1},
            "trace_config_failure":{"CROSS_SOURCE_BRIDGE":1},
        }
        out=search_relation_trace(
            STATE,
            anchors=("memory","lifelong","learning"),
            sources=sources,
            learning_state=learning,
        )
        self.assertEqual(out.status,"RELATION_TRACE_CANDIDATE_FROZEN")
        self.assertNotEqual(out.config_id,"CROSS_SOURCE_BRIDGE")
        self.assertEqual(out.config_attempts,0)
        self.assertEqual(
            out.selection_basis,
            "RETURNED_UTILITY_EXPLORATION_THEN_STRUCTURAL",
        )

    def test_future_return_and_hidden_eval_are_rejected(self):
        bad={**STATE,"future_return_input":True}
        with self.assertRaisesRegex(Exception,"future return"):
            search_relation_trace(bad,anchors=("a-anchor",),sources=({"source_id":"s","title":"a-anchor bridge","observed_relation":""},))
        bad2={**STATE,"hidden_evaluation_input":True}
        with self.assertRaisesRegex(Exception,"hidden evaluation"):
            search_relation_trace(bad2,anchors=("a-anchor",),sources=({"source_id":"s","title":"a-anchor bridge","observed_relation":""},))

    def test_executor_contains_no_project_answer_vocabulary(self):
        text=(ROOT/"kernel/runtime/relation_trace.py").read_text(encoding="utf-8").lower()
        for forbidden in ("venusmemory","worldmind","lateralizer","issue #15","semantic trace answer"):
            self.assertNotIn(forbidden,text)

if __name__=="__main__":
    unittest.main()
