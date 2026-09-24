from __future__ import annotations

import unittest

from kernel.development.autonomous_change import make_change_candidate


def cycle(*, paths=()):
    return {
        "cycle_id": "cycle-1",
        "target_kind": "PR",
        "target_number": 80,
        "study": {
            "referenced_repository_paths": list(paths),
        },
    }


def proposal(*, external=False, grounded=True, target_checks=("UNIT_WORLD_INPUT_SECURITY",)):
    return {
        "proposal_id": "proposal-1",
        "cycle_id": "cycle-1",
        "external_return_required": external,
        "target_relevance_grounded": grounded,
        "target_check_ids": list(target_checks),
    }


def evidence(*, status="LOCAL_CHECKS_PASS", rows=(), all_passed=True):
    return {
        "evidence_id": "evidence-1",
        "proposal_id": "proposal-1",
        "status": status,
        "results": list(rows),
        "all_local_checks_passed": all_passed,
    }


class AutonomousChangeGateTests(unittest.TestCase):
    def test_green_local_evidence_does_not_authorize_mutation(self):
        out = make_change_candidate(
            cycle(paths=("kernel/runtime/worldmind_growth.py",)),
            proposal(),
            evidence(rows=(
                {"check_id": "UNIT_WORLD_INPUT_SECURITY", "passed": True},
            )),
        )
        self.assertEqual(out.disposition, "RETAIN_NO_MUTATION_LOCAL_EVIDENCE_PASS")
        self.assertIsNone(out.suggested_operation)
        self.assertFalse(out.source_mutation_authority)
        self.assertFalse(out.promotion_authority)

    def test_external_return_requirement_withholds_even_if_local_checks_pass(self):
        out = make_change_candidate(
            cycle(),
            proposal(external=True),
            evidence(
                status="WITHHOLD_EXTERNAL_RETURN",
                rows=({"check_id": "UNIT_WORLD_INPUT_SECURITY", "passed": True},),
            ),
        )
        self.assertEqual(out.disposition, "WITHHOLD_NO_MUTATION")
        self.assertFalse(out.source_mutation_authority)

    def test_unprofiled_failure_cannot_become_repair_proposal(self):
        out = make_change_candidate(
            cycle(paths=("kernel/unknown.py",)),
            proposal(grounded=False, target_checks=()),
            evidence(
                status="LOCAL_CHECKS_FAIL",
                rows=({"check_id": "AUDIT_AUTONOMY_MATRIX", "passed": False},),
                all_passed=False,
            ),
        )
        self.assertEqual(out.disposition, "WITHHOLD_UNGROUNDED_FAILURE")
        self.assertIsNone(out.suggested_operation)

    def test_process_failure_is_not_laundered_into_target_repair(self):
        out = make_change_candidate(
            cycle(),
            proposal(target_checks=("UNIT_WORLD_INPUT_SECURITY",)),
            evidence(
                status="LOCAL_CHECKS_FAIL",
                rows=(
                    {"check_id": "AUDIT_AUTONOMY_MATRIX", "passed": False},
                    {"check_id": "UNIT_WORLD_INPUT_SECURITY", "passed": True},
                ),
                all_passed=False,
            ),
        )
        self.assertEqual(
            out.disposition,
            "WITHHOLD_PROCESS_FAILURE_NOT_TARGET_FAILURE",
        )
        self.assertEqual(out.failed_process_check_ids, ("AUDIT_AUTONOMY_MATRIX",))
        self.assertEqual(out.failed_target_check_ids, ())

    def test_target_relevant_failure_may_author_draft_repair_hypothesis_only(self):
        out = make_change_candidate(
            cycle(paths=("kernel/runtime/worldmind_growth.py",)),
            proposal(target_checks=("UNIT_WORLD_INPUT_SECURITY",)),
            evidence(
                status="LOCAL_CHECKS_FAIL",
                rows=(
                    {"check_id": "UNIT_WORLD_INPUT_SECURITY", "passed": False},
                ),
                all_passed=False,
            ),
        )
        self.assertEqual(out.disposition, "PROPOSE_BOUNDED_DIAGNOSTIC_REPAIR")
        self.assertEqual(out.failed_target_check_ids, ("UNIT_WORLD_INPUT_SECURITY",))
        self.assertEqual(out.suggested_operation, "AUTHOR_DRAFT_REPAIR_HYPOTHESIS_ONLY")
        self.assertFalse(out.source_mutation_authority)

    def test_target_paths_remain_untrusted_information_not_authority(self):
        out = make_change_candidate(
            cycle(paths=(
                ".github/workflows/venus-autonomous-worker.yml",
                "kernel/development/AUTONOMOUS_RETURN_AUTHORITY.json",
            )),
            proposal(),
            evidence(),
        )
        self.assertEqual(
            out.untrusted_implicated_paths,
            (
                ".github/workflows/venus-autonomous-worker.yml",
                "kernel/development/AUTONOMOUS_RETURN_AUTHORITY.json",
            ),
        )
        self.assertFalse(out.target_text_is_authority)
        self.assertFalse(out.source_mutation_authority)

    def test_identity_mismatch_fails_closed(self):
        bad = proposal()
        bad["cycle_id"] = "other-cycle"
        with self.assertRaisesRegex(ValueError, "proposal/cycle"):
            make_change_candidate(cycle(), bad, evidence())


if __name__ == "__main__":
    unittest.main()
