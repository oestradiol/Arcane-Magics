from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CanonicalExtractionReceiptTests(unittest.TestCase):
    def test_r154_external_heavy_custody_is_hash_bound(self):
        data = json.loads(
            (ROOT / "provenance/canonical-extracts/R154_EXTERNAL_HEAVY_CUSTODY.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(data["disposition"], "EXTERNAL_HEAVY_CUSTODY")
        self.assertFalse(data["live_authority"])
        self.assertEqual(
            data["source_archive_sha256"],
            "48a4b9d1f903055aab1fe2bc164d3cf286392c91a7a842a495d54c184f7a69ab",
        )
        files = {row["path"]: row for row in data["files"]}
        trajectory = files[
            "python_proto_r194/state/CURRENT_R154_N1_ANTI_ORIENTED_TRAJECTORY_v0.1.jsonl"
        ]
        self.assertEqual(trajectory["bytes"], 4434463)
        self.assertEqual(
            trajectory["sha256"],
            "8e1756886ebfcac8972bb9730c6c79f90346b6e6c95e3bcaa4baad3264e5d66c",
        )
        self.assertEqual(data["historical_expectations"]["event_count"], 292)
        self.assertEqual(data["historical_expectations"]["reconciliation_count"], 85)

    def test_r209_withhold_is_preserved_as_bounded_current_f_result(self):
        text = (
            ROOT / "provenance/canonical-extracts/R209_R224_CAUSAL_EXTRACT_2026-09-24.md"
        ).read_text(encoding="utf-8")
        self.assertIn("WITHHOLD_UNDERDETERMINED_CURRENT_F", text)
        self.assertIn("bounded task completion under current F", text)
        self.assertIn("closure of the absolute-origin/source proposition", text)
        self.assertIn("genuinely new separator or an expanded future family", text)

    def test_r213_label_admission_does_not_become_sovereignty(self):
        text = (
            ROOT / "provenance/canonical-extracts/R209_R224_CAUSAL_EXTRACT_2026-09-24.md"
        ).read_text(encoding="utf-8")
        self.assertIn("labels are non-sovereign", text)
        self.assertIn("name/label admission", text)
        self.assertIn("semantic or operational sovereignty", text)
        self.assertIn("name-free or renamed reconstruction test", text)

    def test_r224_repair_remains_distinct_from_historical_rewrite(self):
        text = (
            ROOT / "provenance/canonical-extracts/R209_R224_CAUSAL_EXTRACT_2026-09-24.md"
        ).read_text(encoding="utf-8")
        self.assertIn("repair(current projection)", text)
        self.assertIn("retroactive rewrite(historical OPEN/debt state)", text)
        self.assertIn("immutable history", text)


if __name__ == "__main__":
    unittest.main()
