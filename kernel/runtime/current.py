from __future__ import annotations

"""Hydrate the admitted WorldMirror/VMK2 runtime from persisted state.

This module is the persistence boundary between files on disk and the live
``VMK2Reference`` object. It reconstructs the hot/cold JSON snapshot, verifies
payload hashes and state roots, and refuses silent state drift.

It is not developmental cognition and does not decide what the learner should
work on. See ``docs/WORLDMIRROR_VM.md``.
"""

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from .vmk2 import (
    EvidenceReceipt, ExecutionReceipt, IngressEvent, JurisdictionReceipt,
    LegitimacyReceipt, PolicyMode, ProjectionReceipt, ReceiptStatus,
    ReopeningReceipt, ReturnRole, StateObject, StateTransitionReceipt,
    TransitionPolicy, TurnLease, VerifiedReturn, VMK2Reference, digest,
)

KERNEL_DIR = Path(__file__).resolve().parents[1]
STATE_DIR = KERNEL_DIR / "state"
HOT_CHECKPOINT = STATE_DIR / "IG10_HOT_CHECKPOINT.json"
COLD_DIR = STATE_DIR / "cold"

EXPECTED_SOURCE_SNAPSHOT_SHA256 = "ceafc691d14f329785e206d32328290abbb74ee279224ec16884aff1f630acc5"
EXPECTED_IG10_ROOT = "a84ec144537967aff0c34b81ac3e6eafabc2450bb31e29d05284526b795c7228"


def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _snapshot_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _payload_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def reconstruct_snapshot() -> dict[str, Any]:
    envelope = _json(HOT_CHECKPOINT)
    if envelope.get("schema") != "Venus.HotCheckpoint.v1":
        raise ValueError("unknown hot-checkpoint schema")

    snapshot = envelope["hot_snapshot"]
    cold = []
    for desc in envelope["cold_state"]:
        payload = _json(COLD_DIR / desc["file"])
        if sha256(_payload_bytes(payload)).hexdigest() != desc["payload_sha256"]:
            raise ValueError(f"cold payload digest mismatch: {desc['object_id']}")
        if digest({"id": desc["object_id"], "value": payload}) != desc["root"]:
            raise ValueError(f"cold state root mismatch: {desc['object_id']}")
        cold.append((
            int(desc["position"]),
            {
                "object_id": desc["object_id"],
                "value": payload,
                "root": desc["root"],
                "dependencies": desc["dependencies"],
            },
        ))

    for position, state_obj in sorted(cold):
        snapshot["state"].insert(position, state_obj)

    actual = sha256(_snapshot_bytes(snapshot)).hexdigest()
    if actual != envelope["source_snapshot_sha256"] or actual != EXPECTED_SOURCE_SNAPSHOT_SHA256:
        raise ValueError("reconstructed snapshot digest mismatch")
    return snapshot


def hydrate(snapshot: dict[str, Any]) -> VMK2Reference:
    if snapshot.get("kernel_version") != VMK2Reference.KERNEL_VERSION:
        raise ValueError("kernel-version mismatch")

    vm = VMK2Reference()
    vm.evidence = {
        x["evidence_id"]: EvidenceReceipt(
            x["evidence_id"], x["source_id"], x["assessor_id"],
            x["payload_digest"], int(x["exposure_epoch"]),
            tuple(x.get("provenance_ids", ())), bool(x.get("immutable", True)),
        ) for x in snapshot["evidence"]
    }
    vm.execution_receipts = {
        x["receipt_id"]: ExecutionReceipt(
            x["receipt_id"], x["action_id"], x["target_id"],
            x["effect_digest"], int(x["epoch"]),
        ) for x in snapshot["execution_receipts"]
    }
    vm.ingress = {
        x["event_id"]: IngressEvent(
            x["event_id"], x["evidence_id"], x["source_id"], x["target_id"],
            ReturnRole(x["role"]), int(x["epoch"]), x["nonce"],
            x.get("receipt_id"), x.get("interface_id", "default"),
            x.get("jurisdiction_id", "default"),
        ) for x in snapshot["ingress"]
    }
    vm.returns = {
        x["return_id"]: VerifiedReturn(
            x["return_id"], x["ingress_event_id"], x["evidence_id"],
            x["source_id"], x["target_id"], ReturnRole(x["role"]),
            int(x["epoch"]), x["nonce"], x.get("receipt_id"), x["jurisdiction_id"],
        ) for x in snapshot["returns"]
    }
    vm.jurisdictions = {
        x["receipt_id"]: JurisdictionReceipt(
            x["receipt_id"], x["jurisdiction_id"], x["actor_id"],
            frozenset(x["target_ids"]),
            frozenset(PolicyMode(v) for v in x["allowed_modes"]),
            int(x["valid_from_epoch"]), int(x["valid_until_epoch"]),
            ReceiptStatus(x["status"]),
        ) for x in snapshot["jurisdictions"]
    }
    vm.legitimacy = {
        x["receipt_id"]: LegitimacyReceipt(
            x["receipt_id"], x["actor_id"], x["target_id"], x["check_name"],
            ReceiptStatus(x["status"]), int(x["valid_from_epoch"]),
            int(x["valid_until_epoch"]), bool(x.get("withdrawn", False)),
        ) for x in snapshot["legitimacy"]
    }
    vm.turn_leases = {
        x["lease_id"]: TurnLease(
            x["lease_id"], x["owner_id"], int(x["start_epoch"]),
            int(x["end_epoch"]), x.get("contamination_epoch"),
        ) for x in snapshot["turn_leases"]
    }
    vm.policies = {
        x["policy_id"]: TransitionPolicy(
            x["policy_id"], x["actor_id"], x["target_id"],
            PolicyMode(x["mode"]), x["jurisdiction_receipt_id"],
            tuple(x.get("legitimacy_receipt_ids", ())),
            x.get("required_turn_owner"),
        ) for x in snapshot["policies"]
    }

    for x in snapshot["state"]:
        root = digest({"id": x["object_id"], "value": x["value"]})
        if root != x["root"]:
            raise ValueError(f"state root mismatch: {x['object_id']}")
        vm.state[x["object_id"]] = StateObject(
            x["object_id"], x["value"], x["root"],
            frozenset(x.get("dependencies", ())),
        )

    vm.transitions = {
        x["transition_id"]: StateTransitionReceipt(
            x["transition_id"], x["verified_return_id"], x["policy_id"],
            x["target_id"], x["before_root"], x["after_root"],
            frozenset(x["dependency_closure"]),
            dict(x["sibling_roots_before"]), dict(x["sibling_roots_after"]),
            int(x["epoch"]),
        ) for x in snapshot["transitions"]
    }
    vm.projections = {
        x["projection_id"]: ProjectionReceipt(
            x["projection_id"], frozenset(x["future_family"]),
            tuple(x["evidence_ids"]), x["payload_digest"],
        ) for x in snapshot["projections"]
    }
    vm.reopenings = {
        x["reopening_id"]: ReopeningReceipt(
            x["reopening_id"], x["projection_id"],
            frozenset(x["prior_future_family"]),
            frozenset(x["expanded_future_family"]),
            x["separator_evidence_id"], x["separator_digest"], int(x["epoch"]),
        ) for x in snapshot["reopenings"]
    }
    vm.consumed_nonces = set(snapshot["consumed_nonces"])
    vm.exposure_log = [tuple(row) for row in snapshot["exposure_log"]]

    ig10 = vm.state.get("ig10:model-specific-F")
    if ig10 is None or ig10.root != EXPECTED_IG10_ROOT:
        raise ValueError("IG10 current-state root mismatch")
    return vm


def load_current_kernel() -> VMK2Reference:
    return hydrate(reconstruct_snapshot())


def current_summary(vm: VMK2Reference | None = None) -> dict[str, Any]:
    vm = vm or load_current_kernel()
    value = vm.state["ig10:model-specific-F"].value
    return {
        "schema": "Venus.CurrentKernelSummary.v1",
        "runtime_checkpoint": "IG10",
        "kernel_version": vm.KERNEL_VERSION,
        "state_objects": len(vm.state),
        "verified_returns": len(vm.returns),
        "transitions": len(vm.transitions),
        "state_root": vm.state["ig10:model-specific-F"].root,
        "verdict": "PASS_MODEL_SPECIFIC_PHYSICAL_F_WITNESS",
        "scheduler": value["routing"]["scheduler"],
        "ready_queue": value["routing"]["ready_queue"],
        "reentry_conditions": value["routing"]["reentry_conditions"],
    }


def main() -> int:
    print(json.dumps(current_summary(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
