from __future__ import annotations

import unittest


from kernel.runtime.vmk2 import (
    AdditiveBackend,
    Backend,
    EvidenceReceipt,
    JurisdictionReceipt,
    PolicyMode,
    ReceiptStatus,
    ReturnRole,
    TransitionPolicy,
    VMK2Error,
    VMK2Reference,
    canonical,
    digest,
)


class MutatingBackend(Backend):
    def decode(self, payload):
        return payload

    def update(self, old_value, decoded):
        old_value["items"].append(decoded)
        return old_value


class VMK2CanonicalizationTests(unittest.TestCase):
    def test_unordered_containers_have_order_independent_digest(self):
        left = {"targets": {"beta", "alpha"}, "modes": frozenset({"PORTAL", "WORD"})}
        right = {"modes": frozenset({"WORD", "PORTAL"}), "targets": {"alpha", "beta"}}
        self.assertEqual(canonical(left), canonical(right))
        self.assertEqual(digest(left), digest(right))

    def test_cross_process_fixture_is_exact(self):
        value = {"alpha": frozenset({"z", "a"}), "n": 1.25, "seq": (2, 1)}
        self.assertEqual(
            canonical(value),
            b'{"alpha":["a","z"],"n":1.25,"seq":[2,1]}',
        )
        self.assertEqual(
            digest(value),
            "b0dbdc03c8014b6bad308f71247188797b467f165aa19711aed4d15b41a6ee75",
        )

    def test_nonfinite_numbers_fail_closed(self):
        for value in (
            float("nan"),
            float("inf"),
            float("-inf"),
            {"nested": [1, float("nan")]},
        ):
            with self.subTest(value=value):
                with self.assertRaisesRegex(VMK2Error, "non-finite"):
                    canonical(value)

    def test_non_string_mapping_keys_fail_closed(self):
        with self.assertRaisesRegex(VMK2Error, "string keys"):
            canonical({1: "ambiguous-cross-language-key"})


class VMK2InvariantTests(unittest.TestCase):
    def setUp(self):
        self.vm = VMK2Reference()
        self.vm.register_state("target", 1.0)
        jurisdiction = JurisdictionReceipt(
            "J", "local", "actor", frozenset({"target"}),
            frozenset({PolicyMode.WORD, PolicyMode.PORTAL}),
            0, 100, ReceiptStatus.PASS,
        )
        self.vm.register_jurisdiction(jurisdiction)
        self.vm.register_policy(
            TransitionPolicy("P", "actor", "target", PolicyMode.PORTAL, "J")
        )
        self.vm.register_policy(
            TransitionPolicy("W", "actor", "target", PolicyMode.WORD, "J")
        )
        evidence = self.vm.register_evidence(
            source_id="world",
            assessor_id="external",
            payload=2.0,
            exposure_epoch=1,
        )
        self.ret = self.vm.ingest_return(
            evidence_id=evidence.evidence_id,
            source_id="world",
            target_id="target",
            role=ReturnRole.ENCOUNTER,
            epoch=2,
            nonce="n1",
        )

    def test_portal_transition_consumes_return_once(self):
        receipt = self.vm.transition(
            verified_return_id=self.ret.return_id,
            actor_id="actor",
            target_id="target",
            payload=2.0,
            backend=AdditiveBackend(),
            policy_id="P",
            epoch=3,
        )
        self.assertIsNotNone(receipt)
        self.assertEqual(self.vm.state["target"].value, 3.0)
        with self.assertRaises(VMK2Error):
            self.vm.transition(
                verified_return_id=self.ret.return_id,
                actor_id="actor",
                target_id="target",
                payload=2.0,
                backend=AdditiveBackend(),
                policy_id="P",
                epoch=4,
            )

    def test_transition_rejects_payload_not_bound_to_return_evidence(self):
        before = self.vm.state["target"].root
        with self.assertRaises(VMK2Error):
            self.vm.transition(
                verified_return_id=self.ret.return_id,
                actor_id="actor",
                target_id="target",
                payload=999.0,
                backend=AdditiveBackend(),
                policy_id="P",
                epoch=3,
            )
        self.assertEqual(self.vm.state["target"].root, before)
        self.assertNotIn("n1", self.vm.consumed_nonces)

    def test_word_reconstructs_without_spending_nonce(self):
        before = self.vm.state["target"].root
        result = self.vm.transition(
            verified_return_id=self.ret.return_id,
            actor_id="actor",
            target_id="target",
            payload=2.0,
            backend=AdditiveBackend(),
            policy_id="W",
            epoch=3,
        )
        self.assertIsNone(result)
        self.assertEqual(self.vm.state["target"].root, before)
        self.assertNotIn("n1", self.vm.consumed_nonces)

    def test_authority_ids_cannot_be_rebound(self):
        with self.assertRaises(VMK2Error):
            self.vm.register_jurisdiction(
                JurisdictionReceipt(
                    "J", "other", "actor", frozenset({"target"}),
                    frozenset({PolicyMode.PORTAL}),
                    0, 100, ReceiptStatus.PASS,
                )
            )
        with self.assertRaises(VMK2Error):
            self.vm.register_policy(
                TransitionPolicy("P", "actor", "target", PolicyMode.WORD, "J")
            )

    def test_jurisdiction_denial_fails_closed(self):
        self.vm.register_policy(
            TransitionPolicy("BAD", "intruder", "target", PolicyMode.PORTAL, "J")
        )
        with self.assertRaises(VMK2Error):
            self.vm.transition(
                verified_return_id=self.ret.return_id,
                actor_id="intruder",
                target_id="target",
                payload=2.0,
                backend=AdditiveBackend(),
                policy_id="BAD",
                epoch=3,
            )

    def test_action_return_requires_execution_receipt(self):
        evidence = self.vm.register_evidence(
            source_id="world",
            assessor_id="external",
            payload={"effect": True},
            exposure_epoch=4,
        )
        with self.assertRaises(VMK2Error):
            self.vm.ingest_return(
                evidence_id=evidence.evidence_id,
                source_id="world",
                target_id="target",
                role=ReturnRole.ACTION,
                epoch=5,
                nonce="action-no-receipt",
            )

    def test_action_return_cannot_predate_execution_receipt(self):
        receipt = self.vm.register_execution_receipt(
            action_id="a1", target_id="target", effect={"ok": True}, epoch=10
        )
        evidence = self.vm.register_evidence(
            source_id="world",
            assessor_id="external",
            payload={"effect": True},
            exposure_epoch=4,
        )
        with self.assertRaises(VMK2Error):
            self.vm.ingest_return(
                evidence_id=evidence.evidence_id,
                source_id="world",
                target_id="target",
                role=ReturnRole.ACTION,
                epoch=5,
                nonce="return-before-action",
                receipt_id=receipt.receipt_id,
            )

    def test_reopening_requires_strict_future_expansion_and_bound_separator(self):
        ev = self.vm.register_evidence(
            source_id="world",
            assessor_id="external",
            payload={"difference": 1},
            exposure_epoch=4,
        )
        projection = self.vm.register_projection(
            future_family={"f1"},
            evidence_ids={ev.evidence_id},
            payload={"q": "collapsed"},
        )
        with self.assertRaises(VMK2Error):
            self.vm.reopen_projection(
                projection_id=projection.projection_id,
                expanded_future_family={"f1"},
                separator_evidence_id=ev.evidence_id,
                separator={"difference": 1},
                epoch=5,
            )
        reopened = self.vm.reopen_projection(
            projection_id=projection.projection_id,
            expanded_future_family={"f1", "f2"},
            separator_evidence_id=ev.evidence_id,
            separator={"difference": 1},
            epoch=5,
        )
        self.assertEqual(reopened.expanded_future_family, frozenset({"f1", "f2"}))

    def test_register_state_owns_mutable_value(self):
        source = {"items": [1]}
        vm = VMK2Reference()
        vm.register_state("mutable", source)
        source["items"].append(999)
        self.assertEqual(vm.state["mutable"].value, {"items": [1]})
        self.assertEqual(
            vm.state["mutable"].root,
            __import__("kernel.runtime.vmk2", fromlist=["digest"]).digest(
                {"id": "mutable", "value": {"items": [1]}}
            ),
        )

    def test_external_alias_mutation_is_detected_before_transition(self):
        vm = VMK2Reference()
        original = {"items": [1]}
        vm.register_state("target", original)
        j = JurisdictionReceipt(
            "J2", "local", "actor", frozenset({"target"}),
            frozenset({PolicyMode.PORTAL}), 0, 100, ReceiptStatus.PASS
        )
        vm.register_jurisdiction(j)
        vm.register_policy(TransitionPolicy("P2", "actor", "target", PolicyMode.PORTAL, "J2"))
        ev = vm.register_evidence(source_id="world", assessor_id="external", payload=2, exposure_epoch=1)
        ret = vm.ingest_return(
            evidence_id=ev.evidence_id, source_id="world", target_id="target",
            role=ReturnRole.ENCOUNTER, epoch=2, nonce="mutable-alias"
        )
        # Simulate hostile/corrupt internal mutation after custody.
        vm.state["target"].value["items"].append(7)
        with self.assertRaisesRegex(VMK2Error, "state root drift"):
            vm.transition(
                verified_return_id=ret.return_id, actor_id="actor", target_id="target",
                payload=2, backend=MutatingBackend(), policy_id="P2", epoch=3
            )

    def test_mutating_backend_cannot_rewrite_prior_state_object(self):
        vm = VMK2Reference()
        prior = vm.register_state("target", {"items": [1]})
        j = JurisdictionReceipt(
            "J3", "local", "actor", frozenset({"target"}),
            frozenset({PolicyMode.PORTAL}), 0, 100, ReceiptStatus.PASS
        )
        vm.register_jurisdiction(j)
        vm.register_policy(TransitionPolicy("P3", "actor", "target", PolicyMode.PORTAL, "J3"))
        ev = vm.register_evidence(source_id="world", assessor_id="external", payload=2, exposure_epoch=1)
        ret = vm.ingest_return(
            evidence_id=ev.evidence_id, source_id="world", target_id="target",
            role=ReturnRole.ENCOUNTER, epoch=2, nonce="mutating-backend"
        )
        receipt = vm.transition(
            verified_return_id=ret.return_id, actor_id="actor", target_id="target",
            payload=2, backend=MutatingBackend(), policy_id="P3", epoch=3
        )
        self.assertEqual(prior.value, {"items": [1]})
        self.assertEqual(vm.state["target"].value, {"items": [1, 2]})
        self.assertNotEqual(receipt.before_root, receipt.after_root)


if __name__ == "__main__":
    unittest.main()
