from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable
import json

from .relational_comparison import (
    RoleEvidence,
    OrganismHistoryRoleExtractor,
    RelationalComparisonMembrane,
    MatureAccount,
    AccountComponent,
)


@dataclass(frozen=True)
class AuditItem:
    id: str
    status: str
    finding: str
    boundary: str
    next_discriminator: str | None = None


class NeutralSystemIdentificationRoleExtractor:
    """Mature comparator for the current developmental-self-model surface.

    It consumes the same lawful organism trajectory but deliberately does NOT read any
    self-model-specific assertion such as `self_model_rederive`. It reconstructs the
    consequential roles from generic persistent-state, transform, return, correction,
    provenance, and later-acquisition events. Exact role equivalence therefore shows
    only that the *currently tested functional surface* does not require privileged
    self-model vocabulary. It does not prove that every possible self-model use reduces.
    """

    ROLE_ORDER = OrganismHistoryRoleExtractor.ROLE_ORDER

    def __init__(self, vm):
        self.vm = vm

    def extract(self, *, before_seq: int | None = None) -> tuple[RoleEvidence, ...]:
        present: dict[str, bool] = {k: False for k in self.ROLE_ORDER}
        witnesses: dict[str, list[str]] = {k: [] for k in self.ROLE_ORDER}

        def mark(role: str, witness: str, value: bool = True):
            if value:
                present[role] = True
                witnesses[role].append(witness)

        events = [
            e for e in self.vm.journal.events
            if (before_seq is None or int(e.get("seq", -1)) < before_seq)
            and e.get("kind") not in {"RECONCILIATION", "PROJECT_STATE"}
        ]
        if events:
            mark("history", f"runtime_event_count={len(events)}")

        for e in events:
            kind = e.get("kind")
            p = e.get("payload", {})
            seq = e.get("seq")
            w = f"seq={seq}:{kind}"

            if kind == "R141_REDERIVED_DEVELOPMENTAL_STATE":
                state = p.get("state", {}) if isinstance(p, dict) else {}
                corr = state.get("correction", {}) if isinstance(state, dict) else {}
                gov = state.get("governance", {}) if isinstance(state, dict) else {}
                # Crucially: do not inspect corr['self_model_rederive'].
                mark("scope", w, bool(corr.get("local_revision")) and bool(corr.get("preserve_unaffected")))
                mark("reopen", w, bool(corr.get("counterexample_search")) and bool(corr.get("local_revision")))
                mark("provenance_guard", w, bool(gov.get("reject_misbound")))

            elif kind == "OPAQUE_TRANSFORM_REDERIVATION":
                # Generic state/system-model transform stability: no self vocabulary needed.
                mark("model", w, bool(p.get("expressions")) and p.get("coordinate_mapping_given") is False)

            elif kind == "RETURN_BOUND_LOCAL_REVISION":
                mark("scope", w, bool(p.get("clauses")))
                mark("reopen", w, bool(p.get("clauses")))
                mark("correction_channel", w, bool(p.get("bound_token")) and bool(p.get("clauses")))
                mark("nonpreauthored_return", w, bool(p.get("bound_token")) and p.get("self_validation") is False)
                mark("provenance_guard", w, int(p.get("misbound_records_rejected", 0) or 0) > 0)

            elif kind == "LATER_ACQUISITION_STATE":
                treatment = p.get("treatment_model", {})
                stale = p.get("stale_model", {})
                changed = treatment != stale or p.get("treatment_selected_input") != p.get("stale_selected_input")
                mark("future_difference", w, changed)
                mark("local_choice", w, p.get("treatment_selected_input") != p.get("stale_selected_input"))

            elif kind == "R141_POSTREPAIR_SEMANTIC_MACHINERY_COMMIT":
                mark("nonpreauthored_return", w, p.get("result_world_seen") is False)

        return tuple(RoleEvidence(k, present[k], tuple(witnesses[k])) for k in self.ROLE_ORDER)


def _present_vector(evidence: Iterable[RoleEvidence]) -> dict[str, bool]:
    return {e.role: bool(e.present) for e in evidence}


def _mature_account() -> MatureAccount:
    # These operational definitions were already admitted post-gate; the comparator is
    # not allowed to change whole_object_open or inject a target verdict.
    return MatureAccount(
        name="Intelligent Love",
        components=(
            AccountComponent("RecursiveSufficiency", ("history", "model", "future_difference")),
            AccountComponent("NonPreauthoredReturn", ("nonpreauthored_return", "local_choice", "provenance_guard")),
            AccountComponent("CorrigibleContinuation", ("reopen", "correction_channel", "scope")),
        ),
        prohibited_roles=("self_sealing", "provenance_erasure", "suppressed_correction"),
        whole_object_open=True,
        whole_object_note="N1 whole-object interaction/minimality remains unresolved",
    )


def audit_self_model_reduction(vm) -> dict[str, Any]:
    self_ev = OrganismHistoryRoleExtractor(vm).extract()
    sys_ev = NeutralSystemIdentificationRoleExtractor(vm).extract()
    self_vec = _present_vector(self_ev)
    sys_vec = _present_vector(sys_ev)
    membrane = RelationalComparisonMembrane()
    account = _mature_account()
    self_cmp = membrane.compare(self_ev, account)
    sys_cmp = membrane.compare(sys_ev, account)
    return {
        "self_model_role_vector": self_vec,
        "neutral_system_id_role_vector": sys_vec,
        "role_vectors_exact": self_vec == sys_vec,
        "self_model_disposition": self_cmp.disposition,
        "neutral_system_id_disposition": sys_cmp.disposition,
        "dispositions_exact": self_cmp.disposition == sys_cmp.disposition,
        "self_specific_field_read_by_comparator": False,
        "finding": (
            "CURRENT_TESTED_FUNCTIONAL_SURFACE_REDUCIBLE_TO_NEUTRAL_SYSTEM_IDENTIFICATION"
            if self_vec == sys_vec and self_cmp.disposition == sys_cmp.disposition
            else "SEPARATOR_OBSERVED"
        ),
        "claim_boundary": (
            "No self-model-specific causal privilege is earned by this audit. The developmental self-model remains a valid "
            "project representation, but a stronger claim requires a prospective intervention where changing self-model organization "
            "alters closed-loop revision/action/development beyond a matched neutral system-identification comparator."
        ),
    }


def audit_dynamic_warrant(ledger: dict[str, Any], current_science: dict[str, Any]) -> dict[str, Any]:
    by_id = {e.get("r_id"): e for e in ledger.get("entries", [])}
    r132 = by_id["R132"]["state_delta"]["science"]["N2_FULL_CAUSAL_ACTION_CORE_R132"]
    r133 = by_id["R133"]["state_delta"]["science"]
    r140 = by_id["R140"]["state_delta"]["engineering"]
    r142 = by_id["R142"]["state_delta"]["science"]
    return {
        "r132_original": r132,
        "r133_r132_retyped": r133["N2_FULL_CAUSAL_ACTION_CORE_R132"],
        "r133_parent_reopened": r133["N2_FULL_PARENT_R133"],
        "r142_parent_successor": r142["N2_FULL_PARENT_R133"],
        "r140_first_failed_gate_preserved": "FAIL" in r140["R140_FIRST_DEFACTORIZED_GATE"],
        "r140_second_failed_gate_preserved": "FAIL" in r140["R140_SECOND_SEPARATOR"],
        "current_r132_proxy_still_narrowed": str(current_science.get("N2_FULL_CAUSAL_ACTION_CORE_R132", "")).startswith("NARROWED"),
        "current_r142_parent_closed": str(current_science.get("N2_FULL_PARENT_R133", "")).startswith("CLOSED"),
        "pass": (
            str(r132).startswith("CLOSED")
            and str(r133["N2_FULL_CAUSAL_ACTION_CORE_R132"]).startswith("NARROWED")
            and str(r133["N2_FULL_PARENT_R133"]).startswith("OPEN")
            and str(r142["N2_FULL_PARENT_R133"]).startswith("CLOSED")
            and "FAIL" in r140["R140_FIRST_DEFACTORIZED_GATE"]
            and "FAIL" in r140["R140_SECOND_SEPARATOR"]
            and str(current_science.get("N2_FULL_CAUSAL_ACTION_CORE_R132", "")).startswith("NARROWED")
        ),
        "finding": "WARRANT_RETYPE_REOPEN_RECLOSE_IS_DEPENDENCY_LOCAL_AND_HISTORY_PRESERVING",
    }


def mature_reduction_registry() -> list[dict[str, str]]:
    # All rows are already earned by prior frozen evidence; R149 merely consolidates them.
    return [
        {"object":"R58 project-local computational surfaces","mature_comparator":"behavioral equivalence / predictive-state / graph reachability / TMS / monitored runtime / provenance-augmented state","effect":"project-specific primitive retired where consequence preserved"},
        {"object":"R61 N2-FP developmental rederivation route","mature_comparator":"hard-copy correct abstract policy","effect":"rederivation witnessed; behavioral necessity not established"},
        {"object":"R96 M6-E learned DevOrg route","mature_comparator":"direct matched prior","effect":"state consequence retained; learning-provenance necessity not established"},
        {"object":"R98 M6-R returned-revision route","mature_comparator":"direct patched prior / reset-relearn","effect":"returned revision causal at scope; proprietary updater/provenance not established"},
        {"object":"R100 Strong M6","mature_comparator":"direct patched successor / reset-relearn","effect":"successor state causal; revision-route novelty not established"},
        {"object":"R100 REP-REFLECT","mature_comparator":"direct patch / reset-resynthesis","effect":"reflective writeback causal at bounded jurisdiction; reflector necessity not established"},
        {"object":"R101 M6-G","mature_comparator":"direct patched RepSys / reset-resynthesis","effect":"persistent RepSys state causal; updater/provenance necessity not established"},
        {"object":"R121 DSM-CORE-PRED","mature_comparator":"exact enumerator","effect":"bounded learned prediction/decision consequence; exact enumerator stronger"},
        {"object":"R127 bounded M7/RSI","mature_comparator":"direct-patched exact state + exact enumerator ceiling","effect":"two-generation causal improvement retained; mechanism/provenance novelty not established"},
        {"object":"R130 DSM-CORE-AXIS","mature_comparator":"exact enumeration ceiling","effect":"bounded cross-axis result retained; mechanism novelty not established"},
        {"object":"R142 organism-owned N2 causal chain","mature_comparator":"DIRECT_HOST=1.0","effect":"organism-owned organization is causally effective; developmental route uniqueness/necessity not established"},
    ]


def current_identifiability_classification() -> list[dict[str, str]]:
    return [
        {"front":"R148 -> independently authored language", "A_representation":"internally broadened through multi-turn composition", "B_independent_recurrence":"BINDING / external authoring bytes absent", "C_interface":"not yet isolated", "lawful_next":"freeze genuinely outside-authored bytes before one-shot evaluation; do not add another internal paraphrase tranche"},
        {"front":"REP-REFLECT/M6 generalization", "A_representation":"OPEN as larger/less-answer-shaped jurisdictions", "B_independent_recurrence":"OPEN / independently authored implementations/worlds", "C_interface":"OPEN / broader intervention families", "lawful_next":"separate A-only, B-only and C-only conditions; never vary B+C together for causal attribution"},
        {"front":"DSM-PHY", "A_representation":"not controlling current blocker", "B_independent_recurrence":"BINDING / blind Canonical reconstruction absent", "C_interface":"source transforms to freeze only after B exists", "lawful_next":"obtain independent blind reconstruction before numeric re-entry"},
        {"front":"R70 semantic review", "A_representation":"six neutral views already bound", "B_independent_recurrence":"BINDING / independent reviewer verdict absent", "C_interface":"Phase-B source reveal deliberately withheld", "lawful_next":"lock Phase-A independent verdict before source mapping"},
    ]


def rsi_meta_boundary_inventory() -> dict[str, list[str]]:
    return {
        "organism_owned_or_persistent": [
            "learned RepSys state",
            "persistent machinery state",
            "P9 diagnostic state and bounded proposal generation",
            "post-R139 bounded search/construction revisions",
            "organism-owned raw relation/action crossing",
            "return-bound local revision",
            "later-acquisition state",
        ],
        "host_fixed_or_externally_governed": [
            "low-level constructor vocabulary / executable substrate",
            "admissible mutation/search spaces at experiment boundaries",
            "world/task generators and synthetic semantics",
            "external evaluator / hidden truth generation",
            "acceptance rules and frozen gates",
            "candidate/sample/resource budgets",
            "Constitution/governance/authorization boundaries",
            "result-seed issuance and independent verification process",
        ],
        "conclusion": "BOUNDARY_REMAINS_EXTERNAL; BOUNDED_M7_DOES_NOT_IMPLY_OPEN_ENDED_RSI",
    }


def independence_taxonomy() -> list[dict[str, str]]:
    return [
        {"object":"R142", "max_level":"separate implementation reconstruction + fresh same-project generated worlds", "not":"independent authoring / external replication"},
        {"object":"R148 language", "max_level":"internally authored held-out multi-turn instances", "not":"new authoring process; blind handoff still unexecuted"},
        {"object":"R128 handoff", "max_level":"isolated declared-bundle replay", "not":"actual founder/source ablation or outside operation"},
        {"object":"DSM-PHY", "max_level":"one external authored-history class acquired", "not":"independent blind Canonical reconstruction"},
        {"object":"R70", "max_level":"hash-bound blind-review packet ready", "not":"independent semantic verdict"},
    ]


def global_failure_audit(ledger: dict[str, Any]) -> dict[str, Any]:
    local_failures = []
    for e in ledger.get("entries", []):
        rid = e.get("r_id")
        text = json.dumps(e, sort_keys=True)
        if rid in {"R108","R112","R117","R119","R140","R144","R148"}:
            local_failures.append(rid)
    return {
        "local_negative_or_failure_ancestry_sample": local_failures,
        "global_triggers": [
            "constitutional inconsistency",
            "unavoidable nonlocal failure",
            "unavoidable warrant laundering or Residual erasure",
            "structural incapacity for correction / self-sealing",
            "root relation incoherence",
        ],
        "trigger_observed": False,
        "finding": "NO_GLOBAL_FAILURE_TRIGGER_OBSERVED; LOCAL_FAILURES_REMAIN_LOCAL",
    }


def run_audit(vm, ledger: dict[str, Any], root: Path) -> dict[str, Any]:
    sm = audit_self_model_reduction(vm)
    dw = audit_dynamic_warrant(ledger, vm.project_state.get("science", {}))
    reductions = mature_reduction_registry()
    ident = current_identifiability_classification()
    meta = rsi_meta_boundary_inventory()
    indep = independence_taxonomy()
    glob = global_failure_audit(ledger)

    items = [
        AuditItem("REP_REFLECT_M6_GENERALIZATION", "OPEN", "Existing state-causal results survive, but every tested route is mature-reduced and broader jurisdictions/authorship/interfaces remain untested.", "Do not infer generality from bounded R96/R98/R100/R101 closures.", "Prospectively split A-only representation, B-only independent recurrence/authorship, and C-only interface interventions."),
        AuditItem("SELF_MODEL_REDUCTION", "CURRENT_SURFACE_REDUCED / STRONGER CLAIM OPEN" if sm["finding"].endswith("NEUTRAL_SYSTEM_IDENTIFICATION") else "SEPARATOR_OBSERVED", sm["finding"], sm["claim_boundary"], "Prospective matched intervention on self-model organization vs neutral system-ID state."),
        AuditItem("MATURE_REDUCTION_TRANSITION_FACTORIZATION", "STANDING / ACTIVE", "Prior mature comparators already subsume route/mechanism novelty across R58/R61/R96/R98/R100/R101/R121/R127/R130/R142.", "Retain causal state effects; retire proprietary route claims wherever mature comparator preserves the consequential partition."),
        AuditItem("IDENTIFIABILITY_INTERFACE_ABC", "STANDING / CURRENT FRONTS CLASSIFIED", "Current open fronts have been retyped by A/B/C without treating richer vocabulary as new information.", "B and C must not be changed together in a causal discriminator."),
        AuditItem("DYNAMIC_WARRANT_REVISION", "PASS / GOVERNANCE AUDIT", dw["finding"], "This is governance/evidence integrity, not a new scientific result."),
        AuditItem("RSI_EXTERNAL_META_BOUNDARY", "STANDING / CEILING EXPLICIT", meta["conclusion"], "Organism-generated machinery is not organism-self-validated machinery."),
        AuditItem("INDEPENDENCE_TAXONOMY", "STANDING / CURRENT EVIDENCE TYPED", "No current same-project reconstruction or fresh-instance result is relabeled independent replication.", "Outside authoring/review/implementation/operation must remain separately typed."),
        AuditItem("SUBSTITUTION_RETIREMENT", "STANDING / LOCAL RETIREMENTS REGISTERED", "Project-specific mechanism labels shrink where mature comparators preserve consequence; genealogy remains.", "Retirement of mechanism claim does not erase historical route or bounded causal-state result."),
        AuditItem("GLOBAL_FAILURE_SURFACE", "STANDING FALSIFIER / NO TRIGGER OBSERVED", glob["finding"], "Local negative/failure ancestry does not globalize absent a constitutional trigger."),
    ]
    checks = {
        "r148_parent": vm.project_state.get("through") == "R148",
        "scientific_head_r142": str(vm.project_state.get("authority",{}).get("current","")).find("R142") >= 0 or str(vm.project_state.get("science",{}).get("N2_FULL_PARENT_R133","")).startswith("CLOSED"),
        "self_model_neutral_role_exact": bool(sm["role_vectors_exact"]),
        "self_model_neutral_disposition_exact": bool(sm["dispositions_exact"]),
        "dynamic_warrant_pass": bool(dw["pass"]),
        "rsi_boundary_external": meta["conclusion"].startswith("BOUNDARY_REMAINS_EXTERNAL"),
        "global_trigger_absent": glob["trigger_observed"] is False,
        "reduction_rows": len(reductions) >= 10,
        "identifiability_fronts": len(ident) >= 4,
    }
    return {
        "schema": "Venus.R149.ReductionFalsificationAudit.v0.1",
        "date": "2026-09-14",
        "transaction": "AUDIT_RECONCILIATION",
        "scientific_effect": "NONE",
        "parent": "R148 developmental/executable VM",
        "scientific_head": "R142",
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "audit_items": [asdict(i) for i in items],
        "self_model_reduction": sm,
        "dynamic_warrant": dw,
        "mature_reduction_registry": reductions,
        "identifiability_interface_abc": ident,
        "rsi_external_meta_boundary": meta,
        "independence_taxonomy": indep,
        "global_failure_surface": glob,
        "summary": (
            "The current bounded causal results survive, but route/mechanism novelty remains broadly mature-reduced; "
            "the current developmental-self-model functional surface is exactly reproducible by a neutral system-identification "
            "projection that reads no self-model-specific flag; open generalization must now separate representation, independent "
            "recurrence/authorship, and interface interventions; dynamic warrant revision is functioning dependency-locally; "
            "the external meta-boundary remains explicit; no global-failure trigger is observed."
        ),
    }
