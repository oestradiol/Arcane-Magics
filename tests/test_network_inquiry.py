from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from kernel.development.network_inquiry import (
    NetworkInquiryError,
    WebEncounter,
    bind_web_encounters,
    form_network_query,
    form_followup_network_query,
    reconstruct_from_network,
)
from kernel.runtime.memory import VenusMemory


PROBLEM = {
    "problem_id": "p-web-1",
    "disposition": "FORMED_BOUNDED_PROBLEM",
    "source_stream_ids": ["stream-a"],
    "residual_coordinates": ["referenced_incidence_missing"],
    "discriminator": "RESOLVE_REFERENCED_INCIDENCE",
}


class NetworkInquiryTests(unittest.TestCase):
    def test_query_is_derived_from_formed_problem_without_host_answer(self):
        q = form_network_query(PROBLEM)
        self.assertEqual(q.authorship, "LEARNER_DERIVED_FROM_FORMED_PROBLEM")
        self.assertEqual(q.execution_owner, "EXTERNAL_ADAPTER")
        self.assertIn("resolve referenced incidence", q.query_text)
        self.assertFalse(q.truth_authority)
        self.assertFalse(q.promotion_authority)

    def test_nonformed_problem_cannot_mint_query(self):
        with self.assertRaisesRegex(NetworkInquiryError, "formed problem"):
            form_network_query({**PROBLEM, "disposition": "STOP_NO_CONSEQUENTIAL_RESIDUAL"})

    def test_web_encounter_persists_with_indexed_provenance(self):
        q = form_network_query(PROBLEM)
        with tempfile.TemporaryDirectory() as td, VenusMemory(Path(td)) as mem:
            ids = bind_web_encounters(
                mem,
                query=q,
                encounters=(
                    WebEncounter(
                        source_id="source-a",
                        source_url="https://example.test/a",
                        source_date="2026-09-25",
                        retrieved_at="2026-09-25T00:00:00Z",
                        title="Independent incidence result",
                        summary="A novel external coordinate appears in the returned source.",
                        adapter_id="external-web-adapter",
                    ),
                ),
            )
            obj = mem.get(ids[0])
            self.assertEqual(obj.kind, "NETWORK_ENCOUNTER")
            self.assertEqual(obj.payload["return_class"], "ENCOUNTER_RETURN")
            self.assertFalse(obj.payload["truth_authority"])
            self.assertFalse(obj.payload["evaluation_authority"])
            self.assertIn("source:source-a", obj.provenance)

    def test_retained_network_memory_can_change_later_reconstruction(self):
        q = form_network_query(PROBLEM)
        with tempfile.TemporaryDirectory() as td, VenusMemory(Path(td)) as mem:
            ids = bind_web_encounters(
                mem,
                query=q,
                encounters=(
                    WebEncounter(
                        source_id="source-a",
                        source_url="https://example.test/a",
                        source_date="2026-09-25",
                        retrieved_at="2026-09-25T00:00:00Z",
                        title="Orthogonal provenance topology",
                        summary="Noncommuting projection exposes a lateral separator.",
                        adapter_id="external-web-adapter",
                    ),
                    WebEncounter(
                        source_id="source-b",
                        source_url="https://example.test/b",
                        source_date="2026-09-25",
                        retrieved_at="2026-09-25T00:01:00Z",
                        title="Independent source center",
                        summary="Indexed authorship remains distinct across the relation.",
                        adapter_id="external-web-adapter",
                    ),
                ),
            )
            r = reconstruct_from_network(
                mem,
                problem=PROBLEM,
                query=q,
                memory_object_ids=ids,
            )
            self.assertTrue(r.changed_by_network_memory)
            self.assertEqual(set(r.indexed_source_ids), {"source-a", "source-b"})
            self.assertTrue(r.next_query_terms)
            self.assertFalse(r.promotion_authority)

    def test_web_encounter_cannot_be_retyped_as_evaluator_return(self):
        q = form_network_query(PROBLEM)
        with tempfile.TemporaryDirectory() as td, VenusMemory(Path(td)) as mem:
            oid = mem.put(
                "NETWORK_ENCOUNTER",
                {
                    "query_id": q.query_id,
                    "source_id": "bad",
                    "return_class": "INDEPENDENT_EVALUATIVE_RETURN",
                    "title": "x",
                    "summary": "y",
                },
                provenance=("source:bad",),
            )
            with self.assertRaisesRegex(NetworkInquiryError, "retyped"):
                reconstruct_from_network(
                    mem,
                    problem=PROBLEM,
                    query=q,
                    memory_object_ids=(oid,),
                )

    def test_retained_memory_changes_successor_query(self):
        q = form_network_query(PROBLEM)
        with tempfile.TemporaryDirectory() as td, VenusMemory(Path(td)) as mem:
            ids = bind_web_encounters(
                mem,
                query=q,
                encounters=(
                    WebEncounter(
                        source_id="source-a",
                        source_url="https://example.test/a",
                        source_date="2026-09-25",
                        retrieved_at="2026-09-25T00:00:00Z",
                        title="Orthogonal provenance topology",
                        summary="Noncommuting projection exposes a lateral separator.",
                        adapter_id="external-web-adapter",
                    ),
                ),
            )
            r = reconstruct_from_network(
                mem,
                problem=PROBLEM,
                query=q,
                memory_object_ids=ids,
            )
            q2 = form_followup_network_query(prior_query=q, reconstruction=r)
            self.assertNotEqual(q2.query_id, q.query_id)
            self.assertNotEqual(q2.query_text, q.query_text)
            self.assertEqual(
                q2.authorship,
                "LEARNER_DERIVED_FROM_NETWORK_RECONSTRUCTION",
            )
            self.assertTrue(
                any(x.startswith("network-memory:") for x in q2.provenance_ids)
            )
            self.assertFalse(q2.truth_authority)
            self.assertFalse(q2.promotion_authority)


if __name__ == "__main__":
    unittest.main()
