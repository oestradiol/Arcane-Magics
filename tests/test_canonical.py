from __future__ import annotations

import os
import subprocess
import sys
import unittest

from kernel.runtime.canonical import canonical_json, digest


class CanonicalTests(unittest.TestCase):
    def test_sets_are_order_independent(self):
        self.assertEqual(
            canonical_json({"x": {"b", "a", "c"}}),
            canonical_json({"x": {"c", "b", "a"}}),
        )

    def test_set_digest_is_stable_across_hash_seeds(self):
        code = (
            "from kernel.runtime.canonical import digest;"
            "print(digest({'x': {'alpha','beta','gamma','delta'}}))"
        )
        values = []
        for seed in ("1", "2", "3", "999"):
            env = os.environ.copy()
            env["PYTHONHASHSEED"] = seed
            out = subprocess.check_output(
                [sys.executable, "-c", code], text=True, env=env
            ).strip()
            values.append(out)
        self.assertEqual(len(set(values)), 1)

    def test_sequence_order_remains_semantic(self):
        self.assertNotEqual(digest([1, 2]), digest([2, 1]))


if __name__ == "__main__":
    unittest.main()
