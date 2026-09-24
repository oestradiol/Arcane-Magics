from __future__ import annotations

import unittest

from kernel.development.recursive_proposal import ResidualObservation, search
from kernel.development.internalized_residual_search import search_internalized


class GenericSearchInternalizationTests(unittest.TestCase):
    def assert_parity(self,rows):
        a=search(rows)
        b=search_internalized(rows)
        self.assertEqual(a.status,b.status)
        self.assertEqual(a.exact_semantic_candidates,b.exact_semantic_candidates)
        self.assertEqual(a.minimal_complexity,b.minimal_complexity)
        self.assertEqual(a.next_discriminator,b.next_discriminator)

    def test_reference_and_internal_state_match_on_single_constraint(self):
        self.assert_parity([
            ResidualObservation((1,0,1),0,"returned-1")
        ])

    def test_reference_and_internal_state_match_on_complete_xor(self):
        self.assert_parity([
            ResidualObservation((0,0),0,"r00"),
            ResidualObservation((0,1),1,"r01"),
            ResidualObservation((1,0),1,"r10"),
            ResidualObservation((1,1),0,"r11"),
        ])

    def test_internalized_backend_does_not_import_historical_donor(self):
        import inspect
        import kernel.development.internalized_residual_search as mod
        source=inspect.getsource(mod)
        self.assertNotIn("importlib.util",source)
        self.assertNotIn("grammar_expansion.py",source)

    def test_internalized_backend_runs_without_reference_search_execution(self):
        rows=[
            ResidualObservation((0,0),0,"r00"),
            ResidualObservation((0,1),1,"r01"),
            ResidualObservation((1,0),1,"r10"),
            ResidualObservation((1,1),0,"r11"),
        ]
        out=search_internalized(rows)
        self.assertEqual(out.status,"UNIQUE_BOUNDED_PROGRAM_CANDIDATE")
        self.assertEqual(out.exact_semantic_candidates,("XOR(x0,x1)",))
        self.assertFalse(out.promotion_authority)


if __name__=="__main__":
    unittest.main()
