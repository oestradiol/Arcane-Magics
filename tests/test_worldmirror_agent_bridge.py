from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import textwrap
import unittest

from apps.worldmirror_console.agent_bridge import (
    AgentBridge,
    AgentBridgeError,
    request_from_events,
)


class WorldMirrorAgentBridgeTests(unittest.TestCase):
    def test_external_stdio_adapter_returns_one_text_reply(self):
        with tempfile.TemporaryDirectory() as td:
            script = Path(td) / "adapter.py"
            script.write_text(
                textwrap.dedent(
                    """
                    import json, sys
                    req=json.load(sys.stdin)
                    text=req["trigger_event"]["decoded_text"]
                    json.dump({"text":"ack:"+text,"metadata":{"adapter":"test"}},sys.stdout)
                    """
                ),
                encoding="utf-8",
            )
            bridge = AgentBridge.build([sys.executable, str(script)])
            request = request_from_events(
                session_id="s",
                trigger_event={
                    "event_id": "e",
                    "decoded_text": "hello",
                    "actor": "human",
                },
                recent_events=[],
            )
            reply = bridge.reply(request)
            self.assertEqual(reply["text"], "ack:hello")
            self.assertEqual(reply["metadata"]["adapter"], "test")
            self.assertFalse(request["capabilities"]["tool_execution"])
            self.assertFalse(request["capabilities"]["promotion_authority"])
            self.assertFalse(request["capabilities"]["independent_evaluation"])

    def test_tool_calls_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            script = Path(td) / "adapter.py"
            script.write_text(
                'import json; print(json.dumps({"text":"x","tool_calls":[{"x":1}]}))',
                encoding="utf-8",
            )
            bridge = AgentBridge.build([sys.executable, str(script)])
            with self.assertRaises(AgentBridgeError):
                bridge.reply({"schema": "test"})

    def test_protocol_keeps_agent_separate_from_learner_and_return(self):
        protocol = json.loads(
            Path("kernel/development/WORLDMIRROR_AGENT_PROTOCOL.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertIn("AGENT_ADAPTER!=LEARNER_IDENTITY", protocol["noncollapse"])
        self.assertIn("AGENT_REPLY!=INDEPENDENT_RETURN", protocol["noncollapse"])
        self.assertFalse(protocol["promotion_authority"])
        self.assertFalse(protocol["truth_authority"])


if __name__ == "__main__":
    unittest.main()
