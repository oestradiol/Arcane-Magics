from __future__ import annotations

import unittest

from kernel.runtime.internalizer import (
    AntiMinervaViolation,
    InternalizationError,
    OStarTransition,
    SubstrateRole,
    carrier_substitution_probe,
    internalize,
    make_artifact,
    validate_ostar,
)


class InternalizerTests(unittest.TestCase):
    def test_scaffold_may_internalize_while_world_return_remains_external(self):
        scaffold = make_artifact(
            role=SubstrateRole.SCAFFOLD,
            payload={"mediator": [1, 2, 3]},
            source_id="external-scaffold",
            provenance_ids=("R193",),
        )
        receipt = internalize(
            scaffold,
            internalized_capability_payload={"weights": [4, 5, 6]},
            original_scaffold_removed=True,
            function_preserved_after_removal=True,
            fresh_world_return_required=True,
        )
        self.assertTrue(receipt.fresh_world_return_required)
        self.assertFalse(receipt.authority_inherited)
        self.assertFalse(receipt.jurisdiction_inherited)
        self.assertFalse(receipt.evaluator_independence_inherited)

    def test_world_return_cannot_be_consumed_as_self_authority(self):
        ret = make_artifact(
            role=SubstrateRole.WORLD_RETURN,
            payload={"score": 1},
            source_id="world",
            provenance_ids=("external",),
        )
        with self.assertRaises(InternalizationError):
            internalize(
                ret,
                internalized_capability_payload={"score": 1},
                original_scaffold_removed=True,
                function_preserved_after_removal=True,
                fresh_world_return_required=True,
            )

    def test_capability_cannot_inherit_authority(self):
        cap = make_artifact(
            role=SubstrateRole.CAPABILITY,
            payload={"tool": "parser"},
            source_id="library",
            provenance_ids=("package-sha",),
        )
        with self.assertRaises(InternalizationError):
            internalize(
                cap,
                internalized_capability_payload={"tool": "parser-local"},
                original_scaffold_removed=True,
                function_preserved_after_removal=True,
                fresh_world_return_required=True,
                authority_inherited=True,
            )


class OStarTests(unittest.TestCase):
    def test_changed_state_can_pass_ostar(self):
        result = validate_ostar(
            OStarTransition(
                before_self_root="before",
                after_self_root="after",
                world_return_id="return-1",
                world_return_source_id="world",
                provenance_reconstructible=True,
                nonpreauthored_return_reachable=True,
                correction_channel_reachable=True,
                reopening_reachable=True,
                self_authorized_success=False,
                self_validated_success=False,
                world_collapsed_into_model=False,
                other_collapsed_into_model=False,
                founder_hidden_dependency=False,
                labels_preserved=False,
                functional_contract_preserved=True,
            )
        )
        self.assertTrue(result.admitted)
        self.assertFalse(result.static_state_equality_required)

    def test_self_sealing_success_fails_ostar(self):
        result = validate_ostar(
            OStarTransition(
                before_self_root="same",
                after_self_root="same",
                world_return_id="return-1",
                world_return_source_id="world",
                provenance_reconstructible=True,
                nonpreauthored_return_reachable=False,
                correction_channel_reachable=False,
                reopening_reachable=False,
                self_authorized_success=True,
                self_validated_success=True,
                world_collapsed_into_model=True,
                other_collapsed_into_model=True,
                founder_hidden_dependency=False,
                labels_preserved=True,
                functional_contract_preserved=False,
            )
        )
        self.assertFalse(result.admitted)
        self.assertIn("correction channel became unreachable", result.failures)
        self.assertIn("World was collapsed into model(World)", result.failures)


class AntiMinervaTests(unittest.TestCase):
    def test_same_content_different_status_carrier_may_not_change_admissibility(self):
        with self.assertRaises(AntiMinervaViolation):
            carrier_substitution_probe(
                semantic_content={"claim": "same consequence-bearing residual"},
                carrier_outcomes={
                    "prestigious-formal-prose": True,
                    "embodied-ridiculous-fart-joke-carrier": False,
                },
            )

    def test_carrier_difference_is_allowed_when_it_is_declared_consequential(self):
        carrier_substitution_probe(
            semantic_content={"instruction": "same bytes"},
            carrier_outcomes={
                "authenticated-control-channel": True,
                "untrusted-web-page": False,
            },
            consequence_relevant_features={
                "authenticated-control-channel": ("authenticated-authority",),
                "untrusted-web-page": ("untrusted-ingress",),
            },
        )


if __name__ == "__main__":
    unittest.main()
