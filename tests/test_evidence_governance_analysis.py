from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "evaluation" / "analyze_evidence_governance.py"


def load_module():
    spec = importlib.util.spec_from_file_location("evidence_governance_analysis", ANALYZER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class EvidenceGovernanceAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def write_condition(self, root: Path, cid: str, rows: list[dict]) -> Path:
        path = root / f"{cid}.jsonl"
        path.write_text("\n".join(json.dumps(x) for x in rows) + "\n", encoding="utf-8")
        return path

    def base_row(self, rid: str, **overrides):
        row = {
            "id": rid,
            "invalid_promotion": False,
            "unsupported_claim_or_action": False,
            "correct_withhold": True,
            "false_withhold": False,
            "negative_result_reuse_correct": True,
            "task_success": True,
        }
        row.update(overrides)
        return row

    def test_paired_analysis_detects_mechanism_local_direction(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ids = [f"x{i}" for i in range(12)]
            A = [self.base_row(i) for i in ids]
            B = [self.base_row(i) for i in ids]
            C = [self.base_row(i, invalid_promotion=(j < 10)) for j, i in enumerate(ids)]
            D = [self.base_row(i, negative_result_reuse_correct=(j >= 10)) for j, i in enumerate(ids)]
            E = [self.base_row(i) for i in ids]
            paths = {
                cid: self.write_condition(root, cid, rows)
                for cid, rows in zip(("A","B","C","D","E"), (A,B,C,D,E))
            }
            out = self.mod.analyze(paths, alpha=0.05)

        ptest = out["primary_mechanism_tests"]["claim_local_provenance_B_vs_C_invalid_promotion"]
        ntest = out["primary_mechanism_tests"]["retained_negative_state_B_vs_D_negative_reuse"]
        self.assertEqual(ptest["direction"], "LEFT_BETTER")
        self.assertEqual(ntest["direction"], "LEFT_BETTER")
        self.assertLess(ptest["two_sided_exact_p"], 0.05)
        self.assertLess(ntest["two_sided_exact_p"], 0.05)
        self.assertFalse(out["promotion_authority"])

    def test_id_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            rows = [self.base_row("x")]
            paths = {cid: self.write_condition(root, cid, rows) for cid in ("A","B","C","D","E")}
            paths["E"].write_text(json.dumps(self.base_row("other")) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "identical hidden case IDs"):
                self.mod.analyze(paths, alpha=0.05)

    def test_holm_requires_first_test_to_clear_half_alpha(self):
        got = self.mod.holm_two(0.03, 0.04, 0.05)
        self.assertEqual(got["reject_null"], {"provenance": False, "negative_state": False})


if __name__ == "__main__":
    unittest.main()
