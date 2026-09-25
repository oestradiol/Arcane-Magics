from __future__ import annotations

import importlib.abc
import json
from pathlib import Path
import sys
import tempfile
import unittest

from kernel.development.autonomous_patch import (
    AutonomousWritePolicyError,
    classify_path,
    load_write_policy,
    make_patch_plan,
)
from kernel.development.autonomous_worker import WorkItem, make_cycle


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "kernel/development/AUTONOMOUS_WRITE_POLICY.json"
INTERNAL_POLICY = json.loads(
    (ROOT / "kernel/development/INTERNAL_OSTAR_INTERNALIZED_POLICY.json").read_text(
        encoding="utf-8"
    )
)


class _TeacherBlocker(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "kernel.development.internal_ostar_teacher":
            raise ImportError("teacher removed")
        return None


class AutonomousWriteScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = load_write_policy(POLICY_PATH)

    def test_autonomy_owned_state_is_direct_write_only_scope(self):
        row = classify_path(
            self.policy,
            "kernel/development/AUTONOMOUS_LEARNING_STATE.json",
        )
        self.assertEqual(row.mode, "DIRECT_STATE_WRITE")
        self.assertTrue(row.direct_write_allowed)

    def test_ordinary_core_source_is_proposal_only(self):
        row = classify_path(self.policy, "kernel/runtime/vmk2.py")
        self.assertEqual(row.mode, "PROPOSE_ONLY")
        self.assertFalse(row.direct_write_allowed)
        self.assertTrue(row.proposal_allowed)

    def test_safety_floor_requires_external_governance(self):
        protected = (
            ".github/workflows/venus-autonomous-worker.yml",
            "kernel/runtime/ctl.py",
            "kernel/runtime/internalizer.py",
            "kernel/development/AUTONOMOUS_RETURN_AUTHORITY.json",
            "kernel/development/AUTONOMY_SAFETY_DISTINCTION_MATRIX.json",
            "kernel/development/AUTONOMOUS_WRITE_POLICY.json",
            "kernel/development/INTERNAL_OSTAR_INTERNALIZED_POLICY.json",
            "kernel/development/autonomous_learning.py",
            "kernel/development/autonomous_worker.py",
            "kernel/development/autonomous_problem_formation.py",
            "kernel/development/u1_recurrence.py",
            "scripts/run_venus_recurrence_candidate.py",
            "kernel/runtime/bounded_recurrence.py",
            "kernel/development/autonomous_recurrence.py",
            "kernel/development/AUTONOMOUS_RECURRENCE_CATALOG.json",
        )
        for path in protected:
            with self.subTest(path=path):
                row = classify_path(self.policy, path)
                self.assertEqual(row.mode, "EXTERNAL_GOVERNANCE_ONLY")
                self.assertFalse(row.direct_write_allowed)
                self.assertTrue(row.requires_external_governance)

    def test_path_traversal_and_ambiguous_paths_fail_closed(self):
        for path in (
            "../kernel/runtime/ctl.py",
            "/etc/passwd",
            "kernel/../.github/workflows/x.yml",
            r"kernel\runtime\ctl.py",
            "",
        ):
            with self.subTest(path=path):
                with self.assertRaises(AutonomousWritePolicyError):
                    classify_path(self.policy, path)

    def test_unknown_repository_surface_is_denied(self):
        row = classify_path(self.policy, "vendor/generated/unknown.bin")
        self.assertEqual(row.mode, "DENY_UNKNOWN")
        self.assertFalse(row.direct_write_allowed)

    def test_patch_plan_marks_mixed_core_and_floor_for_external_governance(self):
        cycle = {
            "cycle_id": "cycle-x",
            "target_kind": "ISSUE",
            "target_number": 72,
            "decision": "PROBE",
            "study": {
                "referenced_repository_paths": [
                    "kernel/runtime/vmk2.py",
                    "kernel/runtime/ctl.py",
                ]
            },
        }
        plan = make_patch_plan(cycle, self.policy)
        self.assertEqual(plan.disposition, "EXTERNAL_GOVERNANCE_REVIEW_REQUIRED")
        self.assertFalse(plan.arbitrary_code_write_authority)
        self.assertFalse(plan.promotion_authority)
        self.assertFalse(plan.merge_authority)

    def test_patch_plan_uses_returned_pr_changed_files_not_only_body_paths(self):
        cycle = {
            "cycle_id": "cycle-pr",
            "target_kind": "PR",
            "target_number": 200,
            "decision": "PROBE",
            "study": {
                "returned_changed_paths": [
                    "kernel/runtime/vmk2.py",
                    "kernel/runtime/ctl.py",
                ],
                "referenced_repository_paths": [],
            },
        }
        plan = make_patch_plan(cycle, self.policy)
        self.assertEqual(plan.disposition, "EXTERNAL_GOVERNANCE_REVIEW_REQUIRED")
        modes = {row.path: row.mode for row in plan.paths}
        self.assertEqual(modes["kernel/runtime/vmk2.py"], "PROPOSE_ONLY")
        self.assertEqual(modes["kernel/runtime/ctl.py"], "EXTERNAL_GOVERNANCE_ONLY")

    def test_workflow_snapshots_pr_files_as_returned_world_surface(self):
        text = (ROOT / ".github/workflows/venus-autonomous-worker.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "--json number,title,body,state,isDraft,mergeStateStatus,updatedAt,files",
            text,
        )

    def test_internalized_policy_drives_autonomous_cycle_with_teacher_blocked(self):
        blocker = _TeacherBlocker()
        sys.meta_path.insert(0, blocker)
        prior = sys.modules.pop("kernel.development.internal_ostar_teacher", None)
        try:
            cycle = make_cycle(
                issues=(
                    WorkItem(
                        "ISSUE",
                        72,
                        "Safe Strong RSI",
                        body="Remaining work references kernel/runtime/ctl.py.",
                    ),
                ),
                prs=(),
                roadmap_text="#72",
                internal_policy=INTERNAL_POLICY,
            )
            self.assertEqual(cycle.decision, "PROBE")
            self.assertIsNotNone(cycle.study)
        finally:
            sys.meta_path.remove(blocker)
            if prior is not None:
                sys.modules["kernel.development.internal_ostar_teacher"] = prior

    def test_workflow_records_patch_plan_before_git_push(self):
        text = (ROOT / ".github/workflows/venus-autonomous-worker.yml").read_text(
            encoding="utf-8"
        )
        plan_at = text.index("Let Venus classify bounded patch/write jurisdiction")
        push_at = text.index("git push origin")
        self.assertLess(plan_at, push_at)
        self.assertIn("autonomy/patches/", text)
        self.assertIn("AUTONOMOUS_WRITE_POLICY.json", text)

    def test_workflow_does_not_copy_target_source_into_direct_write_set(self):
        text = (ROOT / ".github/workflows/venus-autonomous-worker.yml").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("git add kernel/runtime/", text)
        self.assertNotIn("git add scripts/", text)
        self.assertNotIn("git add tests/", text)
        self.assertNotIn("git add .github/", text)

    def test_runtime_autonomy_modules_do_not_import_teacher(self):
        for rel in (
            "kernel/development/autonomous_worker.py",
            "scripts/run_venus_autonomous_cycle.py",
            ".github/workflows/venus-autonomous-worker.yml",
        ):
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertNotIn("internal_ostar_teacher", text)
            self.assertNotIn("teacher_decision", text)


if __name__ == "__main__":
    unittest.main()
