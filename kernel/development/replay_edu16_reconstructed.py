#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "kernel" / "development" / "EDU16_RECONSTRUCTED_CARRIER_MANIFEST.json"
STATE = ROOT / "kernel" / "development" / "EDU16_RECONSTRUCTED_STATE.json"
POLICY = ROOT / "provenance" / "developmental" / "EDU" / "EDU16_LEARNER_GENERATED_WORLD_FEED_POLICY.json"


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def source_vector_sha256(manifest: dict[str, Any]) -> str:
    payload = "".join(
        f"{source['path']}\0{source['git_blob_sha']}\n"
        for source in manifest["sources"]
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def canonical_state_sha256(state: dict[str, Any]) -> str:
    payload = json.dumps(
        state,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def parse_receipt(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    verdict = re.search(r"\*\*Verdict:\*\*\s*`([^`]+)`", text)
    records = re.search(r"(?mi)^\s*records\s+(\d+)\s*$", text)
    head = re.search(r"(?mi)^\s*head\s+([0-9a-f]{64})\s*$", text)
    sha256 = re.search(r"(?mi)^\s*sha256\s+([0-9a-f]{64})\s*$", text)
    missing = [
        name
        for name, match in (
            ("verdict", verdict),
            ("records", records),
            ("head", head),
            ("sha256", sha256),
        )
        if match is None
    ]
    if missing:
        raise ValueError(f"{path}: missing receipt fields: {', '.join(missing)}")
    return {
        "records": int(records.group(1)),
        "head": head.group(1),
        "sha256": sha256.group(1),
        "verdict": verdict.group(1),
    }


def verify_source_custody(manifest: dict[str, Any], root: Path = ROOT) -> None:
    for source in manifest["sources"]:
        path = root / source["path"]
        if not path.exists():
            raise ValueError(f"missing reconstructed-carrier source: {source['path']}")
        actual = git_blob_sha(path)
        expected = source["git_blob_sha"]
        if actual != expected:
            raise ValueError(
                f"source custody mismatch for {source['path']}: "
                f"expected {expected}, got {actual}"
            )
    actual_vector = source_vector_sha256(manifest)
    if actual_vector != manifest["source_vector_sha256"]:
        raise ValueError(
            "source-vector mismatch: "
            f"expected {manifest['source_vector_sha256']}, got {actual_vector}"
        )


def verify_checkpoints(manifest: dict[str, Any], root: Path = ROOT) -> None:
    previous_records = -1
    for checkpoint in manifest["checkpoints"]:
        parsed = parse_receipt(root / checkpoint["result_path"])
        for key in ("records", "head", "sha256", "verdict"):
            if parsed[key] != checkpoint[key]:
                raise ValueError(
                    f"{checkpoint['id']} {key} mismatch: "
                    f"expected {checkpoint[key]!r}, got {parsed[key]!r}"
                )
        if checkpoint["records"] <= previous_records:
            raise ValueError("reconstructed checkpoint record counts are not increasing")
        previous_records = checkpoint["records"]


def verify_policy(policy: dict[str, Any]) -> None:
    if policy.get("schema") != "Venus.EDU16LearnerOwnedFeedPolicy.v1":
        raise ValueError("unexpected EDU16 policy schema")
    if policy.get("selected_internalization_target") != "WORLD_FEED_SAMPLING_POLICY":
        raise ValueError("EDU16 policy internalization target drift")
    if policy.get("selected_source_families") != ["AGRI", "COMPUTING", "HEALTH", "LABOR"]:
        raise ValueError("EDU16 selected source-family set drift")
    if [q.get("id") for q in policy.get("generated_queries", [])] != [
        "AGRI",
        "COMPUTING",
        "HEALTH",
        "LABOR",
    ]:
        raise ValueError("EDU16 generated query order drift")
    if policy.get("world_execution_owner") != "EXTERNAL_WORLD_INTERFACE":
        raise ValueError("World execution externality lost")
    if policy.get("evaluation_owner") != "INDEPENDENT_EVALUATOR":
        raise ValueError("independent evaluation boundary lost")
    if any(policy.get("claim_fence", {}).values()):
        raise ValueError("EDU16 broad claim fence must remain false")


def reconstruct_state(
    manifest: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    checkpoints = [
        {
            "head": checkpoint["head"],
            "id": checkpoint["id"],
            "records": checkpoint["records"],
            "sha256": checkpoint["sha256"],
            "verdict": checkpoint["verdict"],
        }
        for checkpoint in manifest["checkpoints"]
    ]
    return {
        "carrier_id": "EDU16-RC1",
        "checkpoints": checkpoints,
        "claim_fence": dict(policy["claim_fence"]),
        "external": [
            "World interface execution",
            "independent evaluation",
            "authorization beyond admitted interface scope",
        ],
        "historical_equivalence": {
            "authority_id": "EDU16",
            "event_level_journal_equivalent": False,
            "original_journal_recovered": False,
            "original_runner_recovered": False,
            "record_count": 1703,
        },
        "owned": [
            "curriculum target selection",
            "curriculum gate proposal",
            "open-domain problem selection",
            "research-question formation",
            "evidence role/budget",
            "research-obligation routing",
            "World-feed sampling/query policy",
        ],
        "promotion_authority": False,
        "replay_kind": "DETERMINISTIC_CLAIM_BEARING_STATE_RECONSTRUCTION",
        "runtime_base": {
            "exact_git_checkpoint": True,
            "id": "IG10",
        },
        "schema": "Venus.EDU16ReconstructedCarrierState.v0.1",
        "source_vector_sha256": manifest["source_vector_sha256"],
        "world_feed_policy": {
            "evaluation_owner": policy["evaluation_owner"],
            "schema": policy["schema"],
            "selected_internalization_target": policy["selected_internalization_target"],
            "selected_source_families": policy["selected_source_families"],
            "stop_rule": policy["stop_rule"],
            "world_execution_owner": policy["world_execution_owner"],
        },
    }


def replay(root: Path = ROOT) -> tuple[dict[str, Any], str]:
    manifest = json.loads(
        (root / MANIFEST.relative_to(ROOT)).read_text(encoding="utf-8")
    )
    if manifest.get("carrier_id") != "EDU16-RC1":
        raise ValueError("unexpected reconstructed carrier id")
    if manifest.get("historical_event_replay") is not False:
        raise ValueError("reconstructed carrier may not claim historical event replay")
    if manifest.get("original_runner_recovered") is not False:
        raise ValueError("reconstructed carrier may not claim original runner recovery")
    if manifest.get("original_journal_recovered") is not False:
        raise ValueError("reconstructed carrier may not claim original journal recovery")

    verify_source_custody(manifest, root)
    verify_checkpoints(manifest, root)

    policy = json.loads((root / POLICY.relative_to(ROOT)).read_text(encoding="utf-8"))
    verify_policy(policy)

    state = reconstruct_state(manifest, policy)
    digest = canonical_state_sha256(state)
    if digest != manifest["expected_reconstructed_state_sha256"]:
        raise ValueError(
            "reconstructed state digest mismatch: "
            f"expected {manifest['expected_reconstructed_state_sha256']}, got {digest}"
        )

    committed = json.loads((root / STATE.relative_to(ROOT)).read_text(encoding="utf-8"))
    if committed != state:
        raise ValueError("committed EDU16 reconstructed state differs from replay output")
    return state, digest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replay the EDU16-RC1 claim-bearing state from content-addressed recovered inputs."
    )
    parser.add_argument("--emit-state", action="store_true")
    args = parser.parse_args()
    try:
        state, digest = replay()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2, sort_keys=True))
        return 1

    result = {
        "status": "PASS_RECONSTRUCTED_CLAIM_BEARING_STATE",
        "carrier_id": state["carrier_id"],
        "state_sha256": digest,
        "historical_event_replay": False,
        "promotion_authority": False,
    }
    if args.emit_state:
        result["state"] = state
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
