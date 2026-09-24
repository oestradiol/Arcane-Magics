from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "provenance" / "HISTORICAL_DISTINCTION_TEST_MATRIX.json"
REQUIRED = {
    "id",
    "source_revision_or_branch",
    "source_artifact",
    "distinction",
    "triggering_experiment_or_failure",
    "causal_consequence",
    "later_dependents",
    "current_owner",
    "test_layer",
    "test_id_path",
    "status",
    "credit_genealogy_note",
    "reopening_condition",
}


class HistoricalDistinctionMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(MATRIX.read_text(encoding="utf-8"))
        cls.rows = cls.data["rows"]

    def test_ids_are_unique_and_rows_are_typed(self):
        ids = [row["id"] for row in self.rows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 30)
        for row in self.rows:
            self.assertEqual(REQUIRED - set(row), set(), row.get("id"))
            self.assertTrue(row["distinction"].strip())
            self.assertTrue(row["causal_consequence"].strip())
            self.assertTrue(row["status"].strip())
            self.assertTrue(row["reopening_condition"].strip())

    def test_live_test_file_references_exist(self):
        for row in self.rows:
            ref = row.get("test_id_path")
            if not ref or not ref.startswith(("tests/", "scripts/")):
                continue
            path = ref.split("::", 1)[0]
            self.assertTrue((ROOT / path).exists(), f"{row['id']}: missing {path}")

    def test_planned_rows_are_not_mislabeled_as_covered(self):
        for row in self.rows:
            status = row["status"]
            if status in {"PLANNED", "NO_AUTOMATED_TEST_YET", "OPEN_EXTRACTION"}:
                ref = row.get("test_id_path")
                self.assertFalse(
                    ref and ref.startswith("tests/"),
                    f"{row['id']}: open row points at a passing test as if covered",
                )


if __name__ == "__main__":
    unittest.main()
