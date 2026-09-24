from __future__ import annotations

import unittest

from kernel.runtime.vmk2 import (
    AdditiveBackend,
    EvidenceReceipt,
    JurisdictionReceipt,
    PolicyMode,
    ReceiptStatus,
    ReturnRole,
    TransitionPolicy,
    VMK2Error,
    VMK2Reference,
)


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


if __name__ == "__main__":
    unittest.main()
