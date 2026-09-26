from __future__ import annotations

import ast
import json
from pathlib import Path
import unittest

from kernel.runtime.action_proposal import authorization_matches, propose_process


ROOT = Path(__file__).resolve().parents[1]


class ActionProposalProtocolTests(unittest.TestCase):
    def test_proposal_is_canonical_inert_and_bound_to_authorization(self):
        p = propose_process(
            ["python3", "-c", "print(1)"],
            cwd=".",
            rationale="measure a returned process consequence",
            expected_return="exit code and captured stdout",
        )
        self.assertTrue(p.proposal_id)
        self.assertFalse(
            authorization_matches(
                p,
                {
                    "schema": "Venus.WorldMirrorActionAuthorization.v0.1",
                    "proposal_id": p.proposal_id,
                    "authorized": False,
                    "authorization_id": "a",
                    "issuer": "external",
                },
            )
        )
        self.assertTrue(
            authorization_matches(
                p,
                {
                    "schema": "Venus.WorldMirrorActionAuthorization.v0.1",
                    "proposal_id": p.proposal_id,
                    "authorized": True,
                    "authorization_id": "a",
                    "issuer": "external",
                },
            )
        )

    def test_proposal_module_cannot_execute(self):
        text = (ROOT / "kernel/runtime/action_proposal.py").read_text(encoding="utf-8")
        tree = ast.parse(text)
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.add(node.module or "")
        self.assertNotIn("kernel.runtime.process_bridge", imported)
        self.assertNotIn("subprocess", imported)

    def test_protocol_keeps_authority_external(self):
        protocol = json.loads(
            (ROOT / "kernel/development/WORLDMIRROR_ACTION_PROPOSAL_PROTOCOL.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertIn("PROPOSE!=AUTHORIZE", protocol["noncollapse"])
        self.assertIn("AUTHORIZE!=EXECUTE", protocol["noncollapse"])
        self.assertEqual(protocol["authorization"]["custody"], "EXTERNAL_TO_PROPOSING_LEARNER")
        self.assertFalse(protocol["promotion_authority"])
        self.assertFalse(protocol["truth_authority"])


if __name__ == "__main__":
    unittest.main()
