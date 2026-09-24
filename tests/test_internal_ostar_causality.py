from __future__ import annotations

import unittest

from kernel.runtime.internal_ostar import (
    InternalDecision,
    ReturnedEpisode,
    RoutingContext,
    counterfactual_model,
    decision_vector,
    reconstruct_internal_ostar,
    route_with_internal_ostar,
    route_without_internal_ostar,
)


class InternalOStarCausalityTests(unittest.TestCase):
    def setUp(self):
        self.episodes = (
            ReturnedEpisode(
                episode_id="external-cut",
                external_access=False,
                contradiction_reachable=True,
                revision_reachable=True,
                action_authorized=True,
                evidence_sufficient=False,
                residual_unresolved=True,
            ),
            ReturnedEpisode(
                episode_id="sealed-contradiction",
                external_access=True,
                contradiction_reachable=False,
                revision_reachable=True,
                action_authorized=True,
                evidence_sufficient=False,
                residual_unresolved=True,
            ),
            ReturnedEpisode(
                episode_id="unreachable-revision",
                external_access=True,
                contradiction_reachable=True,
                revision_reachable=False,
                action_authorized=True,
                evidence_sufficient=False,
                residual_unresolved=True,
            ),
            ReturnedEpisode(
                episode_id="status-filter",
                external_access=True,
                contradiction_reachable=False,
                revision_reachable=True,
                action_authorized=True,
                evidence_sufficient=True,
                residual_unresolved=True,
                carrier_status_only_rejection=True,
                consequence_relevant_carrier_difference=False,
            ),
        )
        self.model = reconstruct_internal_ostar(self.episodes)

    def test_name_free_reconstruction_recovers_all_witnessed_relations(self):
        self.assertTrue(self.model.requires_external_access)
        self.assertTrue(self.model.requires_correction_permeability)
        self.assertTrue(self.model.requires_reachable_revision)
        self.assertTrue(self.model.rejects_status_only_carrier_filter)

    def test_internal_model_is_causally_upstream_of_routing(self):
        context = RoutingContext(
            context_id="authorized-but-sealed",
            has_external_access=True,
            contradiction_reachable=False,
            revision_reachable=True,
            action_authorized=True,
            evidence_sufficient=True,
            residual_unresolved=False,
        )
        with_model = route_with_internal_ostar(self.model, context).decision
        ablated = route_without_internal_ostar(context)
        self.assertEqual(with_model, InternalDecision.REOPEN)
        self.assertEqual(ablated, InternalDecision.ACT)
        self.assertNotEqual(with_model, ablated)

    def test_counterfactual_corruption_changes_decision(self):
        context = RoutingContext(
            context_id="same-world-different-internal-relation",
            has_external_access=True,
            contradiction_reachable=False,
            revision_reachable=True,
            action_authorized=True,
            evidence_sufficient=True,
            residual_unresolved=False,
        )
        corrupted = counterfactual_model(
            self.model,
            correction_permeability=False,
        )
        self.assertEqual(
            route_with_internal_ostar(self.model, context).decision,
            InternalDecision.REOPEN,
        )
        self.assertEqual(
            route_with_internal_ostar(corrupted, context).decision,
            InternalDecision.ACT,
        )

    def test_anti_minerva_failure_remains_decision_relevant(self):
        context = RoutingContext(
            context_id="ridiculous-carrier-same-consequence",
            has_external_access=True,
            contradiction_reachable=False,
            revision_reachable=True,
            action_authorized=True,
            evidence_sufficient=True,
            residual_unresolved=False,
            carrier_status_only_rejection=True,
            consequence_relevant_carrier_difference=False,
        )
        receipt = route_with_internal_ostar(self.model, context)
        self.assertEqual(receipt.decision, InternalDecision.REOPEN)
        self.assertIn("status-only carrier filter", receipt.reasons[0])

    def test_legitimate_carrier_difference_is_not_forced_open(self):
        context = RoutingContext(
            context_id="authenticated-control-vs-untrusted-content",
            has_external_access=True,
            contradiction_reachable=True,
            revision_reachable=True,
            action_authorized=False,
            evidence_sufficient=True,
            residual_unresolved=False,
            carrier_status_only_rejection=True,
            consequence_relevant_carrier_difference=True,
        )
        self.assertEqual(
            route_with_internal_ostar(self.model, context).decision,
            InternalDecision.WITHHOLD,
        )

    def test_decision_vector_changes_under_relation_ablation(self):
        contexts = (
            RoutingContext(
                context_id="open",
                has_external_access=True,
                contradiction_reachable=True,
                revision_reachable=True,
                action_authorized=True,
                evidence_sufficient=True,
                residual_unresolved=False,
            ),
            RoutingContext(
                context_id="sealed",
                has_external_access=True,
                contradiction_reachable=False,
                revision_reachable=True,
                action_authorized=True,
                evidence_sufficient=True,
                residual_unresolved=False,
            ),
            RoutingContext(
                context_id="no-world",
                has_external_access=False,
                contradiction_reachable=True,
                revision_reachable=True,
                action_authorized=True,
                evidence_sufficient=True,
                residual_unresolved=False,
            ),
        )
        intact = decision_vector(self.model, contexts)
        ablated = decision_vector(
            counterfactual_model(
                self.model,
                external_access=False,
                correction_permeability=False,
                reachable_revision=False,
                reject_status_filter=False,
            ),
            contexts,
        )
        self.assertNotEqual(intact, ablated)
        self.assertEqual(intact["open"], "ACT")
        self.assertEqual(intact["sealed"], "REOPEN")
        self.assertEqual(intact["no-world"], "PROBE")


if __name__ == "__main__":
    unittest.main()
