from __future__ import annotations

"""Generic executor for learner-state task-graph programs.

This module supplies graph mechanics only. A candidate provides the relation
classifier that interprets returned facts; issue/curriculum meaning and expected
answers remain outside this runtime.
"""

from itertools import combinations
from typing import Any, Mapping, Sequence
import heapq

from .induced_policy import execute_tree


class TaskGraphError(ValueError):
    pass


def _withhold(reason: str) -> None:
    raise TaskGraphError("WITHHOLD_" + reason)


def _number(value: Any, field: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        _withhold("INVALID_" + field.upper())
    if out < 0:
        _withhold("NEGATIVE_" + field.upper())
    return out


def _clean_number(value: float) -> float | int:
    return int(value) if value.is_integer() else value


def expected_duration(task: Mapping[str, Any]) -> tuple[float, float]:
    if "duration" in task:
        value = _number(task["duration"], "duration")
        return value, 0.0
    pert = task.get("pert")
    if not isinstance(pert, Mapping):
        _withhold("MISSING_DURATION")
    try:
        optimistic = _number(pert["optimistic"], "optimistic_duration")
        likely = _number(pert["most_likely"], "most_likely_duration")
        pessimistic = _number(pert["pessimistic"], "pessimistic_duration")
    except KeyError:
        _withhold("UNDERSPECIFIED_PERT")
    if not optimistic <= likely <= pessimistic:
        _withhold("INVALID_PERT_ORDER")
    return (optimistic + 4 * likely + pessimistic) / 6, ((pessimistic - optimistic) / 6) ** 2


def _maximal_ready_sets(ready: Sequence[str], conflicts: set[tuple[str, str]]) -> list[list[str]]:
    if len(ready) > 16:
        _withhold("FRONTIER_TOO_LARGE_FOR_BOUNDED_ENUMERATION")
    valid: list[tuple[str, ...]] = []
    for width in range(1, len(ready) + 1):
        for subset in combinations(sorted(ready), width):
            if all(tuple(sorted(pair)) not in conflicts
                   for pair in combinations(subset, 2)):
                valid.append(subset)
    if not ready:
        return []
    best = max(len(x) for x in valid)
    return [list(x) for x in sorted(set(x for x in valid if len(x) == best))]


def _topological(nodes: Sequence[str], edges: set[tuple[str, str]]) -> list[str]:
    incoming = {node: 0 for node in nodes}
    outgoing = {node: set() for node in nodes}
    for before, after in edges:
        if before not in incoming or after not in incoming:
            _withhold("DEPENDENCY_ENDPOINT_MISSING")
        if after not in outgoing[before]:
            outgoing[before].add(after)
            incoming[after] += 1
    ready = sorted(node for node, count in incoming.items() if count == 0)
    order: list[str] = []
    while ready:
        node = ready.pop(0)
        order.append(node)
        for child in sorted(outgoing[node]):
            incoming[child] -= 1
            if incoming[child] == 0:
                ready.append(child)
                ready.sort()
    if len(order) != len(nodes):
        _withhold("DEPENDENCY_CYCLE")
    return order


def _shortest_lawful_path(routes: Sequence[Mapping[str, Any]], source: str, target: str) -> dict[str, Any]:
    adjacency: dict[str, list[tuple[str, float]]] = {}
    for row in routes:
        try:
            start, end = str(row["source"]), str(row["target"])
            cost = _number(row["cost"], "route_cost")
        except KeyError:
            _withhold("UNDERSPECIFIED_ROUTE")
        if row.get("admissible") is True:
            adjacency.setdefault(start, []).append((end, cost))
    heap: list[tuple[float, tuple[str, ...], str]] = [(0.0, (source,), source)]
    best: dict[str, float] = {source: 0.0}
    while heap:
        cost, path, node = heapq.heappop(heap)
        if node == target:
            return {"path": list(path), "cost": _clean_number(cost)}
        if cost != best.get(node):
            continue
        for child, edge_cost in sorted(adjacency.get(node, ())):
            total = cost + edge_cost
            if total < best.get(child, float("inf")):
                best[child] = total
                heapq.heappush(heap, (total, path + (child,), child))
    _withhold("NO_LAWFUL_ROUTE")
    raise AssertionError("unreachable")


def analyze_task_graph(candidate: Mapping[str, Any], graph: Mapping[str, Any]) -> dict[str, Any]:
    if candidate.get("schema") != "Venus.DependencyPlanningCandidate.v0.1":
        _withhold("UNSUPPORTED_CANDIDATE")
    program = candidate.get("program")
    if not isinstance(program, Mapping):
        _withhold("MISSING_CANDIDATE_PROGRAM")
    required_operators = {
        "DEPENDENCY_RECONSTRUCTION",
        "TOPOLOGICAL_VALIDATION",
        "READY_FRONTIER",
        "CRITICAL_PATH_AND_SLACK",
        "WORK_SPAN_PARALLELISM",
        "RESOURCE_CONFLICT_SCHEDULE",
        "ADMISSIBLE_SHORTEST_PATH",
    }
    if not required_operators.issubset(set(program.get("planning_operators", ()))):
        _withhold("MISSING_PLANNING_OPERATOR")
    if program.get("duration_semantics") != "PERT_EXPECTED_OR_FIXED_DURATION":
        _withhold("UNSUPPORTED_DURATION_POLICY")
    if program.get("critical_path_policy") != "MAX_EXPECTED_PREDECESSOR_FINISH":
        _withhold("UNSUPPORTED_CRITICAL_PATH_POLICY")
    if program.get("parallel_schedule_policy") != "MAX_CONFLICT_FREE_READY_SET":
        _withhold("UNSUPPORTED_PARALLEL_POLICY")
    if program.get("route_policy") != "MINIMUM_COST_ADMISSIBLE_ONLY":
        _withhold("UNSUPPORTED_ROUTE_POLICY")
    if graph.get("underspecified") is True:
        _withhold("UNDERSPECIFIED_GRAPH")

    raw_tasks = graph.get("tasks")
    raw_facts = graph.get("facts")
    if not isinstance(raw_tasks, list) or not raw_tasks or not isinstance(raw_facts, list):
        _withhold("MISSING_GRAPH_DATA")
    tasks: dict[str, Mapping[str, Any]] = {}
    for task in raw_tasks:
        if not isinstance(task, Mapping):
            _withhold("INVALID_TASK")
        task_id = str(task.get("id") or "")
        if not task_id or task_id in tasks:
            _withhold("INVALID_TASK_IDENTITY")
        tasks[task_id] = task
    if len(tasks) > 32:
        _withhold("GRAPH_EXCEEDS_BOUNDED_EXECUTOR")
    nodes = sorted(tasks)
    durations: dict[str, float] = {}
    variance: dict[str, float] = {}
    for node, task in tasks.items():
        durations[node], variance[node] = expected_duration(task)

    classifier = program.get("relation_classifier")
    if not isinstance(classifier, Mapping):
        _withhold("MISSING_RELATION_CLASSIFIER")
    edges: set[tuple[str, str]] = set()
    conflicts: set[tuple[str, str]] = set()
    decisions = []
    for fact in raw_facts:
        if not isinstance(fact, Mapping):
            _withhold("INVALID_RELATION_FACT")
        before, after = str(fact.get("source") or ""), str(fact.get("target") or "")
        if before not in tasks or after not in tasks:
            _withhold("RELATION_ENDPOINT_MISSING")
        features = fact.get("features")
        if not isinstance(features, Mapping):
            _withhold("MISSING_RELATION_FEATURES")
        label = execute_tree(classifier, {str(k): bool(v) for k, v in features.items()})
        if label == str(program.get("dependency_label")):
            edges.add((before, after))
        elif label == str(program.get("resource_conflict_label")):
            conflicts.add(tuple(sorted((before, after))))
        elif label != str(program.get("observation_only_label")):
            _withhold("UNSUPPORTED_RELATION_CLASS")
        decisions.append({"fact_id": str(fact.get("id") or ""), "decision": label})

    order = _topological(nodes, edges)
    incoming = {node: set() for node in nodes}
    outgoing = {node: set() for node in nodes}
    for before, after in edges:
        incoming[after].add(before)
        outgoing[before].add(after)

    earliest_start: dict[str, float] = {}
    earliest_finish: dict[str, float] = {}
    predecessor: dict[str, str | None] = {}
    for node in order:
        best_pred = sorted(incoming[node], key=lambda x: (-earliest_finish[x], x))[0] if incoming[node] else None
        earliest_start[node] = 0.0 if best_pred is None else earliest_finish[best_pred]
        earliest_finish[node] = earliest_start[node] + durations[node]
        predecessor[node] = best_pred
    span = max(earliest_finish.values())

    terminal = sorted(node for node in nodes if not outgoing[node])
    end = sorted(terminal, key=lambda x: (-earliest_finish[x], x))[0]
    critical_path = []
    current: str | None = end
    while current is not None:
        critical_path.append(current)
        current = predecessor[current]
    critical_path.reverse()

    latest_start: dict[str, float] = {}
    latest_finish: dict[str, float] = {}
    for node in reversed(order):
        latest_finish[node] = span if not outgoing[node] else min(latest_start[x] for x in outgoing[node])
        latest_start[node] = latest_finish[node] - durations[node]
    slack = {node: latest_start[node] - earliest_start[node] for node in nodes}

    ready = [node for node in nodes if not incoming[node]]
    parallelizable = _maximal_ready_sets(ready, conflicts)
    work = sum(durations.values())

    # A deterministic list schedule respects precedence and pairwise resource
    # conflicts. It is a valid schedule witness, not a claim of global optimality.
    remaining = set(nodes)
    finished: set[str] = set()
    running: dict[str, float] = {}
    schedule: list[dict[str, Any]] = []
    now = 0.0
    while remaining or running:
        completed = sorted(node for node, finish in running.items() if finish <= now)
        for node in completed:
            finished.add(node)
            del running[node]
        ready_now = sorted(
            node for node in remaining
            if incoming[node] <= finished and tasks[node].get(str(program.get("admissibility_field")), True) is True
        )
        started_any = False
        available = [
            node for node in ready_now
            if all(tuple(sorted((node, active))) not in conflicts for active in running)
        ]
        groups = _maximal_ready_sets(available, conflicts)
        selected_group = groups[0] if groups else []
        for selected in selected_group:
            remaining.remove(selected)
            end_time = now + durations[selected]
            running[selected] = end_time
            schedule.append({
                "task": selected,
                "start": _clean_number(now),
                "finish": _clean_number(end_time),
            })
        started_any = bool(selected_group)
        if not remaining and not running:
            break
        if running:
            now = min(running.values())
        elif remaining and not started_any:
            _withhold("NO_ADMISSIBLE_READY_TASK")
    schedule_makespan = max((float(row["finish"]) for row in schedule), default=0.0)

    route = graph.get("route_query")
    shortest = None
    if route is not None:
        if not isinstance(route, Mapping):
            _withhold("INVALID_ROUTE_QUERY")
        shortest = _shortest_lawful_path(
            graph.get("routes", ()), str(route.get("source") or ""), str(route.get("target") or "")
        )

    return {
        "schema": "Venus.TaskGraphExecution.v0.1",
        "status": "EXECUTED_BOUNDED_TASK_GRAPH",
        "edges": [list(x) for x in sorted(edges)],
        "resource_conflicts": [list(x) for x in sorted(conflicts)],
        "relation_decisions": decisions,
        "topological_order": order,
        "ready_frontier": ready,
        "parallelizable_sets": parallelizable,
        "durations": {k: _clean_number(v) for k, v in sorted(durations.items())},
        "pert_variance": {k: _clean_number(v) for k, v in sorted(variance.items())},
        "work": _clean_number(work),
        "span": _clean_number(span),
        "available_parallelism": _clean_number(work / span) if span else None,
        "critical_path": critical_path,
        "slack": {k: _clean_number(v) for k, v in sorted(slack.items())},
        "schedule": schedule,
        "schedule_makespan": _clean_number(schedule_makespan),
        "shortest_lawful_path": shortest,
        "promotion_authority": False,
        "truth_authority": False,
    }
