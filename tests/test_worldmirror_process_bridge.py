from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

from kernel.runtime.process_bridge import ProcessBridge, ProcessBridgeError, ProcessPolicy


class ProcessBridgeTests(unittest.TestCase):
    def test_allowed_process_returns_provenance_receipt(self):
        exe = Path(sys.executable).name
        with tempfile.TemporaryDirectory() as td:
            policy = ProcessPolicy.build(td, allowed_executables=[exe], max_output_bytes=64)
            bridge = ProcessBridge(policy)
            receipt, stdout, stderr = bridge.run(
                [exe, "-c", "print('bridge-ok')"],
            )
            self.assertEqual(receipt.exit_code, 0)
            self.assertFalse(receipt.timed_out)
            self.assertEqual(stdout, b"bridge-ok\n")
            self.assertEqual(stderr, b"")
            self.assertTrue(receipt.stdout_sha256)

    def test_executable_and_cwd_fail_closed(self):
        exe = Path(sys.executable).name
        with tempfile.TemporaryDirectory() as td:
            bridge = ProcessBridge(ProcessPolicy.build(td, allowed_executables=[exe]))
            with self.assertRaises(ProcessBridgeError):
                bridge.run(["definitely-not-allowed"])
            with self.assertRaises(ProcessBridgeError):
                bridge.run([exe, "-c", "print(1)"], cwd="../")

    def test_bridge_is_explicitly_not_an_os_sandbox(self):
        text = Path("kernel/runtime/process_bridge.py").read_text(encoding="utf-8")
        self.assertIn("not an OS security sandbox", text)
        policy = Path("kernel/development/WORLDMIRROR_CONSOLE_POLICY.json").read_text(encoding="utf-8")
        self.assertIn("ARGV_CWD_SIZE_TIMEOUT_BOUNDARY_ONLY_NOT_OS_SANDBOX", policy)


if __name__ == "__main__":
    unittest.main()
