from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_self_sealing.py"
SCOPE_PATH = ROOT / "kernel/development/SELF_SEALING_AUDIT_SCOPE.json"

_spec = importlib.util.spec_from_file_location("self_sealing", SCRIPT)
if _spec is None or _spec.loader is None:
    raise RuntimeError("cannot load self-sealing auditor")
audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(audit)


class ScopeDeclarationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope = json.loads(SCOPE_PATH.read_text(encoding="utf-8"))

    def test_scope_is_candidate_without_authority(self):
        self.assertEqual(self.scope["status"], "CANDIDATE_NOT_ADMITTED")
        self.assertFalse(self.scope["promotion_authority"])
        self.assertFalse(self.scope["truth_authority"])

    def test_guarded_checkers_and_guards_exist_on_branch(self):
        for row in self.scope["guarded"]:
            with self.subTest(checker=row["checker"]):
                self.assertTrue(
                    (ROOT / row["checker"]).exists(),
                    f"declared checker absent: {row['checker']}",
                )
            for guard in row["guards"]:
                with self.subTest(guard=guard):
                    self.assertTrue(
                        (ROOT / guard).exists(),
                        f"declared guarded artifact absent: {guard}",
                    )

    def test_fence_surfaces_exist_on_branch(self):
        for path in self.scope["fence_surfaces"]:
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).exists())

    def test_every_declared_residual_carries_a_reopening_condition(self):
        # A residual without a reopening condition is not a residual; it is a
        # silent compression wearing a residual's name.
        for row in self.scope["declared_residuals"]:
            with self.subTest(key=row["key"]):
                self.assertIn("key", row)
                self.assertTrue(row.get("reopening_condition", "").strip())
                self.assertIn(
                    row.get("class"),
                    {"UNADJUDICATED", "CONTAMINATION_ATTESTED_AND_REVERTED"},
                )

    def test_declared_residual_keys_are_unique(self):
        keys = [row["key"] for row in self.scope["declared_residuals"]]
        self.assertEqual(len(keys), len(set(keys)))

    def test_admitted_exceptions_state_a_reason_and_independent_check(self):
        for row in self.scope.get("admitted_exceptions", []):
            with self.subTest(prefix=row.get("commit_subject_prefix")):
                self.assertTrue(row.get("reason", "").strip())
                self.assertTrue(row.get("rules_waived"))

    def test_known_contamination_is_declared_not_erased(self):
        keys = {row["key"] for row in self.scope["declared_residuals"]}
        self.assertIn("R2_FENCE_REMOVAL|AGENTS.md|3d9dc269", keys)
        self.assertIn(
            "R1_SELF_SEALING|scripts/lint_github_markdown.py|cda936eb", keys
        )


class EpisodeGroupingTests(unittest.TestCase):
    @staticmethod
    def commit(sha: str, author: str, when: int) -> object:
        return audit.Commit(sha, author, when, f"subject {sha}")

    def test_gap_longer_than_threshold_starts_a_new_episode(self):
        commits = [
            self.commit("a", "X", 0),
            self.commit("b", "X", 100),
            self.commit("c", "X", 100 + 1801),
        ]
        episodes = audit.group_episodes(commits, 1800)
        self.assertEqual([len(e) for e in episodes], [2, 1])

    def test_author_change_starts_a_new_episode(self):
        commits = [
            self.commit("a", "X", 0),
            self.commit("b", "Y", 10),
        ]
        self.assertEqual(len(audit.group_episodes(commits, 1800)), 2)

    def test_the_real_contamination_gap_separates_episodes(self):
        # 13:04:46 -> 13:32:10 is 1644s, inside the default window, so the
        # detector must not rely on the gap alone; it relies on co-modification.
        commits = [
            self.commit("good", "Elaina", 0),
            self.commit("bad", "Elaina", 1644),
        ]
        self.assertEqual(len(audit.group_episodes(commits, 1800)), 1)


class HelperTests(unittest.TestCase):
    def test_normalize_folds_typographic_fence_forms(self):
        self.assertEqual(audit.normalize("a ≠ b"), "a != b")
        self.assertEqual(audit.normalize("x → y"), "x -> y")

    def test_is_prefrozen_matches_declared_markers(self):
        markers = ["_PREFREEZE.json"]
        self.assertTrue(audit.is_prefrozen("kernel/x_PREFREEZE.json", markers))
        self.assertFalse(audit.is_prefrozen("kernel/x.json", markers))

    def test_waiver_requires_both_subject_match_and_rule(self):
        commit = audit.Commit("s", "A", 0, "revert(minerva): undo something")
        exceptions = [
            {
                "commit_subject_prefix": "revert(minerva): undo",
                "rules_waived": ["R2_FENCE_REMOVAL"],
            }
        ]
        self.assertTrue(audit.waived(commit, "R2_FENCE_REMOVAL", exceptions))
        self.assertFalse(audit.waived(commit, "R1_SELF_SEALING", exceptions))

    def test_unrelated_subject_is_not_waived(self):
        commit = audit.Commit("s", "A", 0, "feat: something else")
        exceptions = [
            {
                "commit_subject_prefix": "revert(minerva): undo",
                "rules_waived": ["R2_FENCE_REMOVAL"],
            }
        ]
        self.assertFalse(audit.waived(commit, "R2_FENCE_REMOVAL", exceptions))


class FenceCoverageTests(unittest.TestCase):
    """The fences the 2026-09-26 episode deleted must all be watched."""

    def test_deleted_fences_are_all_declared_tokens(self):
        scope = json.loads(SCOPE_PATH.read_text(encoding="utf-8"))
        tokens = {audit.normalize(t) for t in scope["fence_tokens"]}
        for lost in (
            "external model != Minerva",
            "can inspect != can claim",
            "self-implication != self-certification",
            "re-derivation != memory lookup",
            "current Perspective != diachronic Observer",
            "INTENDED -> WRITTEN -> VERIFIED -> ADMITTED",
        ):
            with self.subTest(fence=lost):
                self.assertIn(audit.normalize(lost), tokens)


if __name__ == "__main__":
    unittest.main()
