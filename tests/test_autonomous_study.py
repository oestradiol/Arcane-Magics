from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from kernel.development.autonomous_study import StudyTarget, make_study_packet


class AutonomousStudyTests(unittest.TestCase):
    def test_study_packet_binds_target_and_finds_related_evidence(self):
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
                ),
            )
            self.assertTrue(packet.study_id)
            self.assertIn("kernel/incidence.json", packet.related_paths)
            self.assertIn("external return", packet.residual_markers)
            self.assertFalse(packet.promotion_authority)

    def test_study_packet_preserves_pr_changed_files(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            packet = make_study_packet(
                root,
                StudyTarget("PR", 9, "repair", "blocked residual", ("kernel/x.py",)),
            )
            self.assertEqual(packet.changed_files, ("kernel/x.py",))
            self.assertIn("STUDY_PATCH", packet.next_operations)

    def test_stop_conditions_preserve_external_return_boundary(self):
        with tempfile.TemporaryDirectory() as td:
            packet = make_study_packet(
                Path(td), StudyTarget("ISSUE", 1, "x", "unresolved")
            )
            text = " ".join(packet.stop_conditions).lower()
            self.assertIn("externally authored/evaluated", text)
            self.assertIn("independent return", text)
            self.assertIn("withhold", text)


if __name__ == "__main__":
    unittest.main()
