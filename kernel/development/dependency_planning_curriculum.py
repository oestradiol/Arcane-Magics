from __future__ import annotations

"""Bounded learner-state curriculum for dependency planning.

Teacher rows provide returned observations. The learned classifier is candidate
state; kernel.runtime.task_graph supplies graph mechanics. Expected held-out
outcomes are used only by this evaluator.
"""

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

from kernel.runtime.induced_policy import LabeledExample, induce_exact_tree
from kernel.runtime.task_graph import TaskGraphError, analyze_task_graph
from kernel.runtime.vmk2 import digest


class DependencyPlanningCurriculumError(ValueError):
    pass


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def induce_candidate(cases: Mapping[str, Any]) -> dict[str, Any]:
    examples = tuple(
        LabeledExample(
            example_id=str(row["id"]),
            features={str(k): bool(v) for k, v in row["features"].items()},
            decision=str(row["decision"]),
        )
        for row in cases["classification_training"]
    )
    classifier = induce_exact_tree(examples)
    program = {
        "schema": "Venus.DependencyPlanningProgram.v0.1",
        "relation_classifier": classifier,
        "dependency_label": "DEPENDENCY",
        "resource_conflict_label": "RESOURCE_CONFLICT",
        "observation_only_label": "OBSERVATION_ONLY",
        "admissibility_field": "admissible",
        "duration_semantics": "PERT_EXPECTED_OR_FIXED_DURATION",
        "critical_path_policy": "MAX_EXPECTED_PREDECESSOR_FINISH",
        "parallel_schedule_policy": "MAX_CONFLICT_FREE_READY_SET",
        "route_policy": "MINIMUM_COST_ADMISSIBLE_ONLY",
        "planning_operators": [
            "DEPENDENCY_RECONSTRUCTION",
            "TOPOLOGICAL_VALIDATION",
            "READY_FRONTIER",
            "CRITICAL_PATH_AND_SLACK",
            "WORK_SPAN_PARALLELISM",
            "RESOURCE_CONFLICT_SCHEDULE",
            "ADMISSIBLE_SHORTEST_PATH",
        ],
    }
    body = {
        "schema": "Venus.DependencyPlanningCandidate.v0.1",
        "status": "LEARNER_INDUCED_BOUNDED_CANDIDATE",
        "program": program,
        "training_fact_ids": sorted(str(x["id"]) for x in cases["classification_training"]),
        "semantics_owner": "LEARNER_STATE_CANDIDATE",
        "generic_executor": "kernel/runtime/task_graph.py",
        "generic_inducer": "kernel/runtime/induced_policy.py",
        "independent_evaluation": False,
        "internalization_claim": False,
        "promotion_authority": False,
        "truth_authority": False,
    }
    return {**body, "candidate_id": digest(body)}


def _rename_graph(graph: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    obj = deepcopy(dict(graph))
    mapping = {"A":"K7","B":"K2","C":"K8","D":"K3","H1":"K4","H2":"K5","G":"K6","E":"K9"}
    reverse = {value: key for key, value in mapping.items()}
    for task in obj.get("tasks", ()):
        task["id"] = mapping.get(str(task["id"]), str(task["id"]))
    for fact in obj.get("facts", ()):
        fact["source"] = mapping.get(str(fact["source"]), str(fact["source"]))
        fact["target"] = mapping.get(str(fact["target"]), str(fact["target"]))
    return obj, reverse


def _restore(values, reverse):
    return [reverse.get(str(x), str(x)) for x in values]


def _normalize(result: Mapping[str, Any], reverse: Mapping[str, str]) -> dict[str, Any]:
    return {
        "edges": sorted(sorted(_restore(edge, reverse)) for edge in result["edges"]),
        "ready_frontier": sorted(_restore(result["ready_frontier"], reverse)),
        "critical_path": _restore(result["critical_path"], reverse),
        "span": result["span"],
        "work": result["work"],
        "slack": {
            reverse.get(str(key), str(key)): value
            for key, value in result["slack"].items()
        },
    }


def _route_schedule_is_valid(graph: Mapping[str, Any], result: Mapping[str, Any]) -> bool:
    starts = {row["task"]: float(row["start"]) for row in result["schedule"]}
    finishes = {row["task"]: float(row["finish"]) for row in result["schedule"]}
    if len(starts) != len(graph["tasks"]):
        return False
    for fact in graph["facts"]:
        features = fact["features"]
        if features.get("prerequisite_assertion") is True:
            if starts.get(fact["target"], float("-inf")) < finishes.get(fact["source"], float("inf")):
                return False
    h1 = next(row for row in result["schedule"] if row["task"] == "H1")
    h2 = next(row for row in result["schedule"] if row["task"] == "H2")
    disjoint = float(h1["finish"]) <= float(h2["start"]) or float(h2["finish"]) <= float(h1["start"])
    return disjoint


def _withhold_status(candidate, graph) -> str:
    try:
        analyze_task_graph(candidate, graph)
    except TaskGraphError as exc:
        return str(exc)
    return "UNEXPECTED_EXECUTION"


def evaluate(
    *,
    prefreeze: Mapping[str, Any],
    cases: Mapping[str, Any],
    candidate: Mapping[str, Any],
) -> dict[str, Any]:
    if prefreeze.get("schema") != "Venus.DependencyPlanningCurriculumPrefreeze.v0.1":
        raise DependencyPlanningCurriculumError("unsupported dependency-planning prefreeze")
    if cases.get("schema") != "Venus.DependencyPlanningDidacticCases.v0.1":
        raise DependencyPlanningCurriculumError("unsupported dependency-planning cases")

    base = cases["base_graph"]
    expected = cases["expected"]
    base_result = analyze_task_graph(candidate, base)

    renamed, reverse = _rename_graph(base)
    renamed["tasks"] = list(reversed(renamed["tasks"]))
    renamed["facts"] = list(reversed(renamed["facts"]))
    renamed_result = analyze_task_graph(candidate, renamed)

    recombined = deepcopy(base)
    edge = cases["heldout_recombination"]["add_dependency"]
    recombined["facts"].append({
        "id":"heldout-recombined-edge",
        "source":edge[0],
        "target":edge[1],
        "features":{"prerequisite_assertion":True,"temporal_order_only":False,"resource_exclusion":False},
    })
    recombined_result = analyze_task_graph(candidate, recombined)

    critical = deepcopy(base)
    next(task for task in critical["tasks"] if task["id"] == "G")["duration"] = 4
    critical_result = analyze_task_graph(candidate, critical)

    noncritical = deepcopy(base)
    next(task for task in noncritical["tasks"] if task["id"] == "H1")["duration"] = 4
    noncritical_result = analyze_task_graph(candidate, noncritical)

    dependency_intervention = deepcopy(base)
    dependency_intervention["facts"].append({
        "id":"intervention-edge",
        "source":"A",
        "target":"B",
        "features":{"prerequisite_assertion":True,"temporal_order_only":False,"resource_exclusion":False},
    })
    dependency_result = analyze_task_graph(candidate, dependency_intervention)

    cycle = deepcopy(base)
    cycle["facts"].append({
        "id":"cycle-edge",
        "source":"E",
        "target":"A",
        "features":{"prerequisite_assertion":True,"temporal_order_only":False,"resource_exclusion":False},
    })
    underspecified = deepcopy(base)
    underspecified["underspecified"] = True
    missing_duration = deepcopy(base)
    next(task for task in missing_duration["tasks"] if task["id"] == "C").pop("duration")

    b1_checks = {
        "opaque_rename_and_presentation_permutation_invariant":
            _normalize(base_result, {}) == _normalize(renamed_result, reverse),
        "dependency_distinct_from_temporal_adjacency":
            ["A","B"] not in base_result["edges"] and expected["base_edges"] == base_result["edges"],
        "heldout_fork_join_recombination":
            ["C","D"] in recombined_result["edges"] and recombined_result["span"] == expected["recombined_span"],
        "perturbed_candidate_training_order_invariant": True,
    }
    reordered = dict(cases)
    reordered["classification_training"] = list(reversed(cases["classification_training"]))
    reordered_candidate = induce_candidate(reordered)
    b1_checks["perturbed_candidate_training_order_invariant"] = (
        reordered_candidate["program"]["relation_classifier"]["tree"]
        == candidate["program"]["relation_classifier"]["tree"]
    )

    schedule_ok = _route_schedule_is_valid(base, base_result)
    lawful_route = base_result["shortest_lawful_path"]
    b2_checks = {
        "critical_duration_intervention_changes_span_and_path":
            critical_result["span"] == expected["critical_intervention_span"]
            and critical_result["critical_path"] == expected["critical_intervention_path"],
        "noncritical_duration_intervention_preserves_span":
            noncritical_result["span"] == expected["noncritical_intervention_span"],
        "dependency_intervention_changes_frontier_and_span":
            dependency_result["ready_frontier"] == expected["dependency_intervention_ready"]
            and dependency_result["span"] == expected["dependency_intervention_span"],
        "parallelism_respects_dependencies_and_resource_conflict":
            base_result["parallelizable_sets"] == expected["base_parallelizable_sets"]
            and base_result["schedule_makespan"] == expected["base_schedule_makespan"]
            and schedule_ok,
        "shorter_inadmissible_route_is_rejected":
            lawful_route == expected["base_lawful_route"],
        "cycle_underspecification_and_missing_duration_withhold":
            _withhold_status(candidate, cycle) == "WITHHOLD_DEPENDENCY_CYCLE"
            and _withhold_status(candidate, underspecified) == "WITHHOLD_UNDERSPECIFIED_GRAPH"
            and _withhold_status(candidate, missing_duration) == "WITHHOLD_MISSING_DURATION",
    }

    candidate_ablation = deepcopy(dict(candidate))
    candidate_ablation["program"] = dict(candidate_ablation["program"])
    candidate_ablation["program"].pop("relation_classifier", None)
    candidate_ablation_status = _withhold_status(candidate_ablation, base)
    operator_ablation = deepcopy(dict(candidate))
    operator_ablation["program"] = dict(operator_ablation["program"])
    operator_ablation["program"]["planning_operators"] = list(
        operator_ablation["program"]["planning_operators"]
    )
    operator_ablation["program"]["planning_operators"].remove("CRITICAL_PATH_AND_SLACK")
    operator_ablation_status = _withhold_status(operator_ablation, base)
    b2_checks["candidate_state_ablation_withholds"] = (
        candidate_ablation_status == "WITHHOLD_MISSING_RELATION_CLASSIFIER"
        and operator_ablation_status == "WITHHOLD_MISSING_PLANNING_OPERATOR"
    )

    b1_pass = all(b1_checks.values())
    b2_pass = b1_pass and all(b2_checks.values())
    return {
        "schema": "Venus.DependencyPlanningCurriculumResult.v0.1",
        "status": "PASS_BOUNDED_DEPENDENCY_PLANNING_B1_B2" if b2_pass else "WITHHOLD_DEPENDENCY_PLANNING_DISCRIMINATOR_NOT_MET",
        "candidate_id": candidate["candidate_id"],
        "b1_checks": b1_checks,
        "b1_pass": b1_pass,
        "b2_checks": b2_checks,
        "b2_pass": b2_pass,
        "bounded_base_result": base_result,
        "critical_intervention_result": critical_result,
        "noncritical_intervention_result": noncritical_result,
        "dependency_intervention_result": dependency_result,
        "withhold_cases": {
            "cycle": _withhold_status(candidate, cycle),
            "underspecified": _withhold_status(candidate, underspecified),
            "missing_duration": _withhold_status(candidate, missing_duration),
            "candidate_state_ablation": candidate_ablation_status,
            "candidate_operator_ablation": operator_ablation_status,
        },
        "independent_evaluation": False,
        "internalization_claim": False,
        "promotion_authority": False,
        "truth_authority": False,
        "next_residual": "FRESH_LEARNER_SELECTED_PLANNING_EPISODE_THEN_LATER_DEVELOPMENTAL_TRANSFER" if b2_pass else "REVISE_CANDIDATE_RELATION_OR_PLANNING_STATE",
        "claim_fence": "A pass establishes only bounded dependency reconstruction and schedule-response behavior on these didactic/intervention cases. It does not establish B3 internalization, self-development planning, independent evaluation, truth authority, or promotion."
    }


def run(prefreeze_path: str | Path, cases_path: str | Path) -> tuple[dict[str, Any], dict[str, Any]]:
    prefreeze = load_json(prefreeze_path)
    cases = load_json(cases_path)
    candidate = induce_candidate(cases)
    result = evaluate(prefreeze=prefreeze, cases=cases, candidate=candidate)
    return candidate, result
