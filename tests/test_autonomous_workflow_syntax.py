from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/venus-autonomous-worker.yml"


class AutonomousWorkflowSyntaxTests(unittest.TestCase):
    def test_only_known_workflow_keys_may_start_at_column_zero(self):
        lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
        allowed = ("name:", "on:", "permissions:", "concurrency:", "jobs:")
        escaped = [
            (index + 1, line)
            for index, line in enumerate(lines)
            if line
            and not line.startswith((" ", "#"))
            and not line.startswith(allowed)
        ]
        self.assertEqual(
            escaped,
            [],
            "text escaped a YAML block to column zero",
        )

    def test_multiline_pr_body_is_built_inside_shell_block(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("printf -v body", text)
        self.assertNotIn('body="This draft PR was opened', text)

    def test_multiline_target_comment_is_built_inside_shell_block(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("printf -v msg", text)

    def test_worker_is_schedule_or_manual_only(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("schedule:", text)
        self.assertNotIn("\n  push:", text)
        self.assertNotIn("\n  pull_request:", text)


if __name__ == "__main__":
    unittest.main()
