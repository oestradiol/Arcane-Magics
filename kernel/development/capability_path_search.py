from __future__ import annotations

"""Target-blind capability composition search.

The search engine knows only typed interfaces, preserved invariants, and cost.
It contains no EDU17R1 vocabulary, benchmark labels, semantic answer table, or
hidden-evaluation data.
"""

from dataclasses import dataclass
from heapq import heappop, heappush
from typing import Iterable, Mapping


class CapabilitySearchError(ValueError):
    pass


@dataclass(frozen=True)
class Capability:
    capability_id: str
    input_type: str
    output_type: str
    preserves: frozenset[str]
    cost: int = 1


@dataclass(frozen=True)
class SearchResult:
    status: str
    paths: tuple[tuple[str, ...], ...]
    total_cost: int | None
    required_invariants: tuple[str, ...]
    source_type: str
    target_type: str


def search_paths(
    capabilities: Iterable[Capability],
    *,
    source_type: str,
    target_type: str,
    required_invariants: Iterable[str],
) -> SearchResult:
    caps = tuple(capabilities)
    required = frozenset(required_invariants)
    if not source_type or not target_type:
        raise CapabilitySearchError("source_type and target_type required")
    if not required:
        raise CapabilitySearchError("required invariants required")

    by_input: dict[str, list[Capability]] = {}
    for cap in caps:
        if cap.cost < 0:
            raise CapabilitySearchError("negative capability cost")
        by_input.setdefault(cap.input_type, []).append(cap)
    for rows in by_input.values():
        rows.sort(key=lambda c: (c.cost, c.capability_id))

    # State tracks only invariants still preserved by the whole composition.
    # Start with the full required set; every edge may preserve or destroy some.
    q: list[tuple[int, str, tuple[str, ...], frozenset[str]]] = []
    heappush(q, (0, source_type, tuple(), required))
    best_cost: dict[tuple[str, frozenset[str]], int] = {(source_type, required): 0}
    winners: list[tuple[str, ...]] = []
    winner_cost: int | None = None

    while q:
        cost, typ, path, preserved = heappop(q)
        if winner_cost is not None and cost > winner_cost:
            break
        if typ == target_type and required <= preserved:
            winner_cost = cost if winner_cost is None else winner_cost
            if cost == winner_cost:
                winners.append(path)
            continue

        for cap in by_input.get(typ, ()):
            next_preserved = preserved & cap.preserves
            if not required <= next_preserved:
                continue
            nc = cost + cap.cost
            key = (cap.output_type, next_preserved)
            old = best_cost.get(key)
            if old is not None and nc > old:
                continue
            if old is None or nc < old:
                best_cost[key] = nc
            heappush(q, (nc, cap.output_type, path + (cap.capability_id,), next_preserved))

    if not winners:
        return SearchResult(
            status="WITHHOLD_NO_ADMISSIBLE_COMPOSITION",
            paths=(),
            total_cost=None,
            required_invariants=tuple(sorted(required)),
            source_type=source_type,
            target_type=target_type,
        )

    unique = tuple(sorted(set(winners)))
    status = "UNIQUE" if len(unique) == 1 else "WITHHOLD_AMBIGUOUS_MINIMAL_COMPOSITION"
    return SearchResult(
        status=status,
        paths=unique,
        total_cost=winner_cost,
        required_invariants=tuple(sorted(required)),
        source_type=source_type,
        target_type=target_type,
    )


def capabilities_from_mapping(value: Mapping[str, object]) -> tuple[Capability, ...]:
    out = []
    for row in value.get("capabilities", ()):
        if not isinstance(row, Mapping):
            raise CapabilitySearchError("capability row must be mapping")
        out.append(
            Capability(
                capability_id=str(row["id"]),
                input_type=str(row["input_type"]),
                output_type=str(row["output_type"]),
                preserves=frozenset(str(x) for x in row.get("preserves", ())),
                cost=int(row.get("cost", 1)),
            )
        )
    return tuple(out)
