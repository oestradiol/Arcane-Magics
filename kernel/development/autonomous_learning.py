from __future__ import annotations

"""Bounded learning state for autonomous work selection.

Authorization/admission is not task success. Merge/close state alone never
updates learner preference. Only an explicit external review-return marker may
change future work utility, and that marker is typed only as usefulness for
future work selection, not truth, scientific validation, or promotion.
"""

from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping

POSITIVE_LABEL = "venus-return-useful"
NEGATIVE_LABEL = "venus-return-unhelpful"
INVALID_LABEL = "venus-return-invalid"


@dataclass(frozen=True)
class WorkLearningState:
    seen_review_prs: tuple[int, ...]
    kind_useful: Mapping[str, int]
    kind_unhelpful: Mapping[str, int]

    def utility(self, kind: str) -> float:
        useful = int(self.kind_useful.get(kind, 0))
        unhelpful = int(self.kind_unhelpful.get(kind, 0))
        total = useful + unhelpful
        return 0.0 if total == 0 else (useful - unhelpful) / total


def empty_state() -> WorkLearningState:
    return WorkLearningState(
        seen_review_prs=(),
        kind_useful={"ISSUE": 0, "PR": 0},
        kind_unhelpful={"ISSUE": 0, "PR": 0},
    )


def from_json(obj: Mapping[str, Any]) -> WorkLearningState:
    # v0.1 migration is intentionally non-rewarding: historical merge/close
    # counts are not imported as learning because admission != utility.
    if obj.get("schema") == "Venus.AutonomousLearningState.v0.1":
        return empty_state()
    return WorkLearningState(
        seen_review_prs=tuple(int(x) for x in obj.get("seen_review_prs", ())),
        kind_useful={str(k): int(v) for k, v in obj.get("kind_useful", {}).items()},
        kind_unhelpful={str(k): int(v) for k, v in obj.get("kind_unhelpful", {}).items()},
    )


def to_json(state: WorkLearningState) -> dict[str, Any]:
    return {
        "schema": "Venus.AutonomousLearningState.v0.2",
        "seen_review_prs": list(state.seen_review_prs),
        "kind_useful": dict(state.kind_useful),
        "kind_unhelpful": dict(state.kind_unhelpful),
        "review_return_semantics": {
            POSITIVE_LABEL: "useful for future work selection only",
            NEGATIVE_LABEL: "unhelpful for future work selection only",
            INVALID_LABEL: "invalid episode; no preference update",
        },
        "truth_authority": False,
        "promotion_authority": False,
        "merge_authority": False,
    }


def _label_names(pr: Mapping[str, Any]) -> set[str]:
    out: set[str] = set()
    for label in pr.get("labels", ()) or ():
        if isinstance(label, Mapping):
            name = label.get("name")
        else:
            name = label
        if name:
            out.add(str(name).strip().lower())
    return out


def update_from_cycle_prs(
    state: WorkLearningState,
    prs: Iterable[Mapping[str, Any]],
) -> WorkLearningState:
    seen = set(state.seen_review_prs)
    useful = dict(state.kind_useful)
    unhelpful = dict(state.kind_unhelpful)

    for pr in prs:
        number = int(pr["number"])
        if number in seen:
            continue
        title = str(pr.get("title", ""))
        match = re.match(r"venus: autonomous cycle (issue|pr)-(\d+)$", title, re.I)
        if not match:
            continue

        labels = _label_names(pr)
        marked = labels & {POSITIVE_LABEL, NEGATIVE_LABEL, INVALID_LABEL}
        if not marked:
            # Merge/close/open state alone is NOT a learner return.
            continue
        if len(marked) != 1:
            # Conflicting external review return is not learnable.
            continue

        marker = next(iter(marked))
        if marker == INVALID_LABEL:
            seen.add(number)
            continue

        kind = match.group(1).upper()
        if marker == POSITIVE_LABEL:
            useful[kind] = useful.get(kind, 0) + 1
        elif marker == NEGATIVE_LABEL:
            unhelpful[kind] = unhelpful.get(kind, 0) + 1
        seen.add(number)

    return WorkLearningState(
        seen_review_prs=tuple(sorted(seen)),
        kind_useful=useful,
        kind_unhelpful=unhelpful,
    )


def target_markers(prs: Iterable[Mapping[str, Any]]) -> tuple[tuple[str, int], ...]:
    out: list[tuple[str, int]] = []
    for pr in prs:
        title = str(pr.get("title", ""))
        match = re.match(r"venus: autonomous cycle (issue|pr)-(\d+)$", title, re.I)
        if match and str(pr.get("state", "")).upper() == "OPEN":
            out.append((match.group(1).upper(), int(match.group(2))))
    return tuple(sorted(set(out)))
