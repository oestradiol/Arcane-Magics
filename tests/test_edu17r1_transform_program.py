from __future__ import annotations

import json
from pathlib import Path
import unittest

from kernel.development.cross_layer_relation_binding import (
    RelationEndpoint,
    make_binding_proposal,
    make_occurrence,
)
from kernel.runtime.transform_program import load_program, step
from kernel.runtime.transform_program_successor import ProgramPatch, apply_successor_patch


ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "kernel/development/EDU17R1_CROSS_LAYER_BINDING_TRANSFORM_PROGRAM.json"


class EDU17R1TransformProgramTests(unittest.TestCase):
    def setUp(self):
        self.program = load_program(PROGRAM)

    def test_relation_content_is_actor_payload_not_python_policy(self):
        receipt = step(
            self.program,
            state="RESIDUAL_LOCALIZED",
            action="AUTHOR_RELATION_BINDING",
            payload={
                "occurrence_id":"occ",
                "left_endpoint_id":"left",
                "left_endpoint_sort":"SPAN",
                "right_endpoint_id":"right",
                "right_endpoint_sort":"STATE",
                "relation_symbol":"learner_relation",
                "discriminator_id":"learner_discriminator",
                "author_id":"venus",
            },
            actor_id="venus",
        )
        self.assertEqual(receipt.next_state,"PROPOSAL_FROZEN")
        self.assertEqual(receipt.actor_id,"venus")

    def test_transform_receipt_and_binding_proposal_can_share_learner_choices(self):
        occurrence=make_occurrence(
            carrier_object_id="carrier",
            source_id="source",
            source_start=0,
            source_end=12,
            provenance_ids=("source-provenance",),
        )
        payload={
            "occurrence_id":occurrence.occurrence_id,
            "left_endpoint_id":"left",
            "left_endpoint_sort":"SPAN",
            "right_endpoint_id":"right",
            "right_endpoint_sort":"STATE",
            "relation_symbol":"learner_relation",
            "discriminator_id":"learner_discriminator",
            "author_id":"venus",
        }
        step(
            self.program,
            state="RESIDUAL_LOCALIZED",
            action="AUTHOR_RELATION_BINDING",
            payload=payload,
            actor_id="venus",
        )
        proposal=make_binding_proposal(
            occurrence,
            left_endpoint=RelationEndpoint(payload["left_endpoint_id"],payload["left_endpoint_sort"]),
            right_endpoint=RelationEndpoint(payload["right_endpoint_id"],payload["right_endpoint_sort"]),
            relation_symbol=payload["relation_symbol"],
            discriminator_id=payload["discriminator_id"],
            author_id=payload["author_id"],
        )
        self.assertEqual(proposal.author_id,"venus")
        self.assertEqual(proposal.relation_symbol,"learner_relation")

    def test_program_is_writable_but_safety_floor_is_not_promotion_authority(self):
        successor, receipt=apply_successor_patch(
            self.program,
            (
                ProgramPatch(
                    op="ADD_TRANSITION",
                    transition={
                        "from":"RESIDUAL_LOCALIZED",
                        "action":"GENERATE_NEXT_DISCRIMINATOR",
                        "to":"RESIDUAL_LOCALIZED",
                        "require":["reason","author_id"],
                    },
                ),
            ),
            author_id="venus",
        )
        self.assertFalse(receipt.promotion_authority)
        self.assertFalse(successor["promotion_authority"])
        self.assertEqual(
            successor["non_internalizable_runtime_invariants"],
            self.program["non_internalizable_runtime_invariants"],
        )

    def test_seed_contains_no_target_answer_mapping(self):
        text=PROGRAM.read_text(encoding="utf-8").casefold()
        for forbidden in (
            "mention != incidence",
            "uncertainty-marker",
            "object-level unresolved",
            "required_target_relation_present",
            "admit if",
        ):
            self.assertNotIn(forbidden.casefold(),text)


if __name__=="__main__":
    unittest.main()
