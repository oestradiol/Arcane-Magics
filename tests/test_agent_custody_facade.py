from __future__ import annotations

import unittest

from packages.agent_custody import AgentCustody, AuthorityLevel


class AgentCustodyFacadeTests(unittest.TestCase):
    def setUp(self):
        self.custody=AgentCustody()

    def test_required_fact_in_return_bundle_but_not_selected_does_not_support_claim(self):
        selected=self.custody.record_evidence(source_id='world',assessor_id='external',payload={'a':1},epoch=1)
        required=self.custody.record_evidence(source_id='world',assessor_id='external',payload={'b':2},epoch=2)
        binding=self.custody.bind_claim(
            claim_id='c',
            returned_evidence_ids=[selected.evidence_id,required.evidence_id],
            selected_evidence_ids=[selected.evidence_id],
            required_evidence_ids=[required.evidence_id],
        )
        self.assertFalse(binding.supported)
        self.assertEqual(binding.missing_required_evidence,frozenset({required.evidence_id}))
        with self.assertRaises(ValueError):
            self.custody.require_supported_claim('c')

    def test_selected_evidence_must_have_been_returned(self):
        e=self.custody.record_evidence(source_id='world',assessor_id='external',payload={'x':1},epoch=1)
        with self.assertRaises(ValueError):
            self.custody.bind_claim(
                claim_id='bad',returned_evidence_ids=[],
                selected_evidence_ids=[e.evidence_id],required_evidence_ids=[]
            )

    def test_returned_evidence_ids_must_resolve_in_custody(self):
        with self.assertRaises(ValueError):
            self.custody.bind_claim(
                claim_id='bad',returned_evidence_ids=['not-real'],
                selected_evidence_ids=[],required_evidence_ids=[]
            )

    def test_authority_level_is_not_upgraded_by_facade(self):
        self.assertIs(self.custody.authority_level,AuthorityLevel.INTERNALLY_REGISTERED)

if __name__=='__main__': unittest.main()
