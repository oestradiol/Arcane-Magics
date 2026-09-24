from __future__ import annotations

import json
from pathlib import Path
import unittest

from kernel.development.autonomous_learning import (
    SELF_REVIEW_LOGINS,
    authorized_return_logins,
)


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "kernel/development/AUTONOMOUS_RETURN_AUTHORITY.json"
WORKFLOW = ROOT / ".github/workflows/venus-autonomous-worker.yml"


class AutonomousReturnAuthorityTests(unittest.TestCase):
    def test_policy_is_explicit_nonwildcard_and_nonself(self):
        logins = authorized_return_logins()
        self.assertTrue(logins)
        self.assertNotIn("*", logins)
        self.assertFalse(logins & SELF_REVIEW_LOGINS)

    def test_authority_policy_is_not_autonomy_owned(self):
        obj = json.loads(POLICY.read_text(encoding="utf-8"))
        self.assertFalse(obj["autonomy_may_modify"])
        self.assertFalse(obj["promotion_authority"])
        self.assertFalse(obj["truth_authority"])
        self.assertFalse(obj["safety_floor_authority"])

    def test_worker_does_not_commit_or_rewrite_authority_policy(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("AUTONOMOUS_RETURN_AUTHORITY.json", text)

    def test_repo_owner_is_current_explicit_authorized_reviewer(self):
        self.assertIn("oestradiol", authorized_return_logins())


if __name__ == "__main__":
    unittest.main()
