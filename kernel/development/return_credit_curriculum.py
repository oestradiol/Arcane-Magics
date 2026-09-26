from __future__ import annotations

"""Bounded learner-side compiler/evaluator for the return-credit curriculum.

The teacher surface supplies labeled observations and interventions, not a
credit algorithm.  Candidate semantics are induced with generic runtime
machinery:
- a decision tree learns which returned events are admissible evidence;
- a minimal equality key is searched from pairwise same/different-context
  examples;
- duplicate handling is selected from the smallest declared Boolean family.

The resulting candidate is state data.  This module is developmental scaffold,
not an Internalizer claim or independent evaluator.
"""

from copy import deepcopy
from itertools import product
import json
from pathlib import Path
from typing import Any, Mapping

from kernel.runtime.contextual_evidence import (
    apply_evidence_program,
    induce_minimal_context_key,
)
from kernel.runtime.induced_policy import (
    LabeledExample,
    execute_tree,
    induce_exact_tree,
)
from kernel.runtime.vmk2 import digest


class ReturnCreditCurriculumError(ValueError):
    pass


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _dedup_choice(rows) -> bool:
    winners = []
    for enabled in (False, True):
        ok = True
        for row in rows:
            ids = tuple(str(x) for x in row["evidence_ids"])
            observed = len(set(ids)) if enabled else len(ids)
            if observed != int(row["expected_unique_evidence_count"]):
                ok = False
                break
        if ok:
            winners.append(enabled)
    if len(winners) != 1:
        raise ReturnCreditCurriculumError(
            f"dedup policy not uniquely induced: {winners}"
        )
    return winners[0]


def induce_candidate(cases: Mapping[str, Any]) -> dict[str, Any]:
    examples = tuple(
        LabeledExample(
            example_id=str(row["id"]),
            features={str(k): bool(v) for k, v in row["features"].items()},
            decision=str(row["decision"]),
        )
        for row in cases["admission_training"]
    )
    admission = induce_exact_tree(examples)
    key = induce_minimal_context_key(
        candidate_fields=tuple(cases["context_candidate_fields"]),
        pair_examples=tuple(cases["context_pair_training"]),
    )
    if key["status"] != "UNIQUE_MINIMAL_CONTEXT_KEY":
        raise ReturnCreditCurriculumError(key["status"])

    program = {
        "schema": "Venus.ContextualEvidenceProgram.v0.1",
        "admission_policy": admission,
        "key_fields": list(key["key_fields"]),
        "deduplicate_evidence_ids": _dedup_choice(cases["dedup_training"]),
        "evidence_id_field": "return_id",
        "feature_field": "features",
        "sign_field": "sign",
        "admitted_decision": "ADMIT",
    }
    body = {
        "schema": "Venus.ReturnCreditCandidateState.v0.1",
        "status": "LEARNER_INDUCED_BOUNDED_CANDIDATE",
        "program": program,
        "training_case_ids": sorted(
            [str(x["id"]) for x in cases["admission_training"]]
            + [str(x["id"]) for x in cases["context_pair_training"]]
            + [str(x["id"]) for x in cases["dedup_training"]]
        ),
        "semantics_owner": "LEARNER_STATE_CANDIDATE",
        "generic_executor": "kernel/runtime/contextual_evidence.py",
        "generic_inducer": "kernel/runtime/induced_policy.py",
        "independent_evaluation": False,
        "internalization_claim": False,
        "promotion_authority": False,
        "truth_authority": False,
    }
    return {**body, "candidate_id": digest(body)}


def _admission_semantics(candidate: Mapping[str, Any]) -> tuple[str, ...]:
    policy = candidate["program"]["admission_policy"]
    names = tuple(policy["feature_names"])
    out = []
    for values in product((False, True), repeat=len(names)):
        features = dict(zip(names, values))
        out.append(execute_tree(policy, features))
    return tuple(out)


def _rename_values(cases: Mapping[str, Any]) -> dict[str, Any]:
    obj = deepcopy(dict(cases))
    mapping = {
        "c0": "K7", "c1": "K8", "c2": "K9",
        "t0": "W4", "t1": "W5", "t2": "W6", "t3": "W7", "t9": "W9",
        "e0": "J1", "e1": "J2", "e7": "J8",
    }
    for row in obj["context_pair_training"]:
        for side in ("left", "right"):
            for key, value in list(row[side].items()):
                row[side][key] = mapping.get(str(value), value)
    return obj


def evaluate(
    *,
    prefreeze: Mapping[str, Any],
    cases: Mapping[str, Any],
    candidate: Mapping[str, Any],
) -> dict[str, Any]:
    if prefreeze.get("schema") != "Venus.ReturnCreditAssignmentPrefreeze.v0.1":
        raise ReturnCreditCurriculumError("unsupported return-credit prefreeze")
    if cases.get("schema") != "Venus.ReturnCreditDidacticCases.v0.1":
        raise ReturnCreditCurriculumError("unsupported return-credit cases")

    reordered = deepcopy(dict(cases))
    reordered["admission_training"] = list(reversed(reordered["admission_training"]))
    reordered["context_pair_training"] = list(reversed(reordered["context_pair_training"]))
    reordered["dedup_training"] = list(reversed(reordered["dedup_training"]))
    reorder_candidate = induce_candidate(reordered)

    renamed_candidate = induce_candidate(_rename_values(cases))
    base_semantics = _admission_semantics(candidate)
    b1_checks = {
        "training_order_invariant": (
            base_semantics == _admission_semantics(reorder_candidate)
            and candidate["program"]["key_fields"] == reorder_candidate["program"]["key_fields"]
            and candidate["program"]["deduplicate_evidence_ids"]
            == reorder_candidate["program"]["deduplicate_evidence_ids"]
        ),
        "opaque_value_renaming_invariant": (
            base_semantics == _admission_semantics(renamed_candidate)
            and candidate["program"]["key_fields"] == renamed_candidate["program"]["key_fields"]
        ),
    }

    policy = candidate["program"]["admission_policy"]
    valid = {
        "authorized": True,
        "candidate_origin_match": True,
        "episode_origin_match": True,
    }
    wrong_origin = dict(valid)
    wrong_origin["candidate_origin_match"] = False
    b1_checks["origin_sensitive"] = (
        execute_tree(policy, valid) != execute_tree(policy, wrong_origin)
        and execute_tree(policy, valid) == "ADMIT"
    )

    delayed_a = {
        "return_id": "delay-a",
        "candidate_id": "cD",
        "target_id": "tD",
        "episode_id": "e0",
        "current_target_id": "tD",
        "sign": "POS",
        "features": valid,
    }
    delayed_b = {**delayed_a, "return_id": "delay-b", "current_target_id": "tOTHER"}
    delayed_out = apply_evidence_program(candidate["program"], (delayed_a, delayed_b))
    b1_checks["current_target_is_not_credit_origin"] = (
        list(delayed_out["buckets"]) == ["cD|tD"]
        and delayed_out["buckets"]["cD|tD"]["POS"] == 2
    )

    returned = apply_evidence_program(candidate["program"], cases["b2_events"])
    b2_checks = {
        "full_ledger_matches_prefrozen_consequence": (
            returned["buckets"] == dict(cases["expected_b2_buckets"])
        )
    }

    removal_id = str(cases["counterfactual_remove_return_id"])
    ablated_events = tuple(
        row for row in cases["b2_events"]
        if str(row["return_id"]) != removal_id
    )
    ablated = apply_evidence_program(candidate["program"], ablated_events)
    b2_checks["counterfactual_matches"] = (
        ablated["buckets"] == dict(cases["expected_counterfactual_buckets"])
    )

    changed = {
        key
        for key in set(returned["buckets"]) | set(ablated["buckets"])
        if returned["buckets"].get(key) != ablated["buckets"].get(key)
    }
    b2_checks["counterfactual_locality"] = changed == {"cA|tX"}
    b2_checks["duplicate_not_new_evidence"] = any(
        row["decision"] == "IGNORE_DUPLICATE"
        for row in returned["decisions"]
    )
    b2_checks["wrong_origin_not_credited"] = any(
        row["evidence_id"] == "r5" and row["decision"] == "IGNORE"
        for row in returned["decisions"]
    )
    b2_checks["contradictory_contexts_remain_visible"] = (
        returned["buckets"]["cA|tX"] == {"NEG": 1, "POS": 2}
        and returned["buckets"]["cA|tY"] == {"NEG": 1}
    )

    b1_pass = all(b1_checks.values())
    b2_pass = b1_pass and all(b2_checks.values())
    return {
        "schema": "Venus.ReturnCreditCurriculumResult.v0.1",
        "status": (
            "PASS_BOUNDED_RETURN_CREDIT_B1_B2"
            if b2_pass
            else "WITHHOLD_RETURN_CREDIT_DISCRIMINATOR_NOT_MET"
        ),
        "candidate_id": candidate["candidate_id"],
        "b1_checks": b1_checks,
        "b1_pass": b1_pass,
        "b2_checks": b2_checks,
        "b2_pass": b2_pass,
        "returned_ledger": returned["buckets"],
        "counterfactual_ledger": ablated["buckets"],
        "selected_key_fields": list(candidate["program"]["key_fields"]),
        "deduplicate_evidence_ids": candidate["program"]["deduplicate_evidence_ids"],
        "independent_evaluation": False,
        "internalization_claim": False,
        "promotion_authority": False,
        "truth_authority": False,
        "next_residual": (
            "FRESH_TRANSFER_RESTART_DELAYED_REUSE_AND_INDEPENDENT_EVALUATION"
            if b2_pass
            else "REVISE_CANDIDATE_REPRESENTATION"
        ),
        "claim_fence": (
            "A pass establishes only bounded induced causal-credit behavior on "
            "the prefrozen didactic/intervention family. It does not establish "
            "general causal attribution, truth, B3 internalization, RSI, or promotion."
        ),
    }


def run(prefreeze_path: str | Path, cases_path: str | Path) -> tuple[dict[str, Any], dict[str, Any]]:
    prefreeze = load_json(prefreeze_path)
    cases = load_json(cases_path)
    candidate = induce_candidate(cases)
    result = evaluate(prefreeze=prefreeze, cases=cases, candidate=candidate)
    return candidate, result
