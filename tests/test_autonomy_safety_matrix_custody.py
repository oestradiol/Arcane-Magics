from __future__ import annotations

import json
from pathlib import Path
import unittest

from scripts.audit_autonomy_safety_matrix import REQUIRED, audit_matrix


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "kernel/development/AUTONOMY_SAFETY_DISTINCTION_MATRIX.json"


class AutonomySafetyMatrixCustodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obj = json.loads(MATRIX.read_text(encoding="utf-8"))

    def test_every_declared_distinction_is_exactly_required(self):
        declared = {str(row["id"]) for row in self.obj["distinctions"]}
        self.assertEqual(declared, set(REQUIRED))
        self.assertEqual(len(declared), len(self.obj["distinctions"]))

    def test_deleting_any_declared_distinction_fails_audit(self):
        rows = list(self.obj["distinctions"])
        for index, row in enumerate(rows):
            with self.subTest(distinction=row["id"]):
                damaged = dict(self.obj)
                damaged["distinctions"] = rows[:index] + rows[index + 1:]
                failures = audit_matrix(damaged)
                self.assertTrue(
                    any("missing required distinctions" in failure for failure in failures),
                    failures,
                )

    def test_adding_unbound_distinction_fails_audit(self):
        damaged = dict(self.obj)
        damaged["distinctions"] = list(self.obj["distinctions"]) + [{
            "id": "UNBOUND_NEW_SAFETY_CLAIM",
            "tests": ["tests/test_autonomy_safety_matrix_custody.py"],
            "invariant": "new claims require explicit independent audit custody",
        }]
        failures = audit_matrix(damaged)
        self.assertTrue(
            any("not bound into REQUIRED custody" in failure for failure in failures),
            failures,
        )


if __name__ == "__main__":
    unittest.main()
