from __future__ import annotations

"""Prospective bounded SSR-3 cross-family transfer evaluator.

Candidate construction sees only:
- the frozen SSR-2 repair machinery;
- the already frozen transfer pressure parents;
- post-freeze returned failing obligations.

Family-wide gold obligations are loaded only after the candidate patches are
frozen, for external scoring.  No target-specific repair rule is embedded here.
"""

from dataclasses import asdict
import json
from pathlib import Path
from typing import Any

from kernel.runtime.transform_program import TransformProgramError, step
from kernel.runtime.transform_program_multi_repair import search_composed_repairs
from kernel.runtime.transform_program_repair_search import BehavioralTrace
from kernel.runtime.transform_program_successor import ProgramPatch, apply_successor_patch
from kernel.runtime.vmk2 import digest

ROOT = Path(__file__).resolve().parents[2]


def load_json(rel: str) -> dict[str, Any]:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def load_jsonl(rel: str) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in (ROOT / rel).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def traces_for_family(rows: list[dict[str, Any]]) -> tuple[BehavioralTrace, ...]:
    return tuple(
        BehavioralTrace(
            trace_id=str(row["trace_id"]),
            prior_state=str(row["prior_state"]),
            action=str(row["action"]),
            payload=dict(row["payload"]),
            expect_success=bool(row["expect_success"]),
            expected_next_state=(
                None if row.get("expected_next_state") is None
                else str(row["expected_next_state"])
            ),
            provenance_id=str(row["provenance_id"]),
        )
        for row in rows
    )


def patches_from_outcome(outcome) -> tuple[ProgramPatch, ...]:
    return tuple(
        ProgramPatch(
            op=str(item["op"]),
            match_from=item.get("match_from"),
            match_action=item.get("match_action"),
            transition=item.get("transition") or None,
        )
        for item in outcome.selected_patches
    )


def score_program(
    program: dict[str, Any],
    rows: list[dict[str, Any]],
    *,
    state_field: str,
    action_field: str,
    payload_field: str,
) -> tuple[int, int, tuple[str, ...]]:
    correct = 0
    failures: list[str] = []
    for row in rows:
        try:
            receipt = step(
                program,
                state=str(row[state_field]),
                action=str(row[action_field]),
                payload={payload_field: row[payload_field]},
                actor_id="external-ssr3-scorer",
            )
            ok = receipt.next_state == str(row["gold"])
        except TransformProgramError:
            ok = False
        if ok:
            correct += 1
        else:
            failures.append(str(row["id"]))
    return correct, len(rows), tuple(failures)


def direct_host_fix(
    parent: dict[str, Any],
    failure_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    patches: list[ProgramPatch] = []
    existing = {
        (str(x["from"]), str(x["action"]))
        for x in parent.get("transitions", ())
    }
    for row in failure_rows:
        key = (str(row["prior_state"]), str(row["action"]))
        transition = {
            "from": key[0],
            "action": key[1],
            "to": str(row["expected_next_state"]),
            "require": sorted(str(k) for k in row["payload"].keys()),
        }
        patches.append(
            ProgramPatch(
                op=("REPLACE_TRANSITION" if key in existing else "ADD_TRANSITION"),
                match_from=(key[0] if key in existing else None),
                match_action=(key[1] if key in existing else None),
                transition=transition,
            )
        )
    successor, _ = apply_successor_patch(
        parent, patches, author_id="external-direct-host-comparator"
    )
    return successor


def evaluate_family(
    *,
    family_id: str,
    parent_path: str,
    benchmark_path: str,
    failure_rows: list[dict[str, Any]],
    state_field: str,
    action_field: str,
    payload_field: str,
    enabled_ops: tuple[str, ...],
    max_patch_count: int,
) -> dict[str, Any]:
    parent = load_json(parent_path)
    traces = traces_for_family(failure_rows)

    candidate = search_composed_repairs(
        parent,
        traces,
        allowed_patch_ops=enabled_ops,
        max_patch_count=max_patch_count,
    )
    if candidate.status != "UNIQUE_COMPOSED_REPAIR_CANDIDATE":
        return {
            "family_id": family_id,
            "candidate_status": candidate.status,
            "promotion_authority": False,
        }

    successor, successor_receipt = apply_successor_patch(
        parent,
        patches_from_outcome(candidate),
        author_id="venus-ssr2-frozen-composed-repair",
    )

    # Depth-1 ablation uses the exact same traces and operations but removes the
    # SSR-2 composition-depth change.
    ablated = search_composed_repairs(
        parent,
        traces,
        allowed_patch_ops=enabled_ops,
        max_patch_count=1,
    )
    if ablated.status == "UNIQUE_COMPOSED_REPAIR_CANDIDATE":
        ablated_program, _ = apply_successor_patch(
            parent,
            patches_from_outcome(ablated),
            author_id="ssr3-ablation-depth-1",
        )
    else:
        ablated_program = parent

    direct = direct_host_fix(parent, failure_rows)
    benchmark = load_jsonl(benchmark_path)

    parent_score = score_program(
        parent, benchmark,
        state_field=state_field, action_field=action_field, payload_field=payload_field
    )
    successor_score = score_program(
        successor, benchmark,
        state_field=state_field, action_field=action_field, payload_field=payload_field
    )
    ablated_score = score_program(
        ablated_program, benchmark,
        state_field=state_field, action_field=action_field, payload_field=payload_field
    )
    direct_score = score_program(
        direct, benchmark,
        state_field=state_field, action_field=action_field, payload_field=payload_field
    )

    return {
        "family_id": family_id,
        "candidate_status": candidate.status,
        "selected_patches": [dict(x) for x in candidate.selected_patches],
        "candidate_digest": candidate.successor_program_digest,
        "successor_receipt_id": successor_receipt.receipt_id,
        "scores": {
            "P_parent": {
                "correct": parent_score[0],
                "total": parent_score[1],
                "failures": list(parent_score[2]),
            },
            "S_successor": {
                "correct": successor_score[0],
                "total": successor_score[1],
                "failures": list(successor_score[2]),
            },
            "A_depth1_ablation": {
                "correct": ablated_score[0],
                "total": ablated_score[1],
                "failures": list(ablated_score[2]),
                "repair_status": ablated.status,
            },
            "H_direct_host": {
                "correct": direct_score[0],
                "total": direct_score[1],
                "failures": list(direct_score[2]),
            },
        },
        "causal_delta_successor_minus_parent": (
            successor_score[0] / successor_score[1]
            - parent_score[0] / parent_score[1]
        ),
        "causal_delta_successor_minus_ablation": (
            successor_score[0] / successor_score[1]
            - ablated_score[0] / ablated_score[1]
        ),
        "direct_host_gap": (
            successor_score[0] / successor_score[1]
            - direct_score[0] / direct_score[1]
        ),
        "promotion_authority": False,
    }


def run() -> dict[str, Any]:
    prefreeze = load_json(
        "kernel/development/SSR3_CROSS_FAMILY_TRANSFER_PREFREEZE.json"
    )
    returned = load_json(
        "kernel/development/SSR3_CROSS_FAMILY_FAILURE_RETURNS.json"
    )
    successor_params = returned["successor_parameters_unchanged"]
    enabled_ops = tuple(str(x) for x in successor_params["enabled_patch_ops"])
    max_patch_count = int(successor_params["max_patch_count"])

    abstention = evaluate_family(
        family_id="ABSTENTION_42",
        parent_path="kernel/development/SSR3_ABSTENTION_PRESSURE_PROGRAM.json",
        benchmark_path="benchmarks/abstention/dev.jsonl",
        failure_rows=list(returned["families"]["ABSTENTION_42"]),
        state_field="pair",
        action_field="variant",
        payload_field="context",
        enabled_ops=enabled_ops,
        max_patch_count=max_patch_count,
    )
    security = evaluate_family(
        family_id="WORLD_INPUT_SECURITY_43",
        parent_path="kernel/development/SSR3_SECURITY_PRESSURE_PROGRAM.json",
        benchmark_path="benchmarks/world_input_security/dev.jsonl",
        failure_rows=list(returned["families"]["WORLD_INPUT_SECURITY_43"]),
        state_field="channel",
        action_field="attack",
        payload_field="content",
        enabled_ops=enabled_ops,
        max_patch_count=max_patch_count,
    )

    families = (abstention, security)
    pass_cross_family = all(
        row.get("candidate_status") == "UNIQUE_COMPOSED_REPAIR_CANDIDATE"
        and row["scores"]["S_successor"]["correct"] == row["scores"]["S_successor"]["total"]
        and row["causal_delta_successor_minus_parent"] > 0
        and row["causal_delta_successor_minus_ablation"] > 0
        for row in families
    )
    host_matches = all(row.get("direct_host_gap") == 0 for row in families)

    body = {
        "schema": "Venus.SSR3CrossFamilyTransferResult.v0.1",
        "date": "2026-09-24",
        "prefreeze": "kernel/development/SSR3_CROSS_FAMILY_TRANSFER_PREFREEZE.json",
        "postfreeze_return": "kernel/development/SSR3_CROSS_FAMILY_FAILURE_RETURNS.json",
        "repair_machinery_unchanged": successor_params,
        "families": {
            row["family_id"]: row for row in families
        },
        "disposition": (
            "PASS_BOUNDED_SSR3_CROSS_FAMILY_TRANSFER"
            if pass_cross_family
            else "WITHHOLD_SSR3_CROSS_FAMILY_TRANSFER"
        ),
        "mechanism_uniqueness": (
            "MATURE_REDUCED_AGAINST_DIRECT_HOST"
            if pass_cross_family and host_matches
            else "NOT_EARNED"
        ),
        "target_specific_retraining": False,
        "hidden_benchmark_claim": False,
        "promotion_authority": False,
        "claim_fence": (
            "This result is bounded to two public declarative policy carriers under the "
            "prefrozen synthetic corruption protocol. It does not establish semantic mastery, "
            "hidden-benchmark performance, general transfer, AGI, or open-ended RSI."
        ),
    }
    body["result_digest"] = digest(body)
    return body


def main() -> int:
    out = run()
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if out["disposition"] == "PASS_BOUNDED_SSR3_CROSS_FAMILY_TRANSFER" else 1


if __name__ == "__main__":
    raise SystemExit(main())
