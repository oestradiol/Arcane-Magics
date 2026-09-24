from __future__ import annotations

from pathlib import Path
import unittest

from scripts.audit_proof_containers import proof_container_errors

ROOT = Path(__file__).resolve().parents[1]


class ProofHygieneBoundaryTests(unittest.TestCase):
    def test_false_theorem_can_pass_container_lint(self):
        false_but_structured = r"""
\begin{theorem}[Deliberately false fixture]
One equals zero.
\end{theorem}
\begin{proof}
Assume the conclusion.
\end{proof}
"""
        self.assertEqual(
            proof_container_errors(false_but_structured, "fixture.tex"),
            [],
            "container lint should test structure, not mathematical validity",
        )

    def test_missing_proof_fails_container_lint(self):
        malformed = r"""
\begin{theorem}[Missing proof]
A theorem-shaped sentence.
\end{theorem}
"""
        self.assertEqual(len(proof_container_errors(malformed, "fixture.tex")), 1)

    def test_machine_verification_is_separate_build_target(self):
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        self.assertIn("proof-containers:", makefile)
        self.assertIn("formal-check:", makefile)
        self.assertIn("lake build", makefile)


if __name__ == "__main__":
    unittest.main()
