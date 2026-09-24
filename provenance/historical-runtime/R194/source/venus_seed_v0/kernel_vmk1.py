from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
import json
from pathlib import Path
from typing import Any

from .canonical import canonical_json, digest
from .model import (
    Authorization, EpistemicStatus, GovernanceDisposition, GovernanceRecord,
    Projection, Proposal, Provenance, Residual, SemanticContext, Relation,
    Warrant,
)
from .runtime import OntogeneticVM


def _payload(value: Any) -> Any:
    """JSON-native, deterministic representation preserving all declared dataclass fields."""
    return json.loads(canonical_json(value))


class CheckStatus(str, Enum):
    PASS = "PASS"
    WITHHOLD = "WITHHOLD"
    FAIL = "FAIL"


class ReturnSourceKind(str, Enum):
    WORLD = "WORLD"
    OTHER_CENTER = "OTHER_CENTER"
    INDEPENDENT_EVALUATOR = "INDEPENDENT_EVALUATOR"
    EXECUTION_ACK = "EXECUTION_ACK"
    SELF_DERIVED = "SELF_DERIVED"


class CompensationDisposition(str, Enum):
    ASSIMILATE = "ASSIMILATE"
    WITHHOLD = "WITHHOLD"
    NO_EFFECT = "NO_EFFECT"


@dataclass(frozen=True)
class GovernanceCheck:
    name: str
    status: CheckStatus
    reason: str = ""


@dataclass(frozen=True)
class GovernanceEnvelope:
    capability_allowed: bool = True
    boundary_ok: bool = True
    authority_ok: bool = True
    warrant_required: bool = False
    required_checks: tuple[str, ...] = ()
    legitimacy_checks: tuple[GovernanceCheck, ...] = ()


@dataclass(frozen=True)
class NonPreauthorshipWarrant:
    assessor_id: str
    status: EpistemicStatus
    evidence_ids: tuple[str, ...] = ()
    reason: str = ""


@dataclass(frozen=True)
class ExternalReturn:
    id: str
    receipt_id: str | None
    interface: str
    source_id: str
    source_kind: ReturnSourceKind
    value: Any
    provenance: Provenance
    npr_warrant: NonPreauthorshipWarrant
    jurisdiction: str = ""
    future_family: tuple[str, ...] = ()
    prior_trajectory_head: str = ""


@dataclass(frozen=True)
class ExternalReturnVerification:
    id: str
    return_id: str
    passed: bool
    npr_supported: bool
    receipt_bound: bool
    interface_bound: bool
    provenance_bound: bool
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class CompensationRecord:
    id: str
    return_id: str
    disposition: CompensationDisposition
    learner_state_before: str
    learner_state_after: str
    affected_ids: tuple[str, ...]
    residual_ids: tuple[str, ...] = ()
    future_family: tuple[str, ...] = ()
    provenance: Provenance = Provenance()
    developmentally_closed: bool = False


class VenusKernelVMK1(OntogeneticVM):
    """Strict successor kernel over the R154 historical runtime.

    VMK-1 is deliberately post-differentiation. It strengthens the execution/return,
    provenance, governance, compensation, and reopening boundaries without mutating
    the historical R154 executable witness.
    """

    FOCAL_SYSTEM_ID = "venus-kernel-vmk1"
    ROOT_CLAIM_STATUS = "OPEN"
    KERNEL_VERSION = "VMK1_v0.1"

    _VMK1_RESERVED = frozenset({
        "PROJECTION", "REOPENING", "EFFECT_VERIFICATION", "COMPENSATION",
        "DEVELOPMENTAL_CLOSURE",
    })

    def __init__(self, journal_path: str | Path | None = None, adapter=None):
        self.pending_executions: dict[str, dict[str, Any]] = {}
        self.external_returns: dict[str, dict[str, Any]] = {}
        self.return_verifications: dict[str, dict[str, Any]] = {}
        self.compensation_records: dict[str, dict[str, Any]] = {}
        self.projections: dict[str, dict[str, Any]] = {}
        self.reopenings: list[dict[str, Any]] = []
        super().__init__(journal_path=journal_path, adapter=adapter)

    def _reduce(self, kind, p):
        super()._reduce(kind, p)
        if kind == "EXECUTION" and p.get("kernel") == self.KERNEL_VERSION:
            self.pending_executions[p["id"]] = p
        elif kind == "RETURN" and p.get("kernel") == self.KERNEL_VERSION:
            self.external_returns[p["id"]] = p
        elif kind == "VERIFICATION" and p.get("kernel") == self.KERNEL_VERSION and p.get("verification_type") == "EXTERNAL_RETURN":
            self.return_verifications[p["return_id"]] = p
        elif kind == "COMPENSATION" and p.get("kernel") == self.KERNEL_VERSION:
            self.compensation_records[p["return_id"]] = p
        elif kind == "PROJECTION" and p.get("kernel") == self.KERNEL_VERSION:
            self.projections[p["id"]] = p
        elif kind == "REOPENING" and p.get("kernel") == self.KERNEL_VERSION:
            self.reopenings.append(p)

    # ------------------------------------------------------------------
    # Full-fidelity typed state registration
    # ------------------------------------------------------------------
    def register_context(self, c: SemanticContext):
        cid = digest(c)
        body = _payload(c)
        body.update({"id": cid, "kernel": self.KERNEL_VERSION, "schema": "SemanticContext/full"})
        self._record("CONTEXT", body, route=("semantic", "full-fidelity"), source=self.FOCAL_SYSTEM_ID)
        return cid

    def register_relation(self, r: Relation):
        if r.context_id not in self.contexts:
            raise ValueError("unknown context")
        body = _payload(r)
        body.update({"kernel": self.KERNEL_VERSION, "schema": "Relation/full"})
        self._record("RELATION", body, route=("relation", "full-fidelity"), source=self.FOCAL_SYSTEM_ID)
        return r.id

    def retain_residual(self, r: Residual):
        body = _payload(r)
        body.update({"kernel": self.KERNEL_VERSION, "schema": "Residual/full"})
        self._record("RESIDUAL", body, route=("residual", "full-fidelity"), source=self.FOCAL_SYSTEM_ID)
        return r.id

    def register_projection(self, projection: Projection, *, evidence_ids: tuple[str, ...] = ()):
        if not projection.future_family:
            raise ValueError("projection requires declared future_family")
        body = _payload(projection)
        body.update({
            "kernel": self.KERNEL_VERSION,
            "schema": "Projection/full",
            "evidence_ids": list(evidence_ids),
            "reopenable": True,
        })
        self._record("PROJECTION", body, route=("compression", "future-family"), source=self.FOCAL_SYSTEM_ID)
        return projection.id

    def reopen_projection(
        self,
        projection_id: str,
        *,
        expanded_future_family: tuple[str, ...],
        discriminator: str,
        source_ids: tuple[str, ...] = (),
    ) -> Residual:
        p = self.projections.get(projection_id)
        if p is None:
            raise ValueError("unknown projection")
        old_f = tuple(p.get("future_family", ()))
        new_f = tuple(expanded_future_family)
        if not set(old_f).issubset(set(new_f)) or set(new_f) == set(old_f):
            raise ValueError("reopening requires a strict future-family expansion")
        if not discriminator.strip():
            raise ValueError("reopening requires a separator/discriminator")
        rid = digest({"projection": projection_id, "F": new_f, "discriminator": discriminator, "sources": source_ids})
        residual = Residual(
            rid,
            "previously lawful compression separated under expanded future family",
            (projection_id,),
            discriminator,
            discriminator,
            Provenance(sources=tuple(source_ids), parents=(projection_id,), route=("projection", "reopen"), authoring=(self.FOCAL_SYSTEM_ID,)),
        )
        self.retain_residual(residual)
        body = {
            "id": digest({"reopen": rid}),
            "kernel": self.KERNEL_VERSION,
            "projection_id": projection_id,
            "prior_future_family": list(old_f),
            "expanded_future_family": list(new_f),
            "discriminator": discriminator,
            "residual_id": rid,
            "source_ids": list(source_ids),
        }
        self._record("REOPENING", body, route=("compression", "reopen"), source=self.FOCAL_SYSTEM_ID)
        return residual

    # ------------------------------------------------------------------
    # Governance / authorization / execution. No fabricated RETURN.
    # ------------------------------------------------------------------
    @staticmethod
    def _governance_disposition(proposal: Proposal, warrant: Warrant | None, g: GovernanceEnvelope):
        if not g.capability_allowed:
            return GovernanceDisposition.REJECT_CUT, "capability unavailable", None
        if not g.boundary_ok:
            return GovernanceDisposition.WITHHOLD, "boundary mismatch", "matching boundary"
        if not g.authority_ok:
            return GovernanceDisposition.REJECT_CUT, "authority denied", None
        if warrant is None and g.warrant_required:
            return GovernanceDisposition.WITHHOLD, "required warrant absent", "lawful warrant"
        if warrant is not None:
            if warrant.status is EpistemicStatus.LICENSE_NOT:
                return GovernanceDisposition.REJECT_CUT, "warrant explicitly denies license", None
            if warrant.status is EpistemicStatus.UNDETERMINED:
                return GovernanceDisposition.WITHHOLD, "warrant undetermined", "new evidence"

        checks = {c.name: c for c in g.legitimacy_checks}
        for name in g.required_checks:
            c = checks.get(name)
            if c is None:
                return GovernanceDisposition.WITHHOLD, f"required legitimacy check missing: {name}", name
            if c.status is CheckStatus.FAIL:
                return GovernanceDisposition.REJECT_CUT, f"legitimacy failed: {name}: {c.reason}", None
            if c.status is CheckStatus.WITHHOLD:
                return GovernanceDisposition.WITHHOLD, f"legitimacy unresolved: {name}: {c.reason}", name
        return GovernanceDisposition.ADMIT, "admitted", None

    def enact(
        self,
        proposal: Proposal,
        warrant: Warrant | None,
        *,
        governance: GovernanceEnvelope | None = None,
        capability_allowed: bool | None = None,
        boundary_ok: bool | None = None,
        return_source: str | None = None,
        return_interface: str | None = None,
    ):
        # Legacy keyword compatibility is accepted only as input plumbing; VMK-1 still
        # evaluates capability, authority and legitimacy as distinct fields.
        g = governance or GovernanceEnvelope()
        if capability_allowed is not None or boundary_ok is not None:
            g = GovernanceEnvelope(
                capability_allowed=g.capability_allowed if capability_allowed is None else capability_allowed,
                boundary_ok=g.boundary_ok if boundary_ok is None else boundary_ok,
                authority_ok=g.authority_ok,
                warrant_required=g.warrant_required,
                required_checks=g.required_checks,
                legitimacy_checks=g.legitimacy_checks,
            )

        disposition, reason, reopen_when = self._governance_disposition(proposal, warrant, g)
        gid = digest({
            "proposal": proposal.id,
            "disposition": disposition.value,
            "reason": reason,
            "governance": _payload(g),
            "warrant": _payload(warrant) if warrant is not None else None,
        })
        record = GovernanceRecord(gid, proposal.id, disposition, reason, reopen_when)
        self._record(
            "GOVERNANCE",
            {
                "id": record.id,
                "proposal": proposal.id,
                "disposition": record.disposition.value,
                "reason": record.reason,
                "reopen_when": record.reopen_when,
                "governance": _payload(g),
                "warrant": _payload(warrant) if warrant is not None else None,
                "kernel": self.KERNEL_VERSION,
            },
            route=("governance", "authority", "legitimacy"),
            source=self.FOCAL_SYSTEM_ID,
        )
        valid = disposition is GovernanceDisposition.ADMIT
        auth = Authorization(
            digest({"p": proposal.id, "g": record.id, "ok": valid}),
            proposal.id,
            record.id,
            proposal.capability,
            proposal.effect_scope,
            valid,
        )
        self._record(
            "AUTHORIZATION",
            {**_payload(auth), "kernel": self.KERNEL_VERSION},
            route=("authorization",), source=self.FOCAL_SYSTEM_ID,
        )
        if not auth.valid:
            return {
                "governance": record, "authorization": auth, "receipt": None,
                "effect_verification": None, "consequence": None,
                "action_committed": False, "committed": False,
                "developmentally_closed": False,
            }

        receipt = self.bridge.execute(proposal, auth)
        execution_payload = {
            **_payload(receipt),
            "kernel": self.KERNEL_VERSION,
            "proposal": _payload(proposal),
            "expected_interface": proposal.expected_interface,
            "legacy_return_label_ignored": {
                "source": return_source, "interface": return_interface,
            } if (return_source is not None or return_interface is not None) else None,
        }
        self._record(
            "EXECUTION", execution_payload,
            route=("vm-os-bridge", "execution"), source="effect-adapter",
        )

        # Execution verification validates only the effect receipt. It is deliberately
        # not a Reality/Other return and cannot satisfy NPR.
        effect_ok = bool(receipt.success and receipt.proposal_id == proposal.id and receipt.authorization_id == auth.id)
        effect_verification = {
            "id": digest({"receipt": receipt.id, "effect_ok": effect_ok}),
            "receipt_id": receipt.id,
            "passed": effect_ok,
            "verification_type": "EXECUTION_EFFECT",
            "kernel": self.KERNEL_VERSION,
        }
        self._record(
            "EFFECT_VERIFICATION", effect_verification,
            route=("verification", "effect-only"), source=self.FOCAL_SYSTEM_ID,
        )
        action_committed = False
        if effect_ok:
            self._record(
                "COMMIT",
                {
                    "commit_type": "ACTION_EFFECT",
                    "proposal": proposal.id,
                    "receipt": receipt.id,
                    "verification": effect_verification["id"],
                    "kernel": self.KERNEL_VERSION,
                },
                route=("action-writeback",), source=self.FOCAL_SYSTEM_ID,
            )
            action_committed = True
        return {
            "governance": record, "authorization": auth, "receipt": receipt,
            "effect_verification": effect_verification, "consequence": None,
            "action_committed": action_committed, "committed": action_committed,
            "developmentally_closed": False,
        }

    # ------------------------------------------------------------------
    # External / Other return and NPR verification
    # ------------------------------------------------------------------
    def register_external_return(
        self,
        *,
        value: Any,
        source_id: str,
        source_kind: ReturnSourceKind,
        interface: str,
        provenance: Provenance,
        npr_warrant: NonPreauthorshipWarrant,
        receipt_id: str | None = None,
        jurisdiction: str = "",
        future_family: tuple[str, ...] = (),
    ) -> ExternalReturn:
        if receipt_id is not None and receipt_id not in self.pending_executions:
            raise ValueError("return references unknown VMK-1 receipt")
        prior_head = self.journal.head
        body_no_id = {
            "receipt_id": receipt_id,
            "interface": interface,
            "source_id": source_id,
            "source_kind": source_kind.value,
            "value": _payload(value),
            "provenance": _payload(provenance),
            "npr_warrant": _payload(npr_warrant),
            "jurisdiction": jurisdiction,
            "future_family": list(future_family),
            "prior_trajectory_head": prior_head,
        }
        rid = digest(body_no_id)
        ret = ExternalReturn(
            rid, receipt_id, interface, source_id, source_kind, value, provenance,
            npr_warrant, jurisdiction, tuple(future_family), prior_head,
        )
        payload = {"id": rid, **body_no_id, "kernel": self.KERNEL_VERSION, "schema": "ExternalReturn/full"}
        self._record("RETURN", payload, route=("World/Other", "RETURN"), source=source_id)
        return ret

    def verify_external_return(self, return_id: str) -> ExternalReturnVerification:
        p = self.external_returns.get(return_id)
        if p is None:
            raise ValueError("unknown external return")
        reasons: list[str] = []

        source_kind = ReturnSourceKind(p["source_kind"])
        npr = p["npr_warrant"]
        prov = p["provenance"]
        source_id = p["source_id"]

        eligible_kind = source_kind in {
            ReturnSourceKind.WORLD,
            ReturnSourceKind.OTHER_CENTER,
            ReturnSourceKind.INDEPENDENT_EVALUATOR,
        }
        if not eligible_kind:
            reasons.append("source kind is NPR-ineligible")
        if source_id == self.FOCAL_SYSTEM_ID:
            reasons.append("focal system cannot author its own NPR witness")
        if source_id not in tuple(prov.get("authoring", ())):
            reasons.append("source/authorship provenance mismatch")
        if not tuple(prov.get("sources", ())):
            reasons.append("return provenance has no source")

        npr_status = EpistemicStatus(npr["status"])
        npr_supported = (
            eligible_kind
            and source_id != self.FOCAL_SYSTEM_ID
            and npr_status is EpistemicStatus.LICENSE
            and bool(npr.get("evidence_ids"))
            and bool(npr.get("assessor_id"))
            and npr.get("assessor_id") != self.FOCAL_SYSTEM_ID
        )
        if npr_status is EpistemicStatus.UNDETERMINED:
            reasons.append("nonpreauthorship undetermined")
        elif npr_status is EpistemicStatus.LICENSE_NOT:
            reasons.append("nonpreauthorship denied")
        elif not npr.get("evidence_ids"):
            reasons.append("nonpreauthorship lacks evidence handle")
        elif npr.get("assessor_id") == self.FOCAL_SYSTEM_ID:
            reasons.append("focal system cannot self-license NPR")

        receipt_bound = True
        interface_bound = True
        receipt_id = p.get("receipt_id")
        if receipt_id is not None:
            execution = self.pending_executions.get(receipt_id)
            if execution is None:
                receipt_bound = False
                reasons.append("unknown receipt")
            else:
                expected = execution.get("expected_interface")
                if expected and p.get("interface") != expected:
                    interface_bound = False
                    reasons.append("return interface does not match proposal expectation")

        provenance_bound = (
            source_id in tuple(prov.get("authoring", ()))
            and bool(tuple(prov.get("sources", ())))
        )
        passed = bool(npr_supported and receipt_bound and interface_bound and provenance_bound)
        vid = digest({"return": return_id, "passed": passed, "reasons": reasons})
        v = ExternalReturnVerification(
            vid, return_id, passed, npr_supported, receipt_bound,
            interface_bound, provenance_bound, tuple(reasons),
        )
        self._record(
            "VERIFICATION",
            {
                **_payload(v),
                "kernel": self.KERNEL_VERSION,
                "verification_type": "EXTERNAL_RETURN",
            },
            route=("verification", "NPR", "attribution"), source=self.FOCAL_SYSTEM_ID,
        )
        return v

    # ------------------------------------------------------------------
    # Compensation / developmental closure. ProjectState remains untouched.
    # ------------------------------------------------------------------
    def compensate(
        self,
        return_id: str,
        *,
        disposition: CompensationDisposition,
        learner_state_before: str,
        learner_state_after: str,
        affected_ids: tuple[str, ...],
        residual_ids: tuple[str, ...] = (),
        future_family: tuple[str, ...] = (),
        provenance: Provenance = Provenance(),
    ) -> CompensationRecord:
        verification = self.return_verifications.get(return_id)
        if not verification or not verification.get("passed"):
            raise ValueError("compensation requires a verified external return")
        if any(not str(x).startswith("learner:") for x in affected_ids):
            raise ValueError("VMK-1 compensation may directly name only learner:* state")
        if disposition is CompensationDisposition.ASSIMILATE:
            if learner_state_before == learner_state_after:
                raise ValueError("assimilation requires changed learner-state digest")
        elif disposition is CompensationDisposition.WITHHOLD:
            if not residual_ids:
                raise ValueError("WITHHOLD compensation requires explicit Residual path")
            if learner_state_before != learner_state_after:
                raise ValueError("WITHHOLD may not silently mutate learner state")
        elif disposition is CompensationDisposition.NO_EFFECT:
            if learner_state_before != learner_state_after:
                raise ValueError("NO_EFFECT may not mutate learner state")

        closed = disposition is CompensationDisposition.ASSIMILATE and learner_state_before != learner_state_after
        cid = digest({
            "return": return_id,
            "disposition": disposition.value,
            "before": learner_state_before,
            "after": learner_state_after,
            "affected": affected_ids,
            "residuals": residual_ids,
            "future_family": future_family,
            "provenance": _payload(provenance),
        })
        c = CompensationRecord(
            cid, return_id, disposition, learner_state_before, learner_state_after,
            tuple(affected_ids), tuple(residual_ids), tuple(future_family), provenance, closed,
        )
        self._record(
            "COMPENSATION",
            {**_payload(c), "kernel": self.KERNEL_VERSION},
            route=("COMPENSATE", "learner-state"), source=self.FOCAL_SYSTEM_ID,
        )
        if closed:
            self._record(
                "DEVELOPMENTAL_CLOSURE",
                {
                    "id": digest({"compensation": cid, "return": return_id}),
                    "kernel": self.KERNEL_VERSION,
                    "return_id": return_id,
                    "compensation_id": cid,
                    "future_family": list(future_family),
                },
                route=("return", "compensation", "changed-later-state"),
                source=self.FOCAL_SYSTEM_ID,
            )
        return c
