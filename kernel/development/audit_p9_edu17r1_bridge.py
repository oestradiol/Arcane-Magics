#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import ast
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
P9 = ROOT / "provenance/historical-runtime/R194/source/venus_seed_v0/capability_pressure_diagnosis.py"
MACHINE = ROOT / "provenance/historical-runtime/R194/source/venus_seed_v0/capability_pressure_multifamily.py"

# This audit does not decide the EDU17R1 repair. It asks only whether the
# historical P9 donor already exposes a neutral interface capable of expressing
# the residual without adding a semantic-specific event/operator.


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def string_literals(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }


def extract_event_ops(path: Path) -> tuple[str, ...]:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    ops: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare) and isinstance(node.left, ast.Name) and node.left.id == "op":
            for comp in node.comparators:
                if isinstance(comp, ast.Constant) and isinstance(comp.value, str):
                    ops.add(comp.value)
                elif isinstance(comp, (ast.Set, ast.Tuple, ast.List)):
                    for elt in comp.elts:
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                            ops.add(elt.value)
    return tuple(sorted(ops))


def extract_mutation_axes(path: Path) -> tuple[str, ...]:
    text = path.read_text(encoding="utf-8")
    known = (
        "binding_capacity",
        "recent_capacity",
        "stack_depth",
        "composition_depth",
        "hypothesis_slots",
        "revision_memory",
        "plan_slots",
        "source_indexed",
        "associative_memory",
    )
    return tuple(axis for axis in known if axis in text)


def audit() -> dict:
    event_ops = extract_event_ops(MACHINE)
    axes = extract_mutation_axes(P9)

    # P9's generic candidate_variations mutates configuration only. No candidate
    # changes the event-processing vocabulary itself.
    semantic_relation_ops = tuple(
        op for op in event_ops
        if any(token in op.lower() for token in ("incidence", "predicate", "relation", "referent"))
    )
    source_text = P9.read_text(encoding="utf-8")
    grammar_mutates_event_semantics = (
        "candidate event op" in source_text.lower()
        or "event_semantics" in source_text.lower()
    )

    bridge_available = bool(semantic_relation_ops) or grammar_mutates_event_semantics
    status = (
        "BRIDGE_AVAILABLE_NEEDS_PROSPECTIVE_TEST"
        if bridge_available
        else "WITHHOLD_NO_NEUTRAL_INCIDENCE_OPERATOR"
    )

    return {
        "schema": "Venus.P9EDU17R1BridgeAudit.v0.1",
        "parent_candidate": "EDU16-RC1",
        "residual": "MENTION != INCIDENCE",
        "historical_donor": "P9DiagnosticMembrane",
        "p9_source_sha256": sha256(P9),
        "machine_source_sha256": sha256(MACHINE),
        "event_ops": list(event_ops),
        "mutation_axes": list(axes),
        "semantic_relation_ops": list(semantic_relation_ops),
        "candidate_grammar_changes_event_semantics": grammar_mutates_event_semantics,
        "status": status,
        "reason": (
            "Historical P9 can select generic capacity/configuration changes by "
            "counterfactual behavior on unlabeled failed traces, but its candidate "
            "grammar does not add event semantics and the inherited event machine "
            "exposes no neutral incidence/referent/relation operator. Encoding the "
            "correct incidence rule as a new special event here would be external "
            "substantive authorship, not learner-owned diagnosis."
        ),
        "next_reopening_condition": (
            "An already-admitted or prospectively learner-authored neutral relation/"
            "incidence representation becomes executable without hidden #31 exposure."
        ),
        "hidden_evaluation_exposed": False,
        "candidate_repair_emitted": False,
        "promotion_authority": False,
    }


def main() -> int:
    print(json.dumps(audit(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
