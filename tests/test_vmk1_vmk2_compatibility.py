from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class VMK1ToVMK2CompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (
            ROOT / "provenance/canonical-extracts/R179_VMK1_TO_VMK2_COMPATIBILITY.md"
        ).read_text(encoding="utf-8")

    def test_receipt_return_and_word_portal_are_not_lost(self):
        self.assertIn("execution receipt != external return", self.text)
        self.assertIn("PRESERVED / REFINED", self.text)
        self.assertIn("WORD/reconstruction != state-changing PORTAL", self.text)
        self.assertIn("strict future-family expansion + evidence-bound separator", self.text)

    def test_compatibility_ledger_preserves_real_residuals(self):
        self.assertIn("external authentication", self.text)
        self.assertIn("LICENSE_NOT", self.text)
        self.assertIn("compensation", self.text)
        self.assertIn("NOT ONE-FOR-ONE IN BARE VMK2", self.text)
        self.assertIn("PARTIAL / TRUST BOUNDARY OPEN", self.text)

    def test_later_kernel_name_cannot_self_grant_compatibility(self):
        self.assertIn("same vocabulary", self.text)
        self.assertIn("-/-> compatibility", self.text)
        self.assertIn("compatibility", self.text)
        self.assertIn("consequence preserved at declared index", self.text)


if __name__ == "__main__":
    unittest.main()
