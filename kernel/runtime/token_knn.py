from __future__ import annotations

"""Generic state-owned token-set nearest-neighbor executor.

No repository, Lateralizer, PR, path, issue, or project semantics live here.
A caller supplies an inert state program and opaque token sets.
"""

from collections import Counter
from typing import Any, Mapping, Sequence


class TokenKNNError(ValueError):
    pass


def _tokens(value: Sequence[str]) -> frozenset[str]:
    out=frozenset(str(x) for x in value)
    if not out:
        raise TokenKNNError("nonempty opaque token set required")
    return out


def _sim(a: frozenset[str],b: frozenset[str]) -> float:
    union=a|b
    return len(a&b)/len(union) if union else 0.0


def validate_program(program: Mapping[str,Any]) -> None:
    if program.get("schema")!="Venus.StateOwnedTokenKNN.v0.1":
        raise TokenKNNError("unsupported token-knn schema")
    cfg=program.get("program",{})
    if cfg.get("metric")!="JACCARD":
        raise TokenKNNError("only JACCARD metric admitted")
    k=int(cfg.get("k") or 0)
    if k<1:
        raise TokenKNNError("k must be positive")
    examples=tuple(cfg.get("examples",()))
    if len(examples)<k:
        raise TokenKNNError("fewer examples than k")
    ids=set()
    for row in examples:
        eid=str(row.get("example_id") or "")
        if not eid or eid in ids:
            raise TokenKNNError("unique example identity required")
        ids.add(eid)
        _tokens(row.get("tokens",()))
        if str(row.get("decision")) not in {"0","1"}:
            raise TokenKNNError("binary decision required")


def execute(program: Mapping[str,Any], query_tokens: Sequence[str]) -> str:
    validate_program(program)
    cfg=program["program"]
    query=_tokens(query_tokens)
    examples=tuple(cfg["examples"])
    ranked=sorted(
        (
            (-_sim(_tokens(row["tokens"]),query),str(row["example_id"]),str(row["decision"]))
            for row in examples
        ),
        key=lambda x:(x[0],x[1]),
    )[:int(cfg["k"])]
    counts=Counter(x[2] for x in ranked)
    if counts["1"]==counts["0"]:
        all_counts=Counter(str(x["decision"]) for x in examples)
        if all_counts["1"]==all_counts["0"]:
            return str(cfg.get("exact_tie_decision","0"))
        return "1" if all_counts["1"]>all_counts["0"] else "0"
    return "1" if counts["1"]>counts["0"] else "0"
