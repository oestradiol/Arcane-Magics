#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]


class DidacticExecutionError(ValueError):
    pass


def _execution_envelope_status(result_status: Any) -> str:
    status = str(result_status or "")
    return (
        "EXECUTED_SELECTED_PREFROZEN_CURRICULUM"
        if status.startswith("PASS_BOUNDED_")
        else "WITHHOLD_CURRICULUM_RESULT"
    )


def load(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def selected_prefreeze_paths(cycle: Mapping[str, Any]) -> frozenset[str]:
    study = cycle.get("study")
    if not isinstance(study, Mapping):
        return frozenset()
    return frozenset(str(x) for x in study.get("referenced_repository_paths", ()))


def resolve_selected_curricula(
    cycle: Mapping[str, Any],
    catalog: Mapping[str, Any],
) -> dict[str, Any]:
    referenced = selected_prefreeze_paths(cycle)
    rows = [
        row for row in catalog.get("curricula", ())
        if str(row.get("prefreeze_path")) in referenced
    ]
    if len(rows) > 1:
        return {
            "status": "WITHHOLD_MULTIPLE_SELECTED_CURRICULA",
            "referenced": referenced,
            "rows": (),
        }
    if rows:
        return {"status": "READY", "referenced": referenced, "rows": tuple(rows)}
    unresolved = frozenset(
        path for path in referenced if path.endswith("_PREFREEZE.json")
    )
    if unresolved:
        return {
            "status": "WITHHOLD_SELECTED_PREFREEZE_HAS_NO_EXECUTOR",
            "referenced": referenced,
            "unresolved_prefreezes": unresolved,
            "rows": (),
        }
    return {
        "status": "NO_SELECTED_EXECUTABLE_CURRICULUM",
        "referenced": referenced,
        "rows": (),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycle", required=True)
    ap.add_argument("--catalog", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--envelope-output", required=True)
    args = ap.parse_args()

    cycle = load(args.cycle)
    catalog = load(args.catalog)
    if catalog.get("schema") != "Venus.DidacticCurriculumExecutionCatalog.v0.1":
        raise DidacticExecutionError("unsupported didactic curriculum catalog")
    for key in (
        "autonomy_may_add_curricula",
        "autonomy_may_modify_catalog",
        "target_binding_authority",
        "promotion_authority",
        "truth_authority",
    ):
        if catalog.get(key) is not False:
            raise DidacticExecutionError(f"catalog authority invariant violated: {key}")

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    envelope_path = Path(args.envelope_output)

    if cycle.get("decision") == "STOP":
        envelope = {
            "schema": "Venus.DidacticCurriculumExecutionEnvelope.v0.1",
            "status": "NOT_APPLICABLE_STOP",
            "executed": False,
            "promotion_authority": False,
            "truth_authority": False,
        }
        envelope_path.write_text(json.dumps(envelope, indent=2, sort_keys=True) + "\n")
        return 0

    route = resolve_selected_curricula(cycle, catalog)
    referenced = route["referenced"]
    rows = route["rows"]
    if route["status"] != "READY":
        envelope = {
            "schema": "Venus.DidacticCurriculumExecutionEnvelope.v0.1",
            "status": route["status"],
            "executed": False,
            "selected_referenced_paths": sorted(referenced),
            "unresolved_prefreezes": sorted(route.get("unresolved_prefreezes", ())),
            "promotion_authority": False,
            "truth_authority": False,
        }
        envelope_path.write_text(json.dumps(envelope, indent=2, sort_keys=True) + "\n")
        return 0

    row = rows[0]
    module_name = str(row["module"])
    if not module_name.startswith("kernel.development."):
        raise DidacticExecutionError("curriculum module must remain in developmental namespace")
    module = importlib.import_module(module_name)
    if not hasattr(module, "run"):
        raise DidacticExecutionError("curriculum module lacks run()")

    prefreeze_path = ROOT / str(row["prefreeze_path"])
    cases_path = ROOT / str(row["cases_path"])
    candidate, result = module.run(prefreeze_path, cases_path)

    candidate_path = outdir / str(row["candidate_filename"])
    result_path = outdir / str(row["result_filename"])
    candidate_path.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    envelope = {
        "schema": "Venus.DidacticCurriculumExecutionEnvelope.v0.1",
        "status": _execution_envelope_status(result.get("status")),
        "executed": True,
        "curriculum_id": row["curriculum_id"],
        "prefreeze_path": row["prefreeze_path"],
        "candidate_filename": candidate_path.name,
        "result_filename": result_path.name,
        "result_status": result.get("status"),
        "independent_evaluation": False,
        "promotion_authority": False,
        "truth_authority": False,
    }
    envelope_path.write_text(json.dumps(envelope, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
