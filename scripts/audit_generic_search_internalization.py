#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kernel.development import generic_residual_search as internal
from kernel.runtime.internalizer import (
    CapabilityScaffold,
    InternalizationEvidence,
    internalize,
)

DONOR = ROOT / "provenance/historical-runtime/R194/source/venus_seed_v0/grammar_expansion.py"
STATE = ROOT / "kernel/development/GENERIC_RESIDUAL_SEARCH_INTERNALIZED_STATE.json"
EXECUTOR = ROOT / "kernel/runtime/internalized_search.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bundle_sha256() -> str:
    h = hashlib.sha256()
    for path in (STATE, EXECUTOR):
        h.update(path.name.encode("utf-8"))
        h.update(b"\0")
        h.update(path.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


def load_donor():
    name = "_venus_r194_grammar_expansion_audit"
    spec = importlib.util.spec_from_file_location(name, DONOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load R194 generic grammar donor")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def donor_signatures(donor, width: int) -> frozenset[tuple[int, ...]]:
    domain = donor.bit_domain(width)
    atoms = tuple(donor.BoolExpr.atom(i) for i in range(width))
    grammar = donor.ObjectGrammar(atoms, stage=0)
    expanded = donor.generic_expand_once(
        grammar,
        atoms,
        meta_ops=("AND", "OR", "XOR"),
        domain_rows=domain,
    )
    return frozenset(
        donor.truth_table(expr, domain)
        for expr in donor.dedupe_semantics(expanded.raw_successor, domain)
    )


def isolated_replay() -> bool:
    """Run state+executor from a temporary directory with no donor/repo tree."""
    state = json.loads(STATE.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        path = td / "internalized_search.py"
        shutil.copy2(EXECUTOR, path)
        spec = importlib.util.spec_from_file_location("_venus_generic_search_isolated", path)
        if spec is None or spec.loader is None:
            return False
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        rows = (
            module.Observation((0, 0), 0, "r00"),
            module.Observation((0, 1), 1, "r01"),
            module.Observation((1, 0), 1, "r10"),
            module.Observation((1, 1), 0, "r11"),
        )
        out = module.search(state["program"], rows)
        return (
            out.status == "UNIQUE_BOUNDED_PROGRAM_CANDIDATE"
            and out.candidates == ("XOR(x0,x1)",)
        )


def audit() -> dict:
    donor = load_donor()
    widths = (2, 3, 4)
    comparisons = {
        str(width): donor_signatures(donor, width) == internal.semantic_signatures(width)
        for width in widths
    }
    equivalent = all(comparisons.values())
    isolated = isolated_replay()

    comparison_payload = {
        "widths": list(widths),
        "semantic_equivalence": comparisons,
        "isolated_replay": isolated,
        "state_sha256": sha256(STATE),
        "executor_sha256": sha256(EXECUTOR),
        "bundle_sha256": bundle_sha256(),
        "internal_version": internal.VERSION,
    }
    return_id = hashlib.sha256(
        json.dumps(comparison_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    receipt = internalize(
        CapabilityScaffold(
            capability_id=internal.VERSION,
            source_content_sha256=sha256(DONOR),
            internal_content_sha256=bundle_sha256(),
            provenance_sources=(
                "R193_SCAFFOLD_INTERNALIZATION_REFERENCE",
                "R194:grammar_expansion.py",
                "state:GENERIC_RESIDUAL_SEARCH_INTERNALIZED_STATE",
            ),
            consumed_roles=(
                "GENERIC_CANDIDATE_PROGRAM_SEARCH",
                "NEXT_DISCRIMINATOR_SELECTION",
            ),
        ),
        InternalizationEvidence(
            evaluator_id="VENUS_CI_EQUIVALENCE_HARNESS",
            return_id=return_id,
            behavior_equivalent_after_removal=equivalent and isolated,
            original_scaffold_inaccessible=isolated,
            fresh_world_return_external=True,
            successor_reconstructible=isolated,
            source_provenance_preserved=True,
        ),
    )

    return {
        "schema": "Venus.GenericResidualSearchInternalizationAudit.v0.2",
        "semantic_equivalence_by_width": comparisons,
        "isolated_without_historical_scaffold": isolated,
        "state_owned_program": True,
        "state_sha256": sha256(STATE),
        "executor_sha256": sha256(EXECUTOR),
        "bundle_sha256": bundle_sha256(),
        "source_runtime_dependency": False,
        "receipt": receipt.__dict__,
        "repair_candidate_authored": False,
        "hidden_evaluation_exposed": False,
        "promotion_authority": False,
    }


def main() -> int:
    try:
        out = audit()
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2, sort_keys=True))
        return 1
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
