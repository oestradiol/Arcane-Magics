from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from kernel.runtime.memory import VenusMemory


class VenusMemoryTests(unittest.TestCase):
    def test_deduplicates_semantic_object(self):
        with tempfile.TemporaryDirectory() as td, VenusMemory(td) as m:
            a = m.put("abstraction", {"x": 1}, labels=["math"])
            b = m.put("abstraction", {"x": 1}, labels=["math"])
            self.assertEqual(a, b)
            self.assertEqual(m.query(kind="abstraction"), (a,))

    def test_consumption_preserves_old_object_and_points_to_replacement(self):
        with tempfile.TemporaryDirectory() as td, VenusMemory(td) as m:
            old = m.put("abstraction", {"rule": "verbose"})
            new = m.put("abstraction", {"rule": "compressed"}, parents=[old])
            m.consume(old, new, reason="same admitted consequences")
            old_obj = m.get(old, touch=False)
            self.assertEqual(old_obj.status, "CONSUMED")
            self.assertEqual(old_obj.replacement, new)
            self.assertEqual(m.get(new, touch=False).status, "ACTIVE")
            self.assertEqual(set(m.dependency_closure([old])), {old, new})

    def test_large_payload_is_externalized_and_verified(self):
        with tempfile.TemporaryDirectory() as td, VenusMemory(td, inline_limit=64) as m:
            digest = m.put("world-return", {"blob": "x" * 10000})
            row = m.db.execute(
                "SELECT canonical,blob_digest FROM objects WHERE digest=?", (digest,)
            ).fetchone()
            self.assertIsNone(row["canonical"])
            self.assertTrue((Path(td) / "objects" / row["blob_digest"][:2] /
                             (row["blob_digest"] + ".z")).exists())
            self.assertEqual(m.get(digest, touch=False).payload["blob"], "x" * 10000)

    def test_export_digest_is_stable_across_reopen(self):
        with tempfile.TemporaryDirectory() as td:
            with VenusMemory(td) as m:
                a = m.put("residual", {"question": "q"}, status="OPEN")
                m.put("abstraction", {"answer": "a"}, parents=[a], provenance=["world:1"])
                first = m.canonical_export()
            with VenusMemory(td) as m:
                second = m.canonical_export()
            self.assertEqual(first, second)
            self.assertEqual(json.loads(first)["schema"], "Venus.Memory.v1")

    def test_parent_must_exist_before_child(self):
        with tempfile.TemporaryDirectory() as td, VenusMemory(td) as m:
            with self.assertRaises(KeyError):
                m.put("abstraction", {"x": 2}, parents=["missing-parent"])

    def test_consumption_replacement_chain_must_be_acyclic(self):
        with tempfile.TemporaryDirectory() as td, VenusMemory(td) as m:
            a = m.put("abstraction", {"v": "a"})
            b = m.put("abstraction", {"v": "b"}, parents=[a])
            m.consume(a, b, reason="b replaces a")
            with self.assertRaises(ValueError):
                m.consume(b, a, reason="cycle")

    def test_new_object_cannot_start_consumed(self):
        with tempfile.TemporaryDirectory() as td, VenusMemory(td) as m:
            with self.assertRaises(ValueError):
                m.put("x", {"v": 1}, status="CONSUMED")

    def test_consumed_requires_replacement(self):
        with tempfile.TemporaryDirectory() as td, VenusMemory(td) as m:
            digest = m.put("x", {"v": 1})
            with self.assertRaises(ValueError):
                m.set_disposition(digest, "CONSUMED")


if __name__ == "__main__":
    unittest.main()
