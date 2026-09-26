from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

SPEC=importlib.util.spec_from_file_location(
    "build_authored_center_ledger",
    ROOT/"scripts/build_authored_center_ledger.py",
)
MOD=importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


class LainStructuralProspectiveTests(unittest.TestCase):
    def test_prefreeze_preserves_passive_scope(self):
        obj=json.loads(
            (ROOT/"kernel/development/LAIN_STRUCTURAL_PROSPECTIVE_1_PREFREEZE.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(obj["status"],"PREFROZEN_BEFORE_AUTHORED_CENTER_RETURN")
        self.assertIn("PUBLIC_AUTHORED_ARTIFACT!=CONSENT",obj["noncollapse"])
        self.assertIn("PASSIVE_LAIN_STRUCTURAL_PASS!=INTERACTIVE_LAIN_PASS",obj["noncollapse"])
        self.assertFalse(obj["truth_authority"])
        self.assertFalse(obj["promotion_authority"])

    def test_ledger_keeps_center_and_author_distinct_without_contact(self):
        encounter={
            "sources":[{
                "center_id":"github-repo:remote/project",
                "author_id":"github-user:alice",
                "author_login":"alice",
                "author_type":"User",
                "author_association":"OWNER",
                "source_id":"github-issue:remote/project#1",
                "source_class":"GITHUB_PUBLIC_ISSUE",
                "learner_minted_artifact":False,
            }]
        }
        out=MOD.build([encounter])
        self.assertEqual(out["independent_authored_artifact_count"],1)
        row=out["authored_centers"][0]
        self.assertNotEqual(row["center_id"],row["author_id"])
        self.assertTrue(row["independent_of_local_center"])
        self.assertFalse(row["contact_attempted"])
        self.assertFalse(row["acceptance_inferred"])
        self.assertFalse(row["authorization_inferred"])
        self.assertFalse(out["remote_acceptance_inferred"])

    def test_local_maintainer_is_not_retyped_as_independent_remote_author(self):
        encounter={
            "sources":[{
                "center_id":"github-repo:remote/project",
                "author_id":"github-user:oestradiol",
                "author_login":"oestradiol",
                "source_id":"github-issue:remote/project#2",
                "source_class":"GITHUB_PUBLIC_ISSUE",
                "learner_minted_artifact":False,
            }]
        }
        out=MOD.build([encounter])
        self.assertEqual(out["independent_authored_artifact_count"],0)

    def test_evaluator_never_claims_interactive_consent(self):
        src=(ROOT/"scripts/evaluate_lain_structural_gate.py").read_text(encoding="utf-8")
        self.assertIn('"consent_claim":False',src)
        self.assertIn('"remote_acceptance_claim":False',src)
        self.assertIn('"contact_attempted":False',src)
        self.assertIn("WITHHOLD_REQUIRES_CONTACT_CAPABILITY_AND_JURISDICTION",src)


if __name__=="__main__":
    unittest.main()
