from __future__ import annotations

import unittest

from kernel.development.relation_feature_adapter import (
    RelationObservation,
    relation_features,
)


class RelationFeatureAdapterTests(unittest.TestCase):
    def test_full_relation_observation_sets_all_neutral_coordinates(self):
        obs = RelationObservation(
            source_start=10,
            source_end=20,
            provenance_ids=("source-a",),
            operator="ARROW",
            left_endpoint="left clause",
            right_endpoint="right clause",
            typed_relation_id="relation-1",
            return_id="return-1",
        )
        self.assertEqual(relation_features(obs), (1, 1, 1, 1, 1, 1))

    def test_surface_occurrence_without_binding_does_not_fake_typed_relation(self):
        obs = RelationObservation(
            source_start=10,
            source_end=20,
            provenance_ids=("source-a",),
            operator="NEQ",
            left_endpoint="left clause",
            right_endpoint="right clause",
            typed_relation_id=None,
            return_id=None,
        )
        self.assertEqual(relation_features(obs), (1, 1, 1, 1, 0, 0))

    def test_adapter_has_no_target_specific_policy(self):
        import inspect
        from kernel.development import relation_feature_adapter as mod

        text = inspect.getsource(mod).casefold()
        for forbidden in (
            "mention != incidence",
            "uncertainty-marker",
            "object-level unresolved",
            "required_target_relation_present",
            "admit if",
            "reject if",
        ):
            self.assertNotIn(forbidden.casefold(), text)


if __name__ == "__main__":
    unittest.main()
