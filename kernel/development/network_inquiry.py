from __future__ import annotations

"""Generic learner-side network inquiry custody.

This module does not browse the Web. It:
- renders a bounded query from an already learner-formed problem;
- accepts externally executed Web encounters as inert provenance-bearing data;
- stores those encounters in VenusMemory;
- reconstructs a later inquiry context from retained network memory.

Query execution remains an external adapter action. Returned pages are encounter
material, not truth or independent evaluation.
"""

from dataclasses import asdict, dataclass
import re
from typing import Any, Iterable, Mapping, Sequence

from kernel.runtime.memory import VenusMemory
from kernel.runtime.vmk2 import digest


class NetworkInquiryError(ValueError):
    pass


STUDY_QUERY_STOP = frozenset({
    "about", "after", "before", "deeper", "from", "into", "issue", "kernel",
    "minerva", "problem", "recover", "required", "requires", "returned",
    "selected", "split", "test", "tests", "that", "this", "with", "without",
})

NETWORK_MEMORY_STOP = STUDY_QUERY_STOP | frozenset({
    "also", "been", "being", "does", "each", "have", "more", "only", "other",
    "over", "same", "some", "such", "than", "their", "there", "these", "they",
    "using", "were", "when", "where", "which", "will", "would", "github",
})


def study_query_terms(study: Mapping[str, Any], *, limit: int = 12) -> tuple[str, ...]:
    """Extract bounded inert lexical cues from a learner-selected study.

    The study text remains untrusted external material. This helper never
    executes it, grants it truth, or treats issue/carrier identity as a semantic
    answer. It only lets the learner's already-selected study constrain what
    the external network adapter is asked to search for.
    """
    if limit < 1:
        raise NetworkInquiryError("study query term limit must be positive")
    parts = [
        str(study.get("target_title") or ""),
        *[str(x) for x in study.get("returned_blocker_sentences", ())],
    ]
    out: list[str] = []
    for part in parts:
        for token in re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)?", part.lower()):
            if len(token) < 3 or token in STUDY_QUERY_STOP or token in out:
                continue
            out.append(token)
            if len(out) >= limit:
                return tuple(out)
    return tuple(out)


def study_context_digest(study: Mapping[str, Any]) -> str:
    """Bind the selected study context as provenance, not as truth authority."""
    body = {
        "target_kind": str(study.get("target_kind") or ""),
        "target_number": int(study.get("target_number") or 0),
        "target_title": str(study.get("target_title") or ""),
        "method": str(study.get("method") or ""),
        "returned_blocker_sentences": tuple(
            str(x) for x in study.get("returned_blocker_sentences", ())
        ),
        "referenced_repository_paths": tuple(
            str(x) for x in study.get("referenced_repository_paths", ())
        ),
    }
    return digest(body)


@dataclass(frozen=True)
class NetworkQuery:
    schema: str
    query_id: str
    problem_id: str
    query_text: str
    residual_coordinates: tuple[str, ...]
    discriminator: str
    provenance_ids: tuple[str, ...]
    study_context_digest: str | None = None
    study_terms: tuple[str, ...] = ()
    authorship: str = "LEARNER_DERIVED_FROM_FORMED_PROBLEM"
    execution_owner: str = "EXTERNAL_ADAPTER"
    promotion_authority: bool = False
    truth_authority: bool = False


@dataclass(frozen=True)
class NetworkExecutionContext:
    schema: str
    context_id: str
    query_id: str
    source_locators: tuple[str, ...]
    carrier_keys: tuple[str, ...]
    role: str = "ADAPTER_ROUTING_CONTEXT_ONLY"
    target_selection_authority: bool = False
    truth_authority: bool = False
    promotion_authority: bool = False


@dataclass(frozen=True)
class WebEncounter:
    source_id: str
    source_url: str
    source_date: str
    retrieved_at: str
    title: str
    summary: str
    adapter_id: str


@dataclass(frozen=True)
class NetworkReconstruction:
    schema: str
    reconstruction_id: str
    problem_id: str
    query_id: str
    memory_object_ids: tuple[str, ...]
    indexed_source_ids: tuple[str, ...]
    changed_by_network_memory: bool
    next_query_terms: tuple[str, ...]
    promotion_authority: bool = False


def _tokens(value: str) -> tuple[str, ...]:
    """Generic lexical terms for returned-network reconstruction.

    Numeric ids, hashes, and punctuation-heavy artifacts are deliberately
    excluded: persistent memory must change inquiry through lexical relation
    cues, not through accidental issue numbers or object identifiers.
    """
    out: list[str] = []
    for token in re.findall(r"[A-Za-z][A-Za-z_-]{2,}", value.lower()):
        if token in NETWORK_MEMORY_STOP or token in out:
            continue
        out.append(token)
    return tuple(out)


def form_network_query(
    problem: Mapping[str, Any],
    *,
    study: Mapping[str, Any] | None = None,
) -> NetworkQuery:
    disposition = str(problem.get("disposition") or "")
    if disposition not in {
        "FORMED_BOUNDED_PROBLEM",
        "FORMED_STANDING_DEVELOPMENTAL_PROBLEM",
    }:
        raise NetworkInquiryError("network inquiry requires a formed problem")

    problem_id = str(problem.get("problem_id") or "")
    residuals = tuple(str(x) for x in problem.get("residual_coordinates", ()))
    discriminator = str(problem.get("discriminator") or "")
    provenance = tuple(str(x) for x in problem.get("source_stream_ids", ()))
    if not problem_id or not residuals or not discriminator or not provenance:
        raise NetworkInquiryError(
            "problem id, residual coordinates, discriminator, and provenance required"
        )

    # Generic rendering only. A learner-selected study may contribute bounded
    # lexical cues, but no issue text is executed or promoted into an answer.
    base_terms = (
        discriminator.replace("_", " ").lower(),
        *[r.replace("_", " ").lower() for r in residuals],
    )
    study_digest: str | None = None
    terms: tuple[str, ...] = ()
    authorship = "LEARNER_DERIVED_FROM_FORMED_PROBLEM"
    if study is not None:
        terms = study_query_terms(study)
        if terms:
            query_text = " ".join((*terms, *base_terms))
            study_digest = study_context_digest(study)
            provenance = provenance + (f"selected-study:{study_digest}",)
            authorship = "LEARNER_DERIVED_FROM_SELECTED_STUDY"
        else:
            query_text = " ".join(base_terms)
    else:
        query_text = " ".join(base_terms)

    body = {
        "schema": "Venus.NetworkQuery.v0.1",
        "problem_id": problem_id,
        "query_text": query_text,
        "residual_coordinates": residuals,
        "discriminator": discriminator,
        "provenance_ids": provenance,
        "study_context_digest": study_digest,
        "study_terms": terms,
        "authorship": authorship,
        "execution_owner": "EXTERNAL_ADAPTER",
        "promotion_authority": False,
        "truth_authority": False,
    }
    return NetworkQuery(query_id=digest(body), **body)


def bind_web_encounters(
    memory: VenusMemory,
    *,
    query: NetworkQuery,
    encounters: Iterable[WebEncounter],
) -> tuple[str, ...]:
    rows = tuple(encounters)
    if not rows:
        raise NetworkInquiryError("at least one external Web encounter required")

    source_ids = [row.source_id for row in rows]
    if any(not x for x in source_ids) or len(source_ids) != len(set(source_ids)):
        raise NetworkInquiryError("Web encounter source identities must be unique and nonempty")

    object_ids = []
    for row in rows:
        if not row.source_url or not row.retrieved_at or not row.adapter_id:
            raise NetworkInquiryError("source URL, retrieval time, and adapter identity required")
        payload = {
            **asdict(row),
            "query_id": query.query_id,
            "return_class": "ENCOUNTER_RETURN",
            "truth_authority": False,
            "evaluation_authority": False,
        }
        object_ids.append(
            memory.put(
                "NETWORK_ENCOUNTER",
                payload,
                provenance=(
                    f"query:{query.query_id}",
                    f"source:{row.source_id}",
                    f"adapter:{row.adapter_id}",
                ),
                scope="WWW_MIND_BOUNDED_STUDY",
                labels=("network", "web", "encounter-return"),
                status="ACTIVE",
            )
        )
    return tuple(object_ids)


def reconstruct_from_network(
    memory: VenusMemory,
    *,
    problem: Mapping[str, Any],
    query: NetworkQuery,
    memory_object_ids: Sequence[str],
) -> NetworkReconstruction:
    if not memory_object_ids:
        raise NetworkInquiryError("network reconstruction requires retained memory")

    source_ids = []
    observed_terms: set[str] = set()
    for object_id in memory_object_ids:
        obj = memory.get(object_id)
        if obj.kind != "NETWORK_ENCOUNTER":
            raise NetworkInquiryError("non-network object supplied to network reconstruction")
        payload = obj.payload
        if str(payload.get("query_id") or "") != query.query_id:
            raise NetworkInquiryError("network memory query identity mismatch")
        if str(payload.get("return_class") or "") != "ENCOUNTER_RETURN":
            raise NetworkInquiryError("Web material cannot be retyped as evaluative return")
        source_id = str(payload.get("source_id") or "")
        if not source_id:
            raise NetworkInquiryError("indexed source identity required")
        source_ids.append(source_id)
        observed_terms.update(_tokens(str(payload.get("title") or "")))
        observed_terms.update(_tokens(str(payload.get("summary") or "")))

    base_terms = set(_tokens(query.query_text))
    new_terms = tuple(sorted(observed_terms - base_terms))[:12]
    changed = bool(new_terms)
    body = {
        "schema": "Venus.NetworkReconstruction.v0.1",
        "problem_id": str(problem["problem_id"]),
        "query_id": query.query_id,
        "memory_object_ids": tuple(memory_object_ids),
        "indexed_source_ids": tuple(sorted(source_ids)),
        "changed_by_network_memory": changed,
        "next_query_terms": new_terms,
        "promotion_authority": False,
    }
    return NetworkReconstruction(
        reconstruction_id=digest(body),
        **body,
    )


def form_followup_network_query(
    *,
    prior_query: NetworkQuery,
    reconstruction: NetworkReconstruction,
) -> NetworkQuery:
    """Derive a successor query from retained network memory.

    This is the causal memory test: removing the returned memory terms must
    change the successor query identity/text. The external adapter still owns
    execution and the query still carries no truth/promotion authority.
    """
    if reconstruction.query_id != prior_query.query_id:
        raise NetworkInquiryError("reconstruction/prior-query identity mismatch")
    if not reconstruction.changed_by_network_memory:
        raise NetworkInquiryError("no returned network-memory change to compile into follow-up")
    terms = tuple(str(x) for x in reconstruction.next_query_terms if str(x).strip())
    if not terms:
        raise NetworkInquiryError("follow-up query requires retained network terms")

    anchors = tuple(prior_query.study_terms[:3])
    if anchors:
        # Make returned memory causally affect the *executed* search variants,
        # while retaining enough selected-study context to avoid topic drift.
        query_text = " ".join((*anchors, *terms[:6])).strip()
    else:
        query_text = " ".join(
            (
                prior_query.discriminator.replace("_", " ").lower(),
                " ".join(terms),
            )
        ).strip()
    body = {
        "schema": "Venus.NetworkQuery.v0.1",
        "problem_id": prior_query.problem_id,
        "query_text": query_text,
        "residual_coordinates": prior_query.residual_coordinates,
        "discriminator": prior_query.discriminator,
        "provenance_ids": tuple(prior_query.provenance_ids)
            + tuple(f"network-memory:{x}" for x in reconstruction.memory_object_ids),
        "study_context_digest": prior_query.study_context_digest,
        "study_terms": prior_query.study_terms,
        "authorship": "LEARNER_DERIVED_FROM_NETWORK_RECONSTRUCTION",
        "execution_owner": "EXTERNAL_ADAPTER",
        "promotion_authority": False,
        "truth_authority": False,
    }
    return NetworkQuery(query_id=digest(body), **body)


def bind_network_execution_context(
    *,
    query: NetworkQuery,
    carrier_keys: Iterable[tuple[str, int]],
    repository_full_name: str,
) -> NetworkExecutionContext:
    """Bind nonsemantic adapter locators after problem/query formation.

    Carrier location can route the external adapter but may not change the
    learner's problem, query identity, truth status, or target-selection law.
    """
    repo = str(repository_full_name).strip()
    keys = tuple(sorted((str(kind), int(number)) for kind, number in carrier_keys))
    if not repo or not keys:
        raise NetworkInquiryError("execution context requires repository and bound carrier")
    locators = tuple(
        f"https://github.com/{repo}/" + ("pull/" if kind == "PR" else "issues/") + str(number)
        for kind, number in keys
    )
    body = {
        "schema": "Venus.NetworkExecutionContext.v0.1",
        "query_id": query.query_id,
        "source_locators": locators,
        "carrier_keys": tuple(f"{kind}:{number}" for kind, number in keys),
        "role": "ADAPTER_ROUTING_CONTEXT_ONLY",
        "target_selection_authority": False,
        "truth_authority": False,
        "promotion_authority": False,
    }
    return NetworkExecutionContext(context_id=digest(body), **body)
