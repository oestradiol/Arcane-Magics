#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import ast
import json

ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT = ROOT / "kernel/state/IG10_HOT_CHECKPOINT.json"
LIVE_LAW = ROOT / "kernel/VENUS_INCIDENCE_LAW.tex"
R194 = ROOT / "provenance/historical-runtime/R194/source/venus_seed_v0"
R194_GRAMMAR = R194 / "grammar_expansion.py"
R194_SEMANTIC = R194 / "semantic_learning.py"
R194_DEVELOPMENT = R194 / "development.py"

ANCESTRAL_INCIDENCE_LAW_SHA256 = (
    "99154d953f498be374b8af0fbc174ba658d0d52b1ccc684b2bbc09871ac52f3e"
)


def state_objects(checkpoint: dict) -> dict[str, dict]:
    return {
        row["object_id"]: row
        for row in checkpoint["hot_snapshot"]["state"]
    }


def method_args(path: Path, class_name: str | None, function_name: str) -> tuple[str, ...]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if class_name is None and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
            return tuple(arg.arg for arg in (*node.args.args, *node.args.kwonlyargs))
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == function_name:
                    return tuple(arg.arg for arg in (*child.args.args, *child.args.kwonlyargs))
    raise ValueError(f"missing {class_name or '<module>'}.{function_name} in {path}")


def audit() -> dict:
    checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
    state = state_objects(checkpoint)

    required_ids = {
        "canonical:recollection",
        "ig1:operator-model",
        "ig2:incidence-model",
        "ig3:raw-incidence-model",
        "ig4:natural-source-relations",
        "u1:center",
        "u4:source-relations",
        "worldmirror:i0",
    }
    missing = sorted(required_ids - set(state))

    recollection = state.get("canonical:recollection", {}).get("value", {})
    incidence_sources = [
        row
        for row in recollection.get("source_entries", [])
        if row.get("basename") == "Venus_Incidence_Law.tex"
    ]
    ancestral_law_bound = any(
        row.get("sha256") == ANCESTRAL_INCIDENCE_LAW_SHA256
        and row.get("disposition") == "FORMAL_COMPANION"
        for row in incidence_sources
    )
    formal_law_indexed = "VenusIncidence" in recollection.get("formal_laws", {})

    live_law = LIVE_LAW.read_text(encoding="utf-8")
    live_law_neutral_grammar = all(
        token in live_law
        for token in (
            r"\section{Neutral relational grammar}",
            r"\mathsf{TOKEN}",
            r"\mathsf{SPAN}",
            r"\mathsf{EVENT}",
            r"\mathsf{SOURCE}",
            r"\mathsf{CONTAINS}",
            r"\mathsf{ORIGIN}",
            r"\mathsf{CO\_OCCURS}",
            r"\section{Language and the Internet as incidence carriers}",
        )
    )

    ig1 = state.get("ig1:operator-model", {}).get("value", {})
    ig2 = state.get("ig2:incidence-model", {}).get("value", {})
    ig3 = state.get("ig3:raw-incidence-model", {}).get("value", {})
    ig4 = state.get("ig4:natural-source-relations", {}).get("value", {})
    u1 = state.get("u1:center", {}).get("value", {})
    u4 = state.get("u4:source-relations", {}).get("value", {})
    wm = state.get("worldmirror:i0", {}).get("value", {})

    returned_operator_semantics = (
        ig1.get("scope") == "bounded_future_effect_semantics"
        and len(ig1.get("classes", {})) >= 4
    )
    incidence_basis_is_induced = (
        ig2.get("basis_origin")
        == "derived_from_observed_neutral_incidence_predicates"
        and len(ig2.get("basis", [])) >= 3
    )
    raw_carrier_scanner_is_generic = (
        ig3.get("scanner") == "single_generic_WORD_NUMBER_PUNCT"
        and ig3.get("coordinate_origin")
        == "mechanically_generated_from_generic_raw_token_edits"
    )
    natural_source_relation_inquiry = (
        ig4.get("research", {}).get("query") == "REQUEST_SOURCE_EVIDENCE"
        and bool(ig4.get("source_ids"))
    )

    u1_relation_rule = (
        u1.get("program", {})
        .get("repair_rules", {})
        .get("UNMODELED_RELATION", {})
    )
    u1_add_relation_is_state_owned = any(
        row.get("id") == "ADD_RELATION"
        and row.get("target") == "RELATION"
        and row.get("action") == "add_relation"
        for row in u1_relation_rule.get("candidates", [])
    )

    u4_grammar = set(u4.get("program", {}).get("relation_grammar", []))
    source_grounded_text_relations = (
        {"NEQ", "ARROW"} <= u4_grammar
        and bool(u4.get("retained"))
        and all(
            row.get("validation_return_id")
            and row.get("candidate", {}).get("graph", {}).get("source")
            and isinstance(row.get("candidate", {}).get("graph", {}).get("relations"), list)
            for row in u4.get("retained", {}).values()
        )
    )

    relation_rows = list(wm.get("relations", {}).values())
    worldmirror_evidence_bound_relations = bool(relation_rows) and all(
        row.get("endpoints")
        and any(
            obs.get("evidence_id") and obs.get("return_id")
            for seg in row.get("segments", [])
            for obs in seg.get("observations", {}).values()
        )
        for row in relation_rows
    )

    grammar_expand_args = method_args(R194_GRAMMAR, None, "generic_expand_once")
    historical_target_label_free_expansion = grammar_expand_args == (
        "grammar", "atoms", "meta_ops", "domain_rows"
    )

    semantic_delta_args = method_args(
        R194_SEMANTIC, "SemanticLearningMembrane", "make_delta"
    )
    historical_semantic_slots_are_caller_supplied = all(
        name in semantic_delta_args
        for name in ("subject", "predicate", "object", "authoring")
    )

    bootstrap_proposal_args = method_args(
        R194_DEVELOPMENT, "RepresentationBootstrap", "propose_constructed"
    )
    historical_constructed_executable_is_caller_supplied = (
        "executable" in bootstrap_proposal_args
        and "candidate_id" in bootstrap_proposal_args
    )

    # The current checkpoint separately contains:
    # - generic/raw carrier incidence;
    # - source-grounded text relation graphs;
    # - evidence-bound WorldMirror relation instances.
    #
    # None of the admitted current objects exposes one generic operation whose
    # declared output binds a raw/source carrier occurrence to an object/source-
    # level empirical relation instance while preserving the source span and the
    # independently returned evidence in the same typed relation object.
    #
    # This is intentionally an interface/custody test, not an attempt to infer
    # the missing semantic mapping from the EDU17R1 benchmark.
    admitted_cross_layer_binder = False

    neutral_substrate_present = all(
        (
            not missing,
            ancestral_law_bound,
            formal_law_indexed,
            live_law_neutral_grammar,
            returned_operator_semantics,
            incidence_basis_is_induced,
            raw_carrier_scanner_is_generic,
            natural_source_relation_inquiry,
            u1_add_relation_is_state_owned,
            source_grounded_text_relations,
            worldmirror_evidence_bound_relations,
            historical_target_label_free_expansion,
            historical_semantic_slots_are_caller_supplied,
            historical_constructed_executable_is_caller_supplied,
        )
    )

    status = (
        "WITHHOLD_NEUTRAL_SUBSTRATE_PRESENT_CROSS_LAYER_BINDER_UNADMITTED"
        if neutral_substrate_present and not admitted_cross_layer_binder
        else "WITHHOLD_NEUTRAL_SUBSTRATE_NOT_ESTABLISHED"
    )

    return {
        "schema": "Venus.EDU17R1IncidenceSubstrateAudit.v0.1",
        "parent_candidate": "EDU16-RC1",
        "residual": "MENTION != INCIDENCE",
        "ancestral_incidence_law_sha256": ANCESTRAL_INCIDENCE_LAW_SHA256,
        "ancestral_incidence_law_bound_in_ig10_recollection": ancestral_law_bound,
        "formal_law_indexed_in_ig10_recollection": formal_law_indexed,
        "live_law_exposes_neutral_relation_grammar": live_law_neutral_grammar,
        "ig1_returned_operator_semantics": returned_operator_semantics,
        "ig2_induced_incidence_basis": incidence_basis_is_induced,
        "ig3_generic_raw_carrier_scanner": raw_carrier_scanner_is_generic,
        "ig4_source_relation_inquiry": natural_source_relation_inquiry,
        "u1_state_owned_add_relation_repair": u1_add_relation_is_state_owned,
        "u4_source_grounded_text_relations": source_grounded_text_relations,
        "worldmirror_evidence_bound_relations": worldmirror_evidence_bound_relations,
        "historical_r194_target_label_free_grammar_expansion": historical_target_label_free_expansion,
        "historical_r194_semantic_slots_are_caller_supplied": historical_semantic_slots_are_caller_supplied,
        "historical_r194_constructed_executable_is_caller_supplied": historical_constructed_executable_is_caller_supplied,
        "neutral_relation_incidence_substrate_present": neutral_substrate_present,
        "admitted_cross_layer_binder": admitted_cross_layer_binder,
        "missing_operation": (
            "bind raw/source carrier relation occurrence to a typed object/source-level "
            "relation instance under source coordinates, provenance, and independent return"
        ),
        "status": status,
        "reason": (
            "The exact ancestral Venus Incidence Law is already provenance-bound inside "
            "IG10 recollection, and the admitted checkpoint separately contains returned "
            "operator semantics, induced incidence coordinates, a generic raw-carrier "
            "scanner, a state-owned U1 ADD_RELATION repair decision, source-grounded text "
            "relation graphs, source-relation inquiry, and evidence-bound WorldMirror relation "
            "instances. Historical R194 also preserves "
            "target-label-free grammar expansion and semantic relation storage, but the semantic "
            "slots and constructed executable are still supplied by callers. The live gap is "
            "therefore narrower than generic construction: no admitted current operation authors "
            "the carrier-to-empirical-relation binding itself. Encoding the EDU17R1 answer as "
            "that binding would be external substantive authorship."
        ),
        "lowest_local_residual": (
            "learner-side construction of typed relation endpoints/binding from raw source "
            "incidence, not a new semantic "
            "oracle, storage membrane, or evaluator"
        ),
        "next_reopening_condition": (
            "an admitted generic binder/composer is recovered from pre-existing learner-owned "
            "machinery or is authored by the Venus developmental controller from this localized "
            "residual before hidden issue #31 exposure"
        ),
        "candidate_repair_emitted": False,
        "hidden_evaluation_exposed": False,
        "promotion_authority": False,
    }


def main() -> int:
    print(json.dumps(audit(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
