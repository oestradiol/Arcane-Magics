from __future__ import annotations

"""Generic state-owned relation-trace executor.

The executor contains no repository/issue/domain answer vocabulary. A caller supplies:
- opaque anchor terms;
- returned source text plus indexed source identities;
- a state-owned candidate family.

It constructs source/anchor co-occurrence relations and selects one bounded trace
without access to future return or hidden evaluation.
"""

from dataclasses import dataclass, asdict
import re
from typing import Any, Iterable, Mapping, Sequence

from .vmk2 import digest


class RelationTraceError(ValueError):
    pass


@dataclass(frozen=True)
class TraceTerm:
    term: str
    source_ids: tuple[str, ...]
    anchor_terms: tuple[str, ...]
    source_support: int
    anchor_degree: int
    title_support: int


@dataclass(frozen=True)
class RelationTrace:
    schema: str
    trace_id: str
    program_digest: str
    config_id: str
    anchor_terms: tuple[str, ...]
    terms: tuple[str, ...]
    relations: tuple[TraceTerm, ...]
    status: str
    future_return_input: bool = False
    hidden_evaluation_input: bool = False
    promotion_authority: bool = False
    truth_authority: bool = False


def _tokenize(text: str, *, min_length: int, stop: frozenset[str]) -> frozenset[str]:
    return frozenset(
        token for token in re.findall(r"[A-Za-z][A-Za-z_-]+", str(text).lower())
        if len(token) >= min_length and token not in stop
    )


def _validate_program(program: Mapping[str, Any]) -> None:
    if program.get("schema") != "Venus.StateOwnedRelationTraceSearch.v0.1":
        raise RelationTraceError("unsupported relation-trace program")
    if program.get("future_return_input") is not False:
        raise RelationTraceError("future return may not enter relation-trace search")
    if program.get("hidden_evaluation_input") is not False:
        raise RelationTraceError("hidden evaluation may not enter relation-trace search")
    configs=tuple(program.get("candidate_configs") or ())
    if not configs:
        raise RelationTraceError("candidate configs required")
    ids=set()
    for cfg in configs:
        cid=str(cfg.get("id") or "")
        if not cid or cid in ids:
            raise RelationTraceError("unique candidate config ids required")
        ids.add(cid)
        if int(cfg.get("min_source_support") or 0) < 1:
            raise RelationTraceError("min_source_support must be positive")
        if int(cfg.get("min_anchor_degree") or 0) < 1:
            raise RelationTraceError("min_anchor_degree must be positive")
        if int(cfg.get("max_terms") or 0) < 1:
            raise RelationTraceError("max_terms must be positive")


def _relations(
    program: Mapping[str, Any],
    *,
    anchors: Sequence[str],
    sources: Iterable[Mapping[str, Any]],
) -> tuple[TraceTerm, ...]:
    tok=program.get("tokenization") or {}
    min_length=int(tok.get("min_length") or 3)
    stop=frozenset(str(x).lower() for x in tok.get("stop_terms",()))
    anchor_terms=tuple(dict.fromkeys(
        x for value in anchors
        for x in _tokenize(str(value),min_length=min_length,stop=stop)
    ))
    if not anchor_terms:
        raise RelationTraceError("at least one anchor term required")
    anchor_set=set(anchor_terms)

    stats: dict[str, dict[str, set[str]]] = {}
    title_hits: dict[str,set[str]] = {}
    for row in sources:
        sid=str(row.get("source_id") or "")
        if not sid:
            raise RelationTraceError("source identity required")
        title_tokens=_tokenize(str(row.get("title") or ""),min_length=min_length,stop=stop)
        body_tokens=_tokenize(
            f"{row.get('title') or ''} {row.get('observed_relation') or row.get('summary') or ''}",
            min_length=min_length,stop=stop,
        )
        present_anchors=anchor_set & set(body_tokens)
        for term in body_tokens-anchor_set:
            slot=stats.setdefault(term,{"sources":set(),"anchors":set()})
            slot["sources"].add(sid)
            slot["anchors"].update(present_anchors)
            if term in title_tokens:
                title_hits.setdefault(term,set()).add(sid)

    out=[]
    for term,slot in stats.items():
        sources_=tuple(sorted(slot["sources"]))
        anchors_=tuple(sorted(slot["anchors"]))
        out.append(TraceTerm(
            term=term,
            source_ids=sources_,
            anchor_terms=anchors_,
            source_support=len(sources_),
            anchor_degree=len(anchors_),
            title_support=len(title_hits.get(term,set())),
        ))
    return tuple(sorted(out,key=lambda x:x.term))


def search_relation_trace(
    program: Mapping[str, Any],
    *,
    anchors: Sequence[str],
    sources: Iterable[Mapping[str, Any]],
) -> RelationTrace:
    _validate_program(program)
    rows=_relations(program,anchors=anchors,sources=sources)
    program_digest=digest(program)
    candidates=[]
    for cfg in program["candidate_configs"]:
        kept=[
            row for row in rows
            if row.source_support >= int(cfg["min_source_support"])
            and row.anchor_degree >= int(cfg["min_anchor_degree"])
            and (not bool(cfg.get("require_title_support")) or row.title_support >= 1)
        ]
        kept=sorted(
            kept,
            key=lambda row:(-row.anchor_degree,-row.source_support,-row.title_support,row.term),
        )[:int(cfg["max_terms"])]
        if not kept:
            continue
        score=(
            sum(row.anchor_degree for row in kept),
            sum(row.source_support for row in kept),
            sum(row.title_support for row in kept),
            -len(kept),
        )
        candidates.append((score,str(cfg["id"]),tuple(kept)))

    if not candidates:
        body={
            "schema":"Venus.StateOwnedRelationTrace.v0.1",
            "program_digest":program_digest,
            "config_id":"NONE",
            "anchor_terms":tuple(dict.fromkeys(str(x).lower() for x in anchors if str(x).strip())),
            "terms":(),
            "relations":(),
            "status":"WITHHOLD_NO_RELATION_TRACE_CANDIDATE",
            "future_return_input":False,
            "hidden_evaluation_input":False,
            "promotion_authority":False,
            "truth_authority":False,
        }
        return RelationTrace(trace_id=digest(body),**body)

    best=max(candidates,key=lambda x:(x[0],tuple(-ord(c) for c in x[1])))
    # Deterministic lexical tie-break after numeric score.
    top_score=best[0]
    tied=sorted((cid,kept) for score,cid,kept in candidates if score==top_score)
    cid,kept=tied[0]
    body={
        "schema":"Venus.StateOwnedRelationTrace.v0.1",
        "program_digest":program_digest,
        "config_id":cid,
        "anchor_terms":tuple(dict.fromkeys(str(x).lower() for x in anchors if str(x).strip())),
        "terms":tuple(row.term for row in kept),
        "relations":tuple(kept),
        "status":"RELATION_TRACE_CANDIDATE_FROZEN",
        "future_return_input":False,
        "hidden_evaluation_input":False,
        "promotion_authority":False,
        "truth_authority":False,
    }
    serial={**body,"relations":tuple(asdict(x) for x in kept)}
    return RelationTrace(trace_id=digest(serial),**body)
