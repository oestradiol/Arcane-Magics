from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
DONOR = (
    ROOT
    / "provenance"
    / "historical-runtime"
    / "R194"
    / "source"
    / "venus_seed_v0"
    / "grammar_expansion.py"
)
EXPECTED_DONOR_GIT_BLOB_SHA = "cd2c041c2a67b686da218fa91684a2d979d8fe3b"
VERSION = "RECONSTRUCTED_GENERIC_RESIDUAL_SEARCH_v0.2"


class RecursiveProposalError(ValueError):
    pass


@dataclass(frozen=True)
class ResidualObservation:
    """One returned constraint on a generic binary decision program.

    Feature coordinates are opaque to this search operator. Their meaning belongs
    to the caller's already-admitted representation and provenance. This module
    never receives issue labels, semantic target names, or hidden benchmark data.
    """

    features: tuple[int, ...]
    desired_action: int
    provenance_id: str


@dataclass(frozen=True)
class SearchOutcome:
    schema: str
    version: str
    status: str
    donor_git_blob_sha: str
    observation_count: int
    feature_count: int
    exact_semantic_candidates: tuple[str, ...]
    minimal_complexity: tuple[int, int] | None
    next_discriminator: tuple[int, ...] | None
    hidden_evaluation_exposed: bool
    promotion_authority: bool


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def load_donor():
    actual = git_blob_sha(DONOR)
    if actual != EXPECTED_DONOR_GIT_BLOB_SHA:
        raise RecursiveProposalError(
            f"ancestral generic-constructor custody mismatch: expected "
            f"{EXPECTED_DONOR_GIT_BLOB_SHA}, got {actual}"
        )
    name = "_venus_r194_grammar_expansion"
    spec = importlib.util.spec_from_file_location(name, DONOR)
    if spec is None or spec.loader is None:
        raise RecursiveProposalError("cannot load ancestral generic constructor")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _normalize_observations(
    observations: Iterable[ResidualObservation],
) -> tuple[ResidualObservation, ...]:
    rows = tuple(observations)
    if not rows:
        raise RecursiveProposalError("STOP_NO_RETURNED_RESIDUAL_OBSERVATIONS")
    width = len(rows[0].features)
    if width < 2:
        raise RecursiveProposalError("generic search requires at least two feature coordinates")
    for row in rows:
        if len(row.features) != width:
            raise RecursiveProposalError("feature-width mismatch")
        if any(bit not in (0, 1) for bit in row.features):
            raise RecursiveProposalError("features must be binary")
        if row.desired_action not in (0, 1):
            raise RecursiveProposalError("desired_action must be binary")
        if not row.provenance_id:
            raise RecursiveProposalError("returned observation requires provenance")
    return rows


def _candidate_pool(width: int):
    donor = load_donor()
    domain = donor.bit_domain(width)
    atoms = tuple(donor.BoolExpr.atom(i) for i in range(width))
    grammar = donor.ObjectGrammar(atoms, stage=0)
    expanded = donor.generic_expand_once(
        grammar,
        atoms,
        meta_ops=("AND", "OR", "XOR"),
        domain_rows=domain,
    )
    # Compare executable semantics on the complete declared finite domain, not
    # syntax strings. This consumes aliases as gauge before search.
    candidates = donor.dedupe_semantics(expanded.raw_successor, domain)
    return donor, domain, candidates


def _exact_candidates(donor, candidates, rows: tuple[ResidualObservation, ...]):
    obs = tuple((row.features, row.desired_action) for row in rows)
    exact = tuple(expr for expr in candidates if donor.errors(expr, obs) == 0)
    return tuple(sorted(exact, key=lambda e: (e.nodes, e.depth, e.canonical())))


def _choose_discriminator(donor, domain, candidates, observed_rows):
    observed = {row.features for row in observed_rows}
    best = None
    for row in domain:
        if row in observed:
            continue
        outputs = tuple(expr.eval(row) for expr in candidates)
        zeros = outputs.count(0)
        ones = outputs.count(1)
        if zeros == 0 or ones == 0:
            continue
        # Prefer the most balanced split, then deterministic lexical row order.
        score = (max(zeros, ones), -min(zeros, ones), tuple(row))
        if best is None or score < best[0]:
            best = (score, tuple(int(x) for x in row))
    return None if best is None else best[1]


def search(
    observations: Iterable[ResidualObservation],
    *,
    hidden_evaluation_exposed: bool = False,
) -> SearchOutcome:
    """Search a bounded ancestral grammar without issue-specific repair knowledge.

    This operator can propose a program only if returned observations uniquely
    determine one executable semantic candidate in the declared bounded grammar.
    Otherwise it WITHHOLDS and, where possible, returns the next feature vector
    on which surviving candidates disagree.

    It does not decide what feature coordinates *mean*. Constructing a lawful
    feature representation remains a separately owned developmental operation.
    """
    if hidden_evaluation_exposed:
        raise RecursiveProposalError("hidden evaluation may not enter proposal search")

    rows = _normalize_observations(observations)
    width = len(rows[0].features)
    donor, domain, pool = _candidate_pool(width)
    exact = _exact_candidates(donor, pool, rows)

    if not exact:
        return SearchOutcome(
            schema="Venus.GenericResidualSearchOutcome.v0.2",
            version=VERSION,
            status="WITHHOLD_NO_EXPRESSIBLE_CANDIDATE",
            donor_git_blob_sha=EXPECTED_DONOR_GIT_BLOB_SHA,
            observation_count=len(rows),
            feature_count=width,
            exact_semantic_candidates=(),
            minimal_complexity=None,
            next_discriminator=None,
            hidden_evaluation_exposed=False,
            promotion_authority=False,
        )

    canon = tuple(expr.canonical() for expr in exact)
    minimum = min((expr.nodes, expr.depth) for expr in exact)

    if len(exact) == 1:
        return SearchOutcome(
            schema="Venus.GenericResidualSearchOutcome.v0.2",
            version=VERSION,
            status="UNIQUE_BOUNDED_PROGRAM_CANDIDATE",
            donor_git_blob_sha=EXPECTED_DONOR_GIT_BLOB_SHA,
            observation_count=len(rows),
            feature_count=width,
            exact_semantic_candidates=canon,
            minimal_complexity=minimum,
            next_discriminator=None,
            hidden_evaluation_exposed=False,
            promotion_authority=False,
        )

    discriminator = _choose_discriminator(donor, domain, exact, rows)
    return SearchOutcome(
        schema="Venus.GenericResidualSearchOutcome.v0.2",
        version=VERSION,
        status=(
            "WITHHOLD_AMBIGUOUS_CANDIDATES_NEXT_DISCRIMINATOR"
            if discriminator is not None
            else "WITHHOLD_OBSERVATIONALLY_EQUIVALENT_CANDIDATES"
        ),
        donor_git_blob_sha=EXPECTED_DONOR_GIT_BLOB_SHA,
        observation_count=len(rows),
        feature_count=width,
        exact_semantic_candidates=canon,
        minimal_complexity=minimum,
        next_discriminator=discriminator,
        hidden_evaluation_exposed=False,
        promotion_authority=False,
    )


def outcome_dict(outcome: SearchOutcome) -> dict:
    return asdict(outcome)


def main() -> int:
    # No issue-specific residual is embedded here. The command-line entry point
    # exists only as a custody/readiness witness; prospective observations must
    # be supplied by an admitted caller.
    print(
        json.dumps(
            {
                "schema": "Venus.GenericResidualSearchReadiness.v0.2",
                "version": VERSION,
                "donor_git_blob_sha": git_blob_sha(DONOR),
                "expected_donor_git_blob_sha": EXPECTED_DONOR_GIT_BLOB_SHA,
                "issue_specific_residual_embedded": False,
                "candidate_emitted": False,
                "promotion_authority": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
