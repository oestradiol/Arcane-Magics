from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
import hashlib
import hmac
from typing import Any, Dict, FrozenSet, Mapping

from .vmk2 import (
    JurisdictionReceipt,
    LegitimacyReceipt,
    VMK2Error,
    VMK2Reference,
    canonical,
    digest,
)


class AuthenticationError(VMK2Error):
    pass


@dataclass(frozen=True)
class AuthenticatedEnvelope:
    envelope_id: str
    issuer_id: str
    key_id: str
    payload_type: str
    payload_digest: str
    signature_hex: str


@dataclass(frozen=True)
class TrustRoot:
    issuer_id: str
    key_id: str
    secret: bytes
    allowed_payload_types: FrozenSet[str]
    revoked: bool = False


def _payload_type(payload: Any) -> str:
    return type(payload).__name__


def _signed_body(
    *,
    issuer_id: str,
    key_id: str,
    payload_type: str,
    payload_digest: str,
) -> dict[str, str]:
    return {
        "issuer_id": issuer_id,
        "key_id": key_id,
        "payload_type": payload_type,
        "payload_digest": payload_digest,
    }


def _signature(secret: bytes, body: Mapping[str, str]) -> str:
    return hmac.new(secret, canonical(dict(body)), hashlib.sha256).hexdigest()


class SymmetricTrustStore:
    """Bounded authenticated adapter for VMK2 authority receipts.

    This is a deployment/test boundary using pre-shared symmetric trust roots.
    It proves that a receipt was authenticated under a configured shared secret.
    It does not implement public-key identity, PKI, remote attestation, or
    cross-organization key distribution.
    """

    def __init__(self) -> None:
        self._roots: Dict[tuple[str, str], TrustRoot] = {}

    def add_root(
        self,
        *,
        issuer_id: str,
        key_id: str,
        secret: bytes,
        allowed_payload_types: FrozenSet[str],
    ) -> TrustRoot:
        if not issuer_id or not key_id or not secret:
            raise AuthenticationError("issuer_id, key_id and non-empty secret required")
        if not allowed_payload_types:
            raise AuthenticationError("allowed_payload_types must be non-empty")
        key = (issuer_id, key_id)
        root = TrustRoot(issuer_id, key_id, bytes(secret), allowed_payload_types, False)
        existing = self._roots.get(key)
        if existing is not None and existing != root:
            raise AuthenticationError("trust root identity already bound to different content")
        self._roots[key] = root
        return root

    def revoke(self, *, issuer_id: str, key_id: str) -> None:
        key = (issuer_id, key_id)
        root = self._roots.get(key)
        if root is None:
            raise AuthenticationError("unknown trust root")
        self._roots[key] = TrustRoot(
            root.issuer_id,
            root.key_id,
            root.secret,
            root.allowed_payload_types,
            True,
        )

    def sign(self, *, issuer_id: str, key_id: str, payload: Any) -> AuthenticatedEnvelope:
        root = self._roots.get((issuer_id, key_id))
        if root is None:
            raise AuthenticationError("unknown trust root")
        if root.revoked:
            raise AuthenticationError("trust root revoked")
        ptype = _payload_type(payload)
        if ptype not in root.allowed_payload_types:
            raise AuthenticationError("payload type not allowed for trust root")
        pdigest = digest(payload)
        body = _signed_body(
            issuer_id=issuer_id,
            key_id=key_id,
            payload_type=ptype,
            payload_digest=pdigest,
        )
        sig = _signature(root.secret, body)
        eid = digest({**body, "signature_hex": sig})
        return AuthenticatedEnvelope(
            eid, issuer_id, key_id, ptype, pdigest, sig
        )

    def verify(self, envelope: AuthenticatedEnvelope, payload: Any) -> None:
        root = self._roots.get((envelope.issuer_id, envelope.key_id))
        if root is None:
            raise AuthenticationError("untrusted issuer/key")
        if root.revoked:
            raise AuthenticationError("trust root revoked")
        ptype = _payload_type(payload)
        if ptype != envelope.payload_type:
            raise AuthenticationError("payload type mismatch")
        if ptype not in root.allowed_payload_types:
            raise AuthenticationError("payload type not authorized by trust root")
        pdigest = digest(payload)
        if pdigest != envelope.payload_digest:
            raise AuthenticationError("payload digest mismatch")
        body = _signed_body(
            issuer_id=envelope.issuer_id,
            key_id=envelope.key_id,
            payload_type=envelope.payload_type,
            payload_digest=envelope.payload_digest,
        )
        expected = _signature(root.secret, body)
        if not hmac.compare_digest(expected, envelope.signature_hex):
            raise AuthenticationError("signature verification failed")
        expected_id = digest({**body, "signature_hex": envelope.signature_hex})
        if expected_id != envelope.envelope_id:
            raise AuthenticationError("envelope identity mismatch")


def register_authenticated_authority(
    kernel: VMK2Reference,
    trust: SymmetricTrustStore,
    *,
    envelope: AuthenticatedEnvelope,
    payload: JurisdictionReceipt | LegitimacyReceipt,
) -> None:
    trust.verify(envelope, payload)
    if isinstance(payload, JurisdictionReceipt):
        kernel.register_jurisdiction(payload)
        return
    if isinstance(payload, LegitimacyReceipt):
        kernel.register_legitimacy(payload)
        return
    raise AuthenticationError("unsupported authority payload")
