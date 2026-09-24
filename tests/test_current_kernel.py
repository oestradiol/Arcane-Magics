from __future__ import annotations

import hashlib
import json
import unittest

from kernel.runtime.current import (
    EXPECTED_IG10_ROOT,
    EXPECTED_SOURCE_SNAPSHOT_SHA256,
    current_summary,
    load_current_kernel,
    reconstruct_snapshot,
)
from kernel.runtime.vmk2 import digest


class CurrentKernelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = reconstruct_snapshot()
        cls.vm = load_current_kernel()

    def test_exact_snapshot_reconstruction(self):
        raw = json.dumps(
            self.snapshot, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(hashlib.sha256(raw).hexdigest(), EXPECTED_SOURCE_SNAPSHOT_SHA256)

    def test_all_state_roots_recompute(self):
        self.assertEqual(len(self.vm.state), 25)
        for object_id, obj in self.vm.state.items():
            self.assertEqual(digest({"id": object_id, "value": obj.value}), obj.root)

    def test_ig10_current_state(self):
        ig10 = self.vm.state["ig10:model-specific-F"]
        self.assertEqual(ig10.root, EXPECTED_IG10_ROOT)
        self.assertEqual(
            ig10.value["routing"]["scheduler"],
            "WITHHOLD_TEST_FAMILY_COMPLETENESS_AND_SEMICLASSICAL_VALIDATION",
        )
        self.assertEqual(ig10.value["routing"]["ready_queue"], [])

    def test_control_counts_survive_compaction(self):
        self.assertEqual(len(self.vm.returns), 288)
        self.assertEqual(len(self.vm.transitions), 283)
        self.assertEqual(len(self.vm.policies), 21)

    def test_summary_is_nonpromotional(self):
        summary = current_summary(self.vm)
        self.assertEqual(summary["runtime_checkpoint"], "IG10")
        self.assertEqual(summary["ready_queue"], [])
        self.assertNotIn("AGI", summary["verdict"])


if __name__ == "__main__":
    unittest.main()
