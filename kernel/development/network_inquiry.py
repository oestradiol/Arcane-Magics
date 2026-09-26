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


@dataclass(frozen=True)
class NetworkQuery:
    schema: str
    query_id: str
    problem_id: str
    query_text: str
    residual_coordinates: tuple[str, ...]
    discriminator: str
    provenance_ids: tuple[str, ...]
    authorship: str = "LEARNER_DERIVED_FROM_FORMED_PROBLEM"
    execution_owner: str = "EXTERNAL_ADAPTER"
    promotion_authority: bool = False
    truth_authority: bool = False


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
    return tuple(
        token.lower()
        for token in re.findall(r"[A-Za-z0-9_]+", value)
        if len(token) > 2
    )


def form_network_query(problem: Mapping[str, Any]) -> NetworkQuery:
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

    # Generic rendering only. No domain answer or target label is injected here.
    # The semantic content comes entirely from the learner-formed problem state.
    query_text = " ".join(
        (
            discriminator.replace("_", " ").lower(),
            *[r.replace("_", " ").lower() for r in residuals],
        )
    )
    body = {
        "schema": "Venus.NetworkQuery.v0.1",
        "problem_id": problem_id,
        "query_text": query_text,
        "residual_coordinates": residuals,
        "discriminator": discriminator,
        "provenance_ids": provenance,
        "authorship": "LEARNER_DERIVED_FROM_FORMED_PROBLEM",
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
