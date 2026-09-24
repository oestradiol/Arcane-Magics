from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SOTAWatchStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "docs/SOTA_WATCH_STATE.json").read_text(encoding="utf-8"))

    def test_watch_schema_and_issue_ownership(self):
        self.assertEqual(self.data["schema"], "Venus.SOTAWatchState.v0.2")
        for row in self.data["entries"]:
            with self.subTest(row=row["id"]):
                self.assertIsInstance(row["issue"], int)
                self.assertTrue(row["recheck_trigger"])
                self.assertIn(row["reconciliation_state"], {"CLEAN", "OPEN"})

    def test_reconcile_entries_are_explicitly_open(self):
        for row in self.data["entries"]:
            with self.subTest(row=row["id"]):
                if row["status"] == "RECONCILE":
                    self.assertEqual(row["reconciliation_state"], "OPEN")
                else:
                    self.assertEqual(row["reconciliation_state"], "CLEAN")

    def test_navier_stokes_reconciliation_is_issue_owned(self):
        row = next(x for x in self.data["entries"] if x["id"] == "navier_stokes_status")
        self.assertEqual(row["issue"], 7)
        self.assertEqual(row["status"], "RECONCILE")
        self.assertEqual(row["reconciliation_state"], "OPEN")


if __name__ == "__main__":
    unittest.main()
