from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from kernel.runtime.interaction_store import InteractionStore


class InteractionStoreTests(unittest.TestCase):
    def test_raw_bytes_and_semantic_view_remain_distinct_and_bound(self):
        with tempfile.TemporaryDirectory() as td:
            with InteractionStore(td) as store:
                sid = store.create_session(title="test")
                first = store.append(
                    session_id=sid,
                    actor="human",
                    kind="CHAT_MESSAGE",
                    media_type="text/plain",
                    raw="hello λ".encode("utf-8"),
                )
                second = store.append(
                    session_id=sid,
                    actor="machine",
                    kind="CHAT_MESSAGE",
                    media_type="text/plain",
                    raw=b"returned view",
                    parent_event_id=first.event_id,
                )

                self.assertEqual(store.raw_bytes(first.raw_sha256), "hello λ".encode("utf-8"))
                self.assertEqual(first.decoded_text, "hello λ")
                self.assertNotEqual(first.raw_sha256, first.semantic_digest)
                self.assertEqual(second.parent_event_id, first.event_id)

                events = store.events(sid)
                self.assertEqual([e.actor for e in events], ["human", "machine"])
                self.assertEqual([e.seq for e in events], sorted(e.seq for e in events))

                semantic = store.memory.get(first.semantic_digest, touch=False)
                self.assertEqual(semantic.kind, "INTERACTION_EVENT_VIEW")
                self.assertIn(f"raw:sha256:{first.raw_sha256}", semantic.provenance)

    def test_binary_event_is_not_forced_into_text(self):
        with tempfile.TemporaryDirectory() as td:
            with InteractionStore(td) as store:
                sid = store.create_session()
                event = store.append(
                    session_id=sid,
                    actor="world",
                    kind="BINARY_RETURN",
                    media_type="application/octet-stream",
                    raw=b"\xff\x00\xfe",
                )
                self.assertIsNone(event.decoded_text)
                self.assertEqual(store.raw_bytes(event.raw_sha256), b"\xff\x00\xfe")


if __name__ == "__main__":
    unittest.main()
