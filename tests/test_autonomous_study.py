from __future__ import annotations

import unittest

from kernel.development.autonomous_study import study_target


def cycle(kind="PR", number=7):
    return {
        "cycle_id": "c",
        "target_kind": kind,
        "target_number": number,
        "related_paths": ["kernel/runtime/ctl.py", "tests/test_ctl.py"],
    }


class AutonomousStudyTests(unittest.TestCase):
    def test_failed_pr_returns_repair_disposition(self):
        out = study_target(
            cycle=cycle(),
            target={
                "mergeStateStatus": "CLEAN",
                "files": [{"path": "kernel/x.py"}],
                "statusCheckRollup": [
                    {"name": "tests", "status": "COMPLETED", "conclusion": "FAILURE"}
                ],
                "reviews": [],
            },
        )
        self.assertEqual(out.disposition, "REPAIR_RETURNED_FAILURE")
        self.assertEqual(out.failed_checks, ("tests",))
        self.assertFalse(out.promotion_authority)
        self.assertFalse(out.merge_authority)

    def test_pending_ci_cannot_be_treated_as_evaluated(self):
        out = study_target(
            cycle=cycle(),
            target={
                "mergeStateStatus": "CLEAN",
                "statusCheckRollup": [
                    {"name": "formal", "status": "IN_PROGRESS", "conclusion": None}
                ],
            },
        )
        self.assertEqual(out.disposition, "WAIT_EXTERNAL_RETURN")
        self.assertEqual(out.pending_checks, ("formal",))

    def test_conflict_reopens_when_no_failed_or_pending_check(self):
        out = study_target(
            cycle=cycle(),
            target={"mergeStateStatus": "CONFLICTING", "statusCheckRollup": []},
        )
        self.assertEqual(out.disposition, "REOPEN_STRUCTURAL_CONFLICT")

    def test_clean_pr_still_requires_claim_review_not_merge(self):
        out = study_target(
            cycle=cycle(),
            target={"mergeStateStatus": "CLEAN", "statusCheckRollup": [], "reviews": []},
        )
        self.assertEqual(out.disposition, "PROBE")
        self.assertTrue(any("claim/evidence/provenance" in x for x in out.next_discriminators))

    def test_issue_study_reconstructs_before_claiming_resolution(self):
        out = study_target(
            cycle=cycle("ISSUE", 31),
            target={"body": "mention != incidence", "comments": [{}, {}], "labels": [{}]},
        )
        self.assertEqual(out.disposition, "PROBE")
        self.assertTrue(any("smallest unresolved causal distinction" in x for x in out.next_discriminators))


if __name__ == "__main__":
    unittest.main()
