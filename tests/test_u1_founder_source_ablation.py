from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_u1_recurrence_founder_ablation.py"

spec = importlib.util.spec_from_file_location("u1_founder_ablation_audit", SCRIPT)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class U1FounderSourceAblationTests(unittest.TestCase):
    def test_isolated_bundle_reproduces_recurrence_and_fails_closed(self):
        out = mod.audit()
        self.assertEqual(
            out["status"],
            "PASS_BOUNDED_RECOMPILED_U1_FOUNDER_SOURCE_ABLATION",
        )
        self.assertTrue(out["isolated_mode"])
        self.assertTrue(out["fresh_directory"])
        self.assertFalse(out["repository_root_required_at_runtime"])
        self.assertFalse(out["canonical_library_required"])
        self.assertFalse(out["conversation_state_required"])
        self.assertFalse(out["network_admitted"])
        self.assertTrue(out["missing_artifact_fails_closed"])
        self.assertFalse(out["promotion_authority"])
        self.assertFalse(out["independent_external_replication"])

    def test_problem_and_source_rename_preserve_consequence_not_provenance_identity(self):
        out = mod.audit()
        self.assertTrue(all(out["label_invariant_metrics"].values()))
        self.assertTrue(out["provenance_changes_under_rename"])
        self.assertNotEqual(
            out["baseline"]["recurrence_id"],
            out["renamed"]["recurrence_id"],
        )


if __name__ == "__main__":
    unittest.main()
