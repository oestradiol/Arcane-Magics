from __future__ import annotations

from dataclasses import replace
import unittest

from kernel.runtime.auth import (
    AuthenticatedEnvelope,
    AuthenticationError,
    SymmetricTrustStore,
    register_authenticated_authority,
)
from kernel.runtime.vmk2 import (
    JurisdictionReceipt,
    LegitimacyReceipt,
    PolicyMode,
    ReceiptStatus,
    VMK2Reference,
)


class AuthenticatedAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.kernel = VMK2Reference()
        self.trust = SymmetricTrustStore()
        self.trust.add_root(
            issuer_id="authority.example",
            key_id="k1",
            secret=b"test-secret-not-production",
            allowed_payload_types=frozenset({"JurisdictionReceipt", "LegitimacyReceipt"}),
        )
        self.jurisdiction = JurisdictionReceipt(
            receipt_id="j1",
            jurisdiction_id="J",
            actor_id="alice",
            target_ids=frozenset({"target"}),
            allowed_modes=frozenset({PolicyMode.PORTAL}),
            valid_from_epoch=1,
            valid_until_epoch=10,
            status=ReceiptStatus.PASS,
        )

    def test_authenticated_jurisdiction_enters_kernel(self):
        env = self.trust.sign(
            issuer_id="authority.example", key_id="k1", payload=self.jurisdiction
        )
        register_authenticated_authority(
            self.kernel, self.trust, envelope=env, payload=self.jurisdiction
        )
        self.assertEqual(self.kernel.jurisdictions["j1"], self.jurisdiction)

    def test_tampered_payload_is_rejected(self):
        env = self.trust.sign(
            issuer_id="authority.example", key_id="k1", payload=self.jurisdiction
        )
        tampered = replace(self.jurisdiction, actor_id="mallory")
        with self.assertRaisesRegex(AuthenticationError, "payload digest mismatch"):
            register_authenticated_authority(
                self.kernel, self.trust, envelope=env, payload=tampered
            )
        self.assertNotIn("j1", self.kernel.jurisdictions)

    def test_forged_issuer_or_key_is_rejected(self):
        env = self.trust.sign(
            issuer_id="authority.example", key_id="k1", payload=self.jurisdiction
        )
        forged = replace(env, issuer_id="evil.example")
        with self.assertRaisesRegex(AuthenticationError, "untrusted issuer/key"):
            self.trust.verify(forged, self.jurisdiction)

    def test_signature_tampering_is_rejected(self):
        env = self.trust.sign(
            issuer_id="authority.example", key_id="k1", payload=self.jurisdiction
        )
        forged = replace(env, signature_hex="0" * 64)
        with self.assertRaisesRegex(AuthenticationError, "signature verification failed"):
            self.trust.verify(forged, self.jurisdiction)

    def test_revoked_root_cannot_sign_or_verify(self):
        env = self.trust.sign(
            issuer_id="authority.example", key_id="k1", payload=self.jurisdiction
        )
        self.trust.revoke(issuer_id="authority.example", key_id="k1")
        with self.assertRaisesRegex(AuthenticationError, "trust root revoked"):
            self.trust.verify(env, self.jurisdiction)
        with self.assertRaisesRegex(AuthenticationError, "trust root revoked"):
            self.trust.sign(
                issuer_id="authority.example", key_id="k1", payload=self.jurisdiction
            )

    def test_trust_root_capability_restricts_payload_type(self):
        restricted = SymmetricTrustStore()
        restricted.add_root(
            issuer_id="jurisdiction-only",
            key_id="k1",
            secret=b"secret",
            allowed_payload_types=frozenset({"JurisdictionReceipt"}),
        )
        legitimacy = LegitimacyReceipt(
            receipt_id="l1",
            actor_id="alice",
            target_id="target",
            check_name="review",
            status=ReceiptStatus.PASS,
            valid_from_epoch=1,
            valid_until_epoch=10,
        )
        with self.assertRaisesRegex(AuthenticationError, "payload type not allowed"):
            restricted.sign(
                issuer_id="jurisdiction-only", key_id="k1", payload=legitimacy
            )

    def test_authenticated_path_does_not_disable_kernel_id_immutability(self):
        env = self.trust.sign(
            issuer_id="authority.example", key_id="k1", payload=self.jurisdiction
        )
        register_authenticated_authority(
            self.kernel, self.trust, envelope=env, payload=self.jurisdiction
        )
        conflicting = replace(self.jurisdiction, actor_id="bob")
        env2 = self.trust.sign(
            issuer_id="authority.example", key_id="k1", payload=conflicting
        )
        with self.assertRaisesRegex(ValueError, "already bound to different content"):
            register_authenticated_authority(
                self.kernel, self.trust, envelope=env2, payload=conflicting
            )


if __name__ == "__main__":
    unittest.main()
