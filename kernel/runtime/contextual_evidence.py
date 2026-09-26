from __future__ import annotations

"""Generic contextual-evidence executor and key inducer.

The module knows no Minerva issue numbers, return-credit hypotheses, target
semantics, or promotion rules.  A state program supplies:
- an induced admission policy;
- fields that define one evidence context;
- whether repeated evidence identities are deduplicated;
- names of the event fields that carry identity/features/sign.

This is generic execution substrate.  What those fields *mean* belongs to the
learner-owned program and its provenance.
"""

from collections import Counter
from itertools import combinations
from typing import Any, Iterable, Mapping, Sequence

from .induced_policy import execute_tree


class ContextualEvidenceError(ValueError):
    pass


def induce_minimal_context_key(
    *,
    candidate_fields: Sequence[str],
    pair_examples: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    fields = tuple(sorted({str(x) for x in candidate_fields if str(x)}))
    rows = tuple(pair_examples)
    if not fields:
        raise ContextualEvidenceError("candidate context fields required")
    if not rows:
        raise ContextualEvidenceError("context pair examples required")

    exact: list[tuple[str, ...]] = []
    for width in range(1, len(fields) + 1):
        for subset in combinations(fields, width):
            good = True
            for row in rows:
                left = row.get("left")
                right = row.get("right")
                if not isinstance(left, Mapping) or not isinstance(right, Mapping):
                    raise ContextualEvidenceError("pair left/right mappings required")
                expected = bool(row.get("same_context"))
                observed = all(left.get(field) == right.get(field) for field in subset)
                if observed != expected:
                    good = False
                    break
            if good:
                exact.append(tuple(subset))
        if exact:
            break

    if not exact:
        return {
            "status": "WITHHOLD_NO_EXPRESSIBLE_CONTEXT_KEY",
            "key_fields": (),
            "alternatives": (),
        }
    exact = sorted(set(exact))
    if len(exact) != 1:
        return {
            "status": "WITHHOLD_AMBIGUOUS_MINIMAL_CONTEXT_KEY",
            "key_fields": (),
            "alternatives": tuple(exact),
        }
    return {
        "status": "UNIQUE_MINIMAL_CONTEXT_KEY",
        "key_fields": exact[0],
        "alternatives": exact,
    }


def apply_evidence_program(
    program: Mapping[str, Any],
    events: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    if program.get("schema") != "Venus.ContextualEvidenceProgram.v0.1":
        raise ContextualEvidenceError("unsupported contextual-evidence program")

    admission = program.get("admission_policy")
    if not isinstance(admission, Mapping):
        raise ContextualEvidenceError("admission policy required")

    key_fields = tuple(str(x) for x in program.get("key_fields", ()))
    if not key_fields:
        raise ContextualEvidenceError("context key fields required")

    id_field = str(program.get("evidence_id_field") or "")
    feature_field = str(program.get("feature_field") or "")
    sign_field = str(program.get("sign_field") or "")
    if not id_field or not feature_field or not sign_field:
        raise ContextualEvidenceError("identity/features/sign field names required")

    deduplicate = bool(program.get("deduplicate_evidence_ids"))
    admitted_decision = str(program.get("admitted_decision") or "ADMIT")

    seen: set[str] = set()
    buckets: dict[tuple[str, ...], Counter[str]] = {}
    decisions = []

    for index, raw in enumerate(events):
        event = dict(raw)
        evidence_id = str(event.get(id_field) or "")
        if not evidence_id:
            raise ContextualEvidenceError("evidence identity required")

        if deduplicate and evidence_id in seen:
            decisions.append({
                "index": index,
                "evidence_id": evidence_id,
                "decision": "IGNORE_DUPLICATE",
                "context_key": None,
            })
            continue

        features = event.get(feature_field)
        if not isinstance(features, Mapping):
            raise ContextualEvidenceError("event feature mapping required")
        decision = execute_tree(admission, {str(k): bool(v) for k, v in features.items()})
        if decision != admitted_decision:
            decisions.append({
                "index": index,
                "evidence_id": evidence_id,
                "decision": decision,
                "context_key": None,
            })
            seen.add(evidence_id)
            continue

        key = tuple(str(event.get(field) or "") for field in key_fields)
        if any(not x for x in key):
            raise ContextualEvidenceError("context-key value missing")
        sign = str(event.get(sign_field) or "")
        if not sign:
            raise ContextualEvidenceError("evidence sign required")

        buckets.setdefault(key, Counter())[sign] += 1
        seen.add(evidence_id)
        decisions.append({
            "index": index,
            "evidence_id": evidence_id,
            "decision": admitted_decision,
            "context_key": key,
        })

    serialized = {
        "|".join(key): dict(sorted(counts.items()))
        for key, counts in sorted(buckets.items())
    }
    return {
        "schema": "Venus.ContextualEvidenceExecution.v0.1",
        "buckets": serialized,
        "decisions": decisions,
        "unique_evidence_ids": len(seen),
    }
