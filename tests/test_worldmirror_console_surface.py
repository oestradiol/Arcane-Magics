from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class WorldMirrorConsoleSurfaceTests(unittest.TestCase):
    def test_surface_is_local_raw_first_and_does_not_fabricate_agent(self):
        server = (ROOT / "apps/worldmirror_console/server.py").read_text(encoding="utf-8")
        html = (ROOT / "apps/worldmirror_console/static/index.html").read_text(encoding="utf-8")
        js = (ROOT / "apps/worldmirror_console/static/app.js").read_text(encoding="utf-8")
        policy = json.loads(
            (ROOT / "kernel/development/WORLDMIRROR_CONSOLE_POLICY.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertIn('default="127.0.0.1"', server)
        self.assertIn("loopback-only", server)
        self.assertIn('"agent_backend_bound": False', server)
        self.assertIn('"fabricated_agent_reply": False', server)
        self.assertIn("/api/raw", js)
        self.assertIn("WorldMirror", html)
        self.assertTrue(policy["interaction"]["raw_bytes_preserved"])
        self.assertFalse(policy["interaction"]["storage_counts_as_learning"])
        self.assertFalse(policy["process_bridge"]["enabled_by_default"])
        self.assertFalse(policy["interface"]["fabricated_agent_reply_when_unbound"])

    def test_interaction_development_contract_blocks_log_equals_learning(self):
        contract = json.loads(
            (ROOT / "kernel/development/INTERACTION_DEVELOPMENT_CONTRACT.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertIn("INTERACTION_LOG!=LEARNING", contract["noncollapse"])
        self.assertIn("SELF_DIALOGUE!=INDEPENDENT_RETURN", contract["noncollapse"])
        self.assertFalse(contract["promotion_authority"])
        self.assertFalse(contract["truth_authority"])


if __name__ == "__main__":
    unittest.main()
