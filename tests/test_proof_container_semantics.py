from __future__ import annotations

import re
import unittest


FORMAL_ENV = re.compile(r"\\begin\{(lemma|theorem|proposition|corollary)\}(?:\[[^\]]*\])?")
PROOF = re.compile(r"\\begin\{proof\}")


class ProofContainerSemanticsTests(unittest.TestCase):
    def test_false_theorem_with_proof_container_is_only_structurally_valid(self):
        # The container audit is intentionally syntactic: a theorem block with
        # a proof environment can pass structural lint even when the proposition
        # is mathematically false. Machine verification is a separate burden.
        tex = r"""
\\begin{theorem}[Deliberately false witness]
For all natural numbers n, n = 0.
\\end{theorem}
\\begin{proof}
This prose is intentionally not a valid mathematical proof.
\\end{proof}
"""
        self.assertIsNotNone(FORMAL_ENV.search(tex))
        self.assertIsNotNone(PROOF.search(tex))

        # The test is not claiming truth. It fixes the semantic boundary:
        # structural presence != verified proof.
        claim_is_machine_verified = False
        self.assertFalse(claim_is_machine_verified)


if __name__ == "__main__":
    unittest.main()
