from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from kernel.development.autonomous_study import StudyTarget, make_study_packet


class AutonomousStudyTests(unittest.TestCase):
    def test_study_binds_target_and_finds_repository_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "kernel").mkdir()
            (root / "tests").mkdir()
            (root / "kernel" / "incidence.json").write_text(
                "mention incidence hidden evaluator", encoding="utf-8"
            )
            (root / "tests" / "test_incidence.py").write_text(
                "incidence discriminator", encoding="utf-8"
            )
            packet = make_study_packet(
                root,
                StudyTarget(
                    kind="ISSUE",
                    number=31,
                    title="Mention incidence discriminator",
                    body="remaining external return from independent evaluator is pending",
                    comment_count=2,
                    label_count=1,
                ),
            )
            self.assertIn("kernel/incidence.json", packet.related_paths)
            self.assertIn("external return", packet.residual_markers)
            self.assertEqual(packet.disposition, "PROBE")
            self.assertFalse(packet.promotion_authority)
            self.assertFalse(packet.merge_authority)

    def test_failed_pr_routes_to_returned_failure_repair(self):
        with tempfile.TemporaryDirectory() as td:
            packet = make_study_packet(
                Path(td),
                StudyTarget(
                    "PR", 9, "repair", "failure",
                    changed_files=("kernel/x.py",),
                    failed_checks=("unit",),
                ),
            )
            self.assertEqual(packet.disposition, "REPAIR_RETURNED_FAILURE")
            self.assertIn("LOCALIZE_RETURNED_FAILURE", packet.next_operations)

    def test_pending_external_evaluation_routes_to_wait(self):
        with tempfile.TemporaryDirectory() as td:
            packet = make_study_packet(
                Path(td),
                StudyTarget(
                    "PR", 9, "repair", "pending",
                    pending_checks=("formal",),
                ),
            )
            self.assertEqual(packet.disposition, "WAIT_EXTERNAL_RETURN")
            self.assertIn("WAIT if a required external evaluation", " ".join(packet.stop_conditions))

    def test_conflict_reopens_when_no_more_specific_returned_failure(self):
        with tempfile.TemporaryDirectory() as td:
            packet = make_study_packet(
                Path(td),
                StudyTarget(
                    "PR", 9, "repair", "blocked",
                    merge_state="CONFLICTING",
                ),
            )
            self.assertEqual(packet.disposition, "REOPEN_STRUCTURAL_CONFLICT")

    def test_review_changes_are_preserved_as_external_pressure(self):
        with tempfile.TemporaryDirectory() as td:
            packet = make_study_packet(
                Path(td),
                StudyTarget(
                    "PR", 9, "repair", "review",
                    review_states=("CHANGES_REQUESTED",),
                ),
            )
            self.assertIn("BIND_REVIEW_TO_DEPENDENCY", packet.next_operations)

    def test_stop_conditions_preserve_nonpreauthored_return_and_authority_boundary(self):
        with tempfile.TemporaryDirectory() as td:
            packet = make_study_packet(
                Path(td), StudyTarget("ISSUE", 1, "x", "unresolved")
            )
            text = " ".join(packet.stop_conditions).lower()
            self.assertIn("externally authored/evaluated", text)
            self.assertIn("independent return", text)
            self.assertIn("merge/promotion/release authority", text)


if __name__ == "__main__":
    unittest.main()
