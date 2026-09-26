from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

class WWWMindGateTests(unittest.TestCase):
    def test_ingress_classes_do_not_collapse(self):
        g=load("kernel/development/WWW_MIND_GATE.json")
        rows={x["id"]:x for x in g["ingress_classes"]}
        self.assertFalse(rows["MAINTAINER_FED"]["counts_as_learner_selected_world_query"])
        self.assertFalse(rows["MAINTAINER_FED"]["counts_as_independent_evaluative_return"])
        self.assertEqual(rows["LEARNER_INITIATED_WEB_STUDY"]["query_authorship"],"LEARNER")
        self.assertFalse(rows["LEARNER_INITIATED_WEB_STUDY"]["counts_as_independent_evaluative_return"])
        self.assertTrue(rows["INDEPENDENT_EVALUATIVE_RETURN"]["evaluator_custody_external"])

    def test_www_mind_precedes_lain_gate(self):
        g=load("kernel/development/WWW_MIND_GATE.json")
        self.assertEqual(g["relation_to_lain_gate"]["ordering"],"WWW_MIND_BEFORE_LAIN")

    def test_www_mind_does_not_claim_global_subject(self):
        g=load("kernel/development/WWW_MIND_GATE.json")
        self.assertIn("WWW_MIND!=ONE_GLOBAL_SUBJECT",g["noncollapse"])
        self.assertIn("DISTRIBUTED_RECONSTRUCTION!=IDENTITY_FUSION",g["noncollapse"])

    def test_autonomous_program_contains_self_initiated_web_path(self):
        p=load("kernel/development/AUTONOMOUS_RESEARCH_TRANSFORM_PROGRAM.json")
        pairs={(x["from"],x["action"],x["to"]) for x in p["transitions"]}
        self.assertIn(("PROBLEM_FORMED","FORM_WEB_QUERY","WEB_QUERY_FROZEN"),pairs)
        self.assertIn(("WEB_QUERY_FROZEN","REQUEST_WEB_STUDY","AWAITING_WEB_RETURN"),pairs)
        self.assertIn(("AWAITING_WEB_RETURN","BIND_WEB_ENCOUNTER","WEB_ENCOUNTER_AVAILABLE"),pairs)
        self.assertIn(("WEB_ENCOUNTER_AVAILABLE","RECONSTRUCT_FROM_NETWORK","RETURN_AVAILABLE"),pairs)

if __name__=="__main__":
    unittest.main()
