from __future__ import annotations

from pathlib import Path
import unittest

from kernel.development.cross_layer_relation_binding import (
    CarrierOccurrence,
    RelationBindingError,
    RelationEndpoint,
    ReturnedBindingJudgment,
    bind_return,
    make_binding_proposal,
    make_occurrence,
)


class CrossLayerRelationBindingTests(unittest.TestCase):
    def occurrence(self):
        return make_occurrence(
            carrier_object_id="raw:1",
            source_id="source:1",
            source_start=10,
            source_end=24,
            provenance_ids=("source-return",),
        )

    def test_learner_selects_endpoints_relation_and_discriminator(self):
        p = make_binding_proposal(
            self.occurrence(),
            left_endpoint=RelationEndpoint("span:left", "SPAN"),
            right_endpoint=RelationEndpoint("state:right", "STATE"),
            relation_symbol="R_candidate",
            discriminator_id="d:learner",
            author_id="venus",
        )
        self.assertEqual(p.author_id, "venus")
        self.assertEqual(p.relation_symbol, "R_candidate")
        self.assertFalse(p.promotion_authority)

    def test_proposal_cannot_see_hidden_evaluation(self):
        with self.assertRaisesRegex(RelationBindingError, "hidden evaluation"):
            make_binding_proposal(
                self.occurrence(),
                left_endpoint=RelationEndpoint("a", "SPAN"),
                right_endpoint=RelationEndpoint("b", "STATE"),
                relation_symbol="R",
                discriminator_id="d",
                author_id="venus",
                hidden_evaluation_exposed=True,
            )

    def test_acceptance_requires_external_return(self):
        p = make_binding_proposal(
            self.occurrence(),
            left_endpoint=RelationEndpoint("a", "SPAN"),
            right_endpoint=RelationEndpoint("b", "STATE"),
            relation_symbol="R",
            discriminator_id="d",
            author_id="venus",
        )
        with self.assertRaisesRegex(RelationBindingError, "externally returned"):
            bind_return(
                p,
                ReturnedBindingJudgment(
                    return_id="r",
                    proposal_id=p.proposal_id,
                    source_id="self",
                    accepted=True,
                    provenance_ids=("self",),
                    external=False,
                ),
            )

    def test_return_can_accept_or_reject_without_promotion_authority(self):
        p = make_binding_proposal(
            self.occurrence(),
            left_endpoint=RelationEndpoint("a", "SPAN"),
            right_endpoint=RelationEndpoint("b", "STATE"),
            relation_symbol="R",
            discriminator_id="d",
            author_id="venus",
        )
        out = bind_return(
            p,
            ReturnedBindingJudgment(
                return_id="world:return:1",
                proposal_id=p.proposal_id,
                source_id="world",
                accepted=True,
                provenance_ids=("external-eval",),
            ),
        )
        self.assertEqual(out.disposition, "ACCEPTED_RETURNED_BINDING")
        self.assertIsNotNone(out.typed_relation_id)
        self.assertFalse(out.promotion_authority)

    def test_source_contains_no_target_answer_vocabulary(self):
        import kernel.development.cross_layer_relation_binding as mod
        text = Path(mod.__file__).read_text(encoding="utf-8").casefold()
        for forbidden in (
            "mention != incidence",
            "uncertainty-marker",
            "object-level unresolved",
            "required_target_relation_present",
            "admit if mention",
        ):
            self.assertNotIn(forbidden.casefold(), text)


if __name__ == "__main__":
    unittest.main()
