from __future__ import annotations

"""Generic state-owned boolean decision tree executor/inducer.

This module contains no Venus-specific safety semantics. It can induce an exact
decision tree from opaque boolean coordinates plus returned decision labels and
later execute the resulting state-owned program without access to the teacher
that produced the training surface.
"""

from collections import Counter
from dataclasses import dataclass
from math import log2
from typing import Any, Iterable, Mapping, Sequence

from .vmk2 import digest


class InducedPolicyError(ValueError):
    pass


@dataclass(frozen=True)
class LabeledExample:
    example_id: str
    features: Mapping[str, bool]
    decision: str


def _entropy(rows: Sequence[LabeledExample]) -> float:
    if not rows:
        return 0.0
    counts = Counter(row.decision for row in rows)
    n = len(rows)
    return -sum((count / n) * log2(count / n) for count in counts.values())


def _build(rows: Sequence[LabeledExample], available: tuple[str, ...]) -> dict[str, Any]:
    labels = {row.decision for row in rows}
    if len(labels) == 1:
        return {"decision": next(iter(labels))}
    if not available:
        counts = Counter(row.decision for row in rows)
        decision = sorted(counts, key=lambda x: (-counts[x], x))[0]
        return {"decision": decision}

    base = _entropy(rows)
    gains: list[tuple[float, str]] = []
    for feature in available:
        false_rows = tuple(row for row in rows if not row.features[feature])
        true_rows = tuple(row for row in rows if row.features[feature])
        conditional = 0.0
        for part in (false_rows, true_rows):
            if part:
                conditional += (len(part) / len(rows)) * _entropy(part)
        gains.append((base - conditional, feature))

    max_gain = max(gain for gain, _ in gains)
    chosen = sorted(
        feature for gain, feature in gains if abs(gain - max_gain) < 1e-12
    )[0]
    remaining = tuple(feature for feature in available if feature != chosen)
    return {
        "feature": chosen,
        "false": _build(
            tuple(row for row in rows if not row.features[chosen]), remaining
        ),
        "true": _build(
            tuple(row for row in rows if row.features[chosen]), remaining
        ),
    }


def induce_exact_tree(examples: Iterable[LabeledExample]) -> dict[str, Any]:
    rows = tuple(examples)
    if not rows:
        raise InducedPolicyError("training examples required")
    feature_names = tuple(sorted(rows[0].features))
    if not feature_names:
        raise InducedPolicyError("at least one feature required")
    for row in rows:
        if not row.example_id or not row.decision:
            raise InducedPolicyError("example identity and decision required")
        if tuple(sorted(row.features)) != feature_names:
            raise InducedPolicyError("all examples must expose the same coordinates")

    seen: dict[tuple[bool, ...], str] = {}
    for row in rows:
        key = tuple(bool(row.features[name]) for name in feature_names)
        prior = seen.setdefault(key, row.decision)
        if prior != row.decision:
            raise InducedPolicyError("incompatible decisions for identical observations")

    tree = _build(rows, feature_names)
    body = {
        "schema": "Venus.InducedDecisionTree.v0.1",
        "feature_names": feature_names,
        "tree": tree,
        "training_example_ids": tuple(sorted(row.example_id for row in rows)),
    }
    return {**body, "program_digest": digest(body)}


def execute_tree(program: Mapping[str, Any], features: Mapping[str, bool]) -> str:
    if program.get("schema") != "Venus.InducedDecisionTree.v0.1":
        raise InducedPolicyError("unsupported induced-policy schema")
    node: Mapping[str, Any] = program["tree"]
    while "decision" not in node:
        feature = str(node["feature"])
        if feature not in features:
            raise InducedPolicyError(f"missing decision coordinate: {feature}")
        node = node["true" if bool(features[feature]) else "false"]
    return str(node["decision"])


def tree_features(program: Mapping[str, Any]) -> tuple[str, ...]:
    used: set[str] = set()

    def walk(node: Mapping[str, Any]) -> None:
        if "decision" in node:
            return
        used.add(str(node["feature"]))
        walk(node["false"])
        walk(node["true"])

    walk(program["tree"])
    return tuple(sorted(used))
