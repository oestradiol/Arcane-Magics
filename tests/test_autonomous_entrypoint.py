from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_venus_autonomous_cycle.py"


class AutonomousEntrypointTests(unittest.TestCase):
    def test_direct_script_invocation_can_import_kernel(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=20,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("--learning-state", proc.stdout)
        self.assertIn("--output", proc.stdout)


if __name__ == "__main__":
    unittest.main()
