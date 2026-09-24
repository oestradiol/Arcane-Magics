from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Iterable

from .canonical import digest
from .model import Provenance
from .world_observer import SemanticCandidate


class LearningDisposition(str, Enum):
    ADMIT = "ADMIT"
    WITHHOLD = "WITHHOLD"
    REJECT = "REJECT"


class LearningOperation(str, Enum):
    DEFINE = "DEFINE"
    RELATE = "RELATE"
    EXEMPLIFY = "EXEMPLIFY"
    CONSTRUCTION = "CONSTRUCTION"


@dataclass(frozen=True)
class CandidateRelationalDelta:
    id: str
    candidate_id: str
    operation: LearningOperation
    namespace: str
    subject: str
    predicate: str
    object: str
    stage: str
    provenance: Provenance


@dataclass(frozen=True)
class EvidenceResolution:
    id: str
    candidate_id: str
    evidence_ids: tuple[str, ...]
    source_ids: tuple[str, ...]
    resolved: bool
    reason: str


@dataclass(frozen=True)
class LearningDecision:
    id: str
    delta_id: str
    disposition: LearningDisposition
    reason: str
    reopen_when: str | None = None


@dataclass(frozen=True)
class LearningCommit:
    id: str
    delta_id: str
    state_digest: str
    trajectory_head_before: str
    stage: str


@dataclass(frozen=True)
class StageGateReceipt:
    id: str
    stage: str
    passed: bool
    evaluator_id: str
    evidence_ids: tuple[str, ...] = ()
    provenance: Provenance = Provenance()


@dataclass
class LearnerState:
    """Non-Canonical developmental semantic state reconstructed from trajectory events.

    This state is deliberately distinct from OntogeneticVM.project_state. It may influence
    later learning/speech only through explicit adapters and governed operations.
    """

    definitions: dict[str, str]
    relations: dict[str, tuple[str, str]]
    examples: dict[str, tuple[str, str]]
    constructions: dict[str, tuple[str, str]]
    completed_items: set[str]
    stage_receipts: dict[str, str]

    @classmethod
    def empty(cls) -> "LearnerState":
        return cls({}, {}, {}, {}, set(), {})

    def snapshot(self) -> dict[str, Any]:
        return {
            "definitions": dict(sorted(self.definitions.items())),
            "relations": {k: list(v) for k, v in sorted(self.relations.items())},
            "examples": {k: list(v) for k, v in sorted(self.examples.items())},
            "constructions": {k: list(v) for k, v in sorted(self.constructions.items())},
            "completed_items": sorted(self.completed_items),
            "stage_receipts": dict(sorted(self.stage_receipts.items())),
        }

    @property
    def state_digest(self) -> str:
        return digest(self.snapshot())


@dataclass(frozen=True)
class LearnerProjection:
    trajectory_head: str
    learner_state_digest: str
    definition_count: int
    relation_count: int
    example_count: int
    construction_count: int
    completed_item_count: int
    stage_receipts: tuple[tuple[str, str], ...]
    definitions: tuple[tuple[str, str], ...]
    relations: tuple[tuple[str, tuple[str, str]], ...]
    constructions: tuple[tuple[str, tuple[str, str]], ...]


class SemanticLearningMembrane:
    """Governed candidate -> learner-state membrane for the R131 World/Observer organism.

    The membrane consumes only provenance-bound SemanticCandidate objects already present in
    the VM trajectory. It writes learner-state events, never PROJECT_STATE or Canonical state.
    Hosted language competence therefore cannot grant itself semantic authority.
    """

    VERSION = "SEMANTIC_LEARNING_MEMBRANE_R131_v0.1"

    RESERVED_NAMESPACES = ("canonical", "project_state", "authority", "root")
    PRE_N2_WITHHELD = frozenset({
        "intelligent love", "venus", "minerva", "structure", "semantics", "whole", "perspective"
    })
    STAGE_ORDER = (
        "ENGLISH_FOUNDATIONS",
        "RELATIONAL_ENGLISH",
        "PHILOSOPHY_BASICS",
        "SCIENCE_BASICS",
        "N2_HIDDEN_RECONSTRUCTION",
        "PROJECT_LANGUAGE",
    )

    def __init__(self, vm, *, trusted_evaluators=("project-manager",)):
        self.vm = vm
        self.trusted_evaluators = frozenset(str(x) for x in trusted_evaluators if str(x))
        self.state = LearnerState.empty()
        self._candidate_payloads: dict[str, dict[str, Any]] = {}
        self._committed_delta_ids: set[str] = set()
        self._replay()

    @staticmethod
    def _norm_token(s: str) -> str:
        return " ".join(str(s).strip().casefold().split())

    def _replay(self):
        for e in self.vm.journal.events:
            kind = e.get("kind")
            p = e.get("payload", {})
            if kind == "INTERPRETATION_CANDIDATES":
                for c in p.get("candidates", []):
                    if isinstance(c, dict) and c.get("id"):
                        self._candidate_payloads[c["id"]] = c
            elif kind == "LEARNER_STAGE_GATE":
                if p.get("passed"):
                    self.state.stage_receipts[p["stage"]] = p["receipt_id"]
            elif kind == "LEARNER_SEMANTIC_COMMIT":
                self._apply_serialized_delta(p["delta"])
                self._committed_delta_ids.add(p["delta"]["id"])
                item_id = p.get("curriculum_item_id")
                if item_id:
                    self.state.completed_items.add(item_id)


    def _refresh_candidate_index(self):
        for e in self.vm.journal.events:
            if e.get("kind") != "INTERPRETATION_CANDIDATES":
                continue
            for c in e.get("payload", {}).get("candidates", []):
                if isinstance(c, dict) and c.get("id"):
                    self._candidate_payloads[c["id"]] = c

    def _apply_serialized_delta(self, d: dict[str, Any]):
        op = LearningOperation(d["operation"])
        subject = d["subject"]
        predicate = d["predicate"]
        obj = d["object"]
        if op is LearningOperation.DEFINE:
            self.state.definitions[subject] = obj
        elif op is LearningOperation.RELATE:
            self.state.relations[d["id"]] = (f"{subject}::{predicate}", obj)
        elif op is LearningOperation.EXEMPLIFY:
            self.state.examples[d["id"]] = (subject, obj)
        elif op is LearningOperation.CONSTRUCTION:
            self.state.constructions[subject] = (predicate, obj)

    def _candidate_is_known_and_exact(self, c: SemanticCandidate) -> bool:
        self._refresh_candidate_index()
        p = self._candidate_payloads.get(c.id)
        if p is None:
            return False
        return (
            p.get("register") == c.register.value
            and p.get("content") == c.content
            and p.get("modality") == c.modality
            and p.get("source_ingress_id") == c.source_ingress_id
            and p.get("provenance") == asdict(c.provenance)
        )

    def project(self, *, max_entries: int = 64) -> LearnerProjection:
        if max_entries < 0:
            raise ValueError("max_entries must be >= 0")
        defs = tuple(sorted(self.state.definitions.items()))[-max_entries:] if max_entries else ()
        rels = tuple(sorted(self.state.relations.items()))[-max_entries:] if max_entries else ()
        cons = tuple(sorted(self.state.constructions.items()))[-max_entries:] if max_entries else ()
        return LearnerProjection(
            trajectory_head=self.vm.journal.head,
            learner_state_digest=self.state.state_digest,
            definition_count=len(self.state.definitions),
            relation_count=len(self.state.relations),
            example_count=len(self.state.examples),
            construction_count=len(self.state.constructions),
            completed_item_count=len(self.state.completed_items),
            stage_receipts=tuple(sorted(self.state.stage_receipts.items())),
            definitions=defs, relations=rels, constructions=cons,
        )

    def make_delta(
        self,
        candidate: SemanticCandidate,
        *,
        operation: LearningOperation,
        namespace: str,
        subject: str,
        predicate: str,
        object: str,
        stage: str,
        authoring: str = "curriculum-manager",
    ) -> CandidateRelationalDelta:
        prov = Provenance(
            sources=tuple(candidate.provenance.sources),
            parents=(candidate.id, candidate.source_ingress_id),
            exposure=tuple(candidate.provenance.exposure),
            route=("SemanticCandidate", "candidate-relational-delta", stage),
            authoring=(authoring,),
        )
        body = {
            "candidate_id": candidate.id,
            "operation": operation.value,
            "namespace": namespace,
            "subject": subject,
            "predicate": predicate,
            "object": object,
            "stage": stage,
            "provenance": asdict(prov),
        }
        return CandidateRelationalDelta(digest(body), candidate.id, operation, namespace, subject, predicate, object, stage, prov)

    def resolve_evidence(
        self,
        candidate: SemanticCandidate,
        *,
        evidence_ids: Iterable[str],
        source_ids: Iterable[str] = (),
        reason: str = "curriculum-grounded teaching item",
    ) -> EvidenceResolution:
        ev = tuple(str(x) for x in evidence_ids if str(x))
        sources = tuple(str(x) for x in source_ids if str(x)) or tuple(candidate.provenance.sources)
        resolved = bool(ev) and bool(sources) and self._candidate_is_known_and_exact(candidate)
        body = {"candidate_id": candidate.id, "evidence_ids": ev, "source_ids": sources, "resolved": resolved, "reason": reason}
        return EvidenceResolution(digest(body), candidate.id, ev, sources, resolved, reason)

    def _stage_index(self, stage: str) -> int:
        try:
            return self.STAGE_ORDER.index(stage)
        except ValueError as exc:
            raise ValueError(f"unknown curriculum stage: {stage}") from exc

    def _stage_unlocked(self, stage: str) -> bool:
        idx = self._stage_index(stage)
        if idx == 0:
            return True
        previous = self.STAGE_ORDER[idx - 1]
        return previous in self.state.stage_receipts

    def _contains_withheld_target(self, *values: str) -> bool:
        text = " ".join(self._norm_token(v) for v in values)
        return any(term in text for term in self.PRE_N2_WITHHELD)

    def adjudicate(self, delta: CandidateRelationalDelta, evidence: EvidenceResolution) -> LearningDecision:
        reason = "admitted"
        disposition = LearningDisposition.ADMIT
        reopen = None

        if delta.id in self._committed_delta_ids:
            disposition, reason = LearningDisposition.REJECT, "delta already committed"
        elif not delta.namespace.startswith("learner:"):
            disposition, reason = LearningDisposition.REJECT, "learner membrane may write only learner:* namespaces"
        elif any(delta.namespace.casefold().startswith(x) for x in self.RESERVED_NAMESPACES):
            disposition, reason = LearningDisposition.REJECT, "reserved authority namespace"
        elif not self._stage_unlocked(delta.stage):
            disposition, reason, reopen = LearningDisposition.WITHHOLD, "curriculum stage locked", "prior stage gate PASS"
        elif not evidence.resolved or evidence.candidate_id != delta.candidate_id:
            disposition, reason, reopen = LearningDisposition.WITHHOLD, "evidence/provenance unresolved", "bound evidence"
        elif delta.stage != "PROJECT_LANGUAGE" and self._contains_withheld_target(delta.subject, delta.predicate, delta.object):
            disposition, reason, reopen = LearningDisposition.WITHHOLD, "N2 mature target vocabulary withheld before project-language stage", "N2 hidden reconstruction gate PASS"
        elif not all(str(x).strip() for x in (delta.subject, delta.predicate, delta.object)):
            disposition, reason = LearningDisposition.REJECT, "empty semantic field"
        elif delta.operation is LearningOperation.DEFINE:
            prior = self.state.definitions.get(delta.subject)
            if prior is not None and prior != delta.object:
                disposition, reason, reopen = LearningDisposition.WITHHOLD, "definition conflict; preserve both until discriminator", "conflict resolution"
        elif delta.operation is LearningOperation.CONSTRUCTION:
            prior = self.state.constructions.get(delta.subject)
            if prior is not None and prior != (delta.predicate, delta.object):
                disposition, reason, reopen = LearningDisposition.WITHHOLD, "construction conflict; no silent overwrite", "conflict resolution"

        body = {"delta_id": delta.id, "disposition": disposition.value, "reason": reason, "reopen_when": reopen}
        return LearningDecision(digest(body), delta.id, disposition, reason, reopen)

    def commit(
        self,
        delta: CandidateRelationalDelta,
        evidence: EvidenceResolution,
        decision: LearningDecision,
        *,
        curriculum_item_id: str | None = None,
    ) -> LearningCommit | None:
        if decision.delta_id != delta.id:
            raise ValueError("decision/delta mismatch")
        if decision.disposition is not LearningDisposition.ADMIT:
            self.vm.record_interface_event(
                "LEARNER_SEMANTIC_WITHHOLD",
                {"delta_id": delta.id, "decision": asdict(decision), "evidence": asdict(evidence), "curriculum_item_id": curriculum_item_id},
                route=("Semantics_i", "learning-membrane", "WITHHOLD"),
                source=self.VERSION,
            )
            return None
        self._refresh_candidate_index()
        if not self._candidate_payloads.get(delta.candidate_id):
            raise ValueError("candidate is not trajectory-bound")

        before_head = self.vm.journal.head
        serialized = {
            "id": delta.id,
            "candidate_id": delta.candidate_id,
            "operation": delta.operation.value,
            "namespace": delta.namespace,
            "subject": delta.subject,
            "predicate": delta.predicate,
            "object": delta.object,
            "stage": delta.stage,
            "provenance": asdict(delta.provenance),
        }
        # Compute prospective learner state without touching Canonical project_state.
        self._apply_serialized_delta(serialized)
        if curriculum_item_id:
            self.state.completed_items.add(curriculum_item_id)
        state_digest = self.state.state_digest
        body = {
            "delta": serialized,
            "evidence": asdict(evidence),
            "decision": asdict(decision),
            "curriculum_item_id": curriculum_item_id,
            "state_digest": state_digest,
            "canonical_mutation": False,
            "project_state_mutation": False,
        }
        event = self.vm.record_interface_event(
            "LEARNER_SEMANTIC_COMMIT",
            body,
            route=("SemanticCandidate", "evidence-resolution", "learning-admissibility", "LearnerState"),
            source=self.VERSION,
        )
        self._committed_delta_ids.add(delta.id)
        return LearningCommit(digest({"delta": delta.id, "state": state_digest, "event": event["digest"]}), delta.id, state_digest, before_head, delta.stage)

    def advance_stage(self, receipt: StageGateReceipt):
        if receipt.stage not in self.STAGE_ORDER:
            raise ValueError("unknown stage")
        if receipt.id != digest({
            "stage": receipt.stage,
            "passed": receipt.passed,
            "evaluator_id": receipt.evaluator_id,
            "evidence_ids": receipt.evidence_ids,
            "provenance": asdict(receipt.provenance),
        }):
            raise ValueError("stage receipt digest mismatch")
        if not receipt.passed:
            raise ValueError("cannot unlock stage from failed receipt")
        if not self._stage_unlocked(receipt.stage):
            raise ValueError("cannot certify a stage before its prerequisite stage is unlocked")
        if not receipt.evaluator_id or receipt.evaluator_id == self.VERSION:
            raise ValueError("learner membrane cannot self-certify stage mastery")
        if receipt.evaluator_id not in self.trusted_evaluators:
            raise ValueError("untrusted curriculum evaluator")

        # The hidden N2 gate is no longer an arbitrary trusted-evaluator assertion.
        # Once R132 exists, project-language unlock must be causally downstream of the
        # conserved R132 result and the separately earned semantic-competence gate.
        if receipt.stage == "N2_HIDDEN_RECONSTRUCTION":
            state = self.vm.project_state if isinstance(self.vm.project_state, dict) else {}
            # Historical R131 fixtures are retained for regression/provenance. The stricter
            # evidence binding activates on the R132 successor that actually claims the N2
            # result and is the only current route to project-language progression.
            if state.get("through") == "R132":
                sci = state.get("science", {}) if isinstance(state.get("science", {}), dict) else {}
                status = str(sci.get("N2_FULL_CAUSAL_ACTION_CORE_R132", ""))
                if not status.startswith("CLOSED / SUPPORTED-LIMITED / MATURE-REDUCED"):
                    raise ValueError("N2 stage gate requires positive bounded R132 causal/action status")
                prov = state.get("provenance", {}) if isinstance(state.get("provenance", {}), dict) else {}
                required = (
                    str(prov.get("semantic_competence_result_sha256", "")),
                    str(prov.get("R132_N2_result_packet_sha256", "")),
                    str(prov.get("R132_N2_final_adjudication_sha256", "")),
                    str(prov.get("R132_N2_independent_reconstruction_sha256", "")),
                    str(prov.get("R132_HSTAR_prefrozen_sha256", "")),
                    str(prov.get("R132_learner_projection_prefrozen_sha256", "")),
                )
                if any(not x for x in required):
                    raise ValueError("R132 ProjectState is missing required N2/competence provenance")
                missing = [x for x in required if x not in receipt.evidence_ids]
                if missing:
                    raise ValueError("N2 stage gate is not bound to all required R132 evidence")
            elif state.get("through") != "R131":
                raise ValueError("N2 stage gate requires a conserved R131 historical fixture or current R132 ProjectState")
        self.vm.record_interface_event(
            "LEARNER_STAGE_GATE",
            {"receipt_id": receipt.id, "stage": receipt.stage, "passed": True, "evaluator_id": receipt.evaluator_id, "evidence_ids": list(receipt.evidence_ids), "provenance": asdict(receipt.provenance)},
            route=("curriculum-evaluation", "stage-gate"),
            source=receipt.evaluator_id,
        )
        self.state.stage_receipts[receipt.stage] = receipt.id


def make_stage_gate_receipt(stage: str, *, evaluator_id: str, evidence_ids: Iterable[str]) -> StageGateReceipt:
    ev = tuple(str(x) for x in evidence_ids if str(x))
    prov = Provenance(sources=ev, route=("external-evaluation", "curriculum-stage-gate"), authoring=(evaluator_id,))
    body = {"stage": stage, "passed": True, "evaluator_id": evaluator_id, "evidence_ids": ev, "provenance": asdict(prov)}
    return StageGateReceipt(digest(body), stage, True, evaluator_id, ev, prov)
