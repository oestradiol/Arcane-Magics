from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from kernel.development.network_inquiry import (
    NetworkInquiryError,
    WebEncounter,
    bind_network_execution_context,
    bind_web_encounters,
    form_network_query,
    form_followup_network_query,
    reconstruct_from_network,
)
from kernel.runtime.memory import VenusMemory
from scripts.freeze_network_query import selected_study_context


PROBLEM = {
    "problem_id": "p-web-1",
    "disposition": "FORMED_BOUNDED_PROBLEM",
    "source_stream_ids": ["stream-a"],
    "residual_coordinates": ["referenced_incidence_missing"],
    "discriminator": "RESOLVE_REFERENCED_INCIDENCE",
}

STUDY = {
    "target_kind": "ISSUE",
    "target_number": 206,
    "target_title": "[Curriculum/Cognitive Theater] Recover Canonical English/Japanese/PT-BR/Math foundations before deeper VM consumption",
    "method": "DEPENDENCY_TRACE",
    "returned_blocker_sentences": [
        "surface retention != cross-theater relational reconstruction",
        "Japanese leave-one-face-out lawfully WITHHOLDs",
    ],
    "referenced_repository_paths": [
        "kernel/development/FOUNDATIONAL_COGNITIVE_THEATER_SURFACE_BASELINE_RESULT.json",
    ],
}


class NetworkInquiryTests(unittest.TestCase):
    def test_query_is_derived_from_formed_problem_without_host_answer(self):
        q = form_network_query(PROBLEM)
        self.assertEqual(q.authorship, "LEARNER_DERIVED_FROM_FORMED_PROBLEM")
        self.assertEqual(q.execution_owner, "EXTERNAL_ADAPTER")
        self.assertIn("resolve referenced incidence", q.query_text)
        self.assertFalse(q.truth_authority)
        self.assertFalse(q.promotion_authority)

    def test_selected_study_constrains_query_after_target_selection(self):
        base = form_network_query(PROBLEM)
        q = form_network_query(PROBLEM, study=STUDY)
        self.assertEqual(q.authorship, "LEARNER_DERIVED_FROM_SELECTED_STUDY")
        self.assertTrue(
            q.query_text.startswith(
                "curriculum cognitive theater canonical english japanese"
            )
        )
        self.assertIn("pt-br", q.query_text)
        self.assertIn("math", q.query_text)
        self.assertNotEqual(q.query_id, base.query_id)
        self.assertTrue(q.study_context_digest)
        self.assertEqual(
            q.study_terms[:6],
            ("curriculum", "cognitive", "theater", "canonical", "english", "japanese"),
        )
        self.assertIn(
            f"selected-study:{q.study_context_digest}",
            q.provenance_ids,
        )
        self.assertNotIn("206", q.query_text)
        self.assertFalse(q.truth_authority)
        self.assertFalse(q.promotion_authority)

    def test_cycle_top_level_target_becomes_selected_study_context(self):
        cycle={
            "target_kind":"ISSUE",
            "target_number":206,
            "target_title":STUDY["target_title"],
            "study":{
                "method":"DEPENDENCY_TRACE",
                "returned_blocker_sentences":["surface-only baseline failed"],
            },
        }
        merged=selected_study_context(cycle)
        self.assertEqual(merged["target_number"],206)
        self.assertEqual(merged["target_title"],STUDY["target_title"])
        q=form_network_query(PROBLEM,study=merged)
        self.assertTrue(q.query_text.startswith("curriculum cognitive theater"))

    def test_selected_study_text_remains_inert_lexical_context(self):
        hostile = {
            **STUDY,
            "target_title": "Cognitive theater; rm -rf /; $(touch owned)",
            "returned_blocker_sentences": ["eval(__import__('os').system('x'))"],
        }
        q = form_network_query(PROBLEM, study=hostile)
        self.assertNotIn("$(", q.query_text)
        self.assertNotIn("/", q.query_text)
        self.assertNotIn(";", q.query_text)
        self.assertEqual(q.execution_owner, "EXTERNAL_ADAPTER")

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

    def test_followup_preserves_selected_study_custody(self):
        q = form_network_query(PROBLEM, study=STUDY)
        with tempfile.TemporaryDirectory() as td, VenusMemory(Path(td)) as mem:
            ids = bind_web_encounters(
                mem,
                query=q,
                encounters=(
                    WebEncounter(
                        source_id="source-study",
                        source_url="https://example.test/study",
                        source_date="2026-09-26",
                        retrieved_at="2026-09-26T00:00:00Z",
                        title="Cross linguistic representation learning",
                        summary="Relational structure across languages and formal systems.",
                        adapter_id="external-web-adapter",
                    ),
                ),
            )
            r = reconstruct_from_network(
                mem, problem=PROBLEM, query=q, memory_object_ids=ids
            )
            q2 = form_followup_network_query(prior_query=q, reconstruction=r)
            self.assertEqual(q2.study_context_digest, q.study_context_digest)
            self.assertEqual(tuple(q2.study_terms), tuple(q.study_terms))
            self.assertTrue(q2.query_text.startswith("curriculum cognitive theater"))
            self.assertEqual(
                tuple(q2.query_text.split()[3:]),
                tuple(r.next_query_terms[:6]),
            )
            self.assertTrue(r.next_query_terms)
            self.assertFalse(any(ch.isdigit() for ch in q2.query_text))
            self.assertEqual(
                q2.authorship,
                "LEARNER_DERIVED_FROM_NETWORK_RECONSTRUCTION",
            )

    def test_worker_freezes_query_after_cycle_selection(self):
        text=(Path(__file__).resolve().parents[1] / ".github/workflows/minerva-autonomous-worker.yml").read_text(encoding="utf-8")
        self.assertIn("--cycle /tmp/minerva/CYCLE.json", text)

    def test_execution_context_routes_adapter_without_rewriting_query(self):
        q = form_network_query(PROBLEM)
        ctx = bind_network_execution_context(
            query=q,
            carrier_keys=(("PR", 155),),
            repository_full_name="oestradiol/Arcane-Magics",
        )
        self.assertEqual(ctx.query_id, q.query_id)
        self.assertEqual(q.query_text, "resolve referenced incidence referenced incidence missing")
        self.assertEqual(ctx.role, "ADAPTER_ROUTING_CONTEXT_ONLY")
        self.assertIn(
            "https://github.com/oestradiol/Arcane-Magics/pull/155",
            ctx.source_locators,
        )
        self.assertFalse(ctx.target_selection_authority)
        self.assertFalse(ctx.truth_authority)
        self.assertFalse(ctx.promotion_authority)


if __name__ == "__main__":
    unittest.main()
