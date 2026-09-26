from __future__ import annotations

import json
from http.server import HTTPServer
from pathlib import Path
from queue import Queue
import sys
import tempfile
import textwrap
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from apps.worldmirror_console.agent_bridge import AgentBridge
from apps.worldmirror_console.server import ConsoleContext, Handler


ROOT = Path(__file__).resolve().parents[1]


class WorldMirrorConsoleEndToEndTests(unittest.TestCase):
    def test_human_event_roundtrips_through_external_agent_as_two_raw_events(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            adapter = root / "adapter.py"
            adapter.write_text(
                textwrap.dedent(
                    """
                    import json, sys
                    req=json.load(sys.stdin)
                    trigger=req["trigger_event"]
                    json.dump({"text":"machine:"+trigger["decoded_text"]},sys.stdout)
                    """
                ),
                encoding="utf-8",
            )

            ready: Queue = Queue()

            def serve() -> None:
                ctx = ConsoleContext(
                    data_root=root / "data",
                    static_root=ROOT / "apps/worldmirror_console/static",
                    process_bridge=None,
                    agent_bridge=AgentBridge.build([sys.executable, str(adapter)]),
                )
                server = HTTPServer(("127.0.0.1", 0), Handler)
                server.ctx = ctx
                ready.put(server)
                try:
                    server.serve_forever()
                finally:
                    server.server_close()
                    ctx.close()

            thread = threading.Thread(target=serve, daemon=True)
            thread.start()
            server = ready.get(timeout=5)
            base = f"http://127.0.0.1:{server.server_address[1]}"

            try:
                req = Request(
                    base + "/api/sessions",
                    data=json.dumps({"title": "e2e"}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urlopen(req, timeout=5) as response:
                    sid = json.loads(response.read())["session_id"]

                raw = "hello from outside".encode("utf-8")
                req = Request(
                    base + "/api/raw",
                    data=raw,
                    headers={
                        "Content-Type": "text/plain; charset=utf-8",
                        "X-WorldMirror-Session": sid,
                        "X-WorldMirror-Actor": "human",
                        "X-WorldMirror-Kind": "CHAT_MESSAGE",
                    },
                    method="POST",
                )
                with urlopen(req, timeout=5) as response:
                    posted = json.loads(response.read())
                self.assertEqual(posted["event"]["decoded_text"], "hello from outside")
                self.assertEqual(
                    posted["machine_event"]["decoded_text"],
                    "machine:hello from outside",
                )
                self.assertIsNone(posted["agent_error"])

                with urlopen(base + "/api/events?session_id=" + sid, timeout=5) as response:
                    events = json.loads(response.read())["events"]
                self.assertEqual([e["actor"] for e in events], ["human", "machine"])
                self.assertEqual(events[1]["parent_event_id"], events[0]["event_id"])
                self.assertNotEqual(events[0]["raw_sha256"], events[0]["semantic_digest"])

                req = Request(
                    base + "/api/process",
                    data=b"{}",
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with self.assertRaises(HTTPError) as caught:
                    urlopen(req, timeout=5)
                self.assertEqual(caught.exception.code, 403)
            finally:
                server.shutdown()
                thread.join(timeout=5)
                self.assertFalse(thread.is_alive())


if __name__ == "__main__":
    unittest.main()
