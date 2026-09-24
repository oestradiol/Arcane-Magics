#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "kernel" / "custody" / "EDU16_CUSTODY_STATUS.json"
REPLAY = ROOT / "kernel" / "development" / "replay_edu16_reconstructed.py"


def load_replay_module():
    spec = importlib.util.spec_from_file_location("edu16_reconstructed_replay", REPLAY)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> int:
    data = json.loads(STATUS.read_text(encoding="utf-8"))
    errors = []
    auth = data["authority"]
    current = (ROOT / "kernel" / "CURRENT_STATE.md").read_text(
        encoding="utf-8", errors="replace"
    )
    receipt = (
        ROOT
        / "provenance"
        / "developmental"
        / "EDU"
        / "EDU16_WORLD_FEED_SAMPLING_POLICY_RESULT.md"
    ).read_text(encoding="utf-8", errors="replace")

    for token in (str(auth["records"]), auth["head"], auth["sha256"], auth["verdict"]):
        if token not in current:
            errors.append("CURRENT_STATE missing EDU16 custody token: " + token)
        if token not in receipt:
            errors.append("EDU16 receipt missing custody token: " + token)

    exe = data["executable_custody"]
    if exe.get("git_replayable_runtime") is not False:
        errors.append("historical EDU16 runtime may not be marked Git-replayable without exact runner/journal custody")
    if exe.get("exact_1703_event_runner_located") is not False:
        errors.append("historical EDU16 runner recovery was not established")
    if exe.get("exact_1703_event_journal_located") is not False:
        errors.append("historical EDU16 journal recovery was not established")

    rc = data.get("reconstructed_carrier", {})
    if rc.get("id") != "EDU16-RC1":
        errors.append("missing EDU16-RC1 reconstructed carrier identity")
    if rc.get("git_replayable_claim_state") is not True:
        errors.append("EDU16-RC1 must be Git-replayable at claim-bearing-state scope")
    if rc.get("exact_historical_event_replay") is not False:
        errors.append("EDU16-RC1 may not claim exact historical event replay")
    if rc.get("successor_use") != "PROSPECTIVE_REIMPLEMENTATION_PARENT_ONLY":
        errors.append("EDU16-RC1 successor-use boundary drift")

    if data["runtime_base"].get("id") != "IG10" or data["runtime_base"].get("git_reconstructible") is not True:
        errors.append("IG10 replayable runtime base boundary lost")

    recovery = ROOT / data["evidence_custody"]["recovery_manifest"]
    if not recovery.exists():
        errors.append("recovery manifest missing")

    for key in ("manifest", "replay", "state"):
        path = rc.get(key)
        if not path or not (ROOT / path).exists():
            errors.append(f"EDU16-RC1 missing {key}: {path!r}")

    if not errors:
        try:
            module = load_replay_module()
            state, digest = module.replay()
            if state.get("carrier_id") != "EDU16-RC1":
                errors.append("EDU16-RC1 replay returned wrong carrier id")
            if digest != rc.get("reconstructed_state_sha256"):
                errors.append("EDU16-RC1 reconstructed-state digest mismatch")
            if state.get("historical_equivalence", {}).get("event_level_journal_equivalent") is not False:
                errors.append("EDU16-RC1 replay collapsed reconstructed state into historical event replay")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append("EDU16-RC1 replay failed: " + str(exc))

    if errors:
        print("EDU16 CUSTODY BOUNDARY FAIL")
        for error in errors:
            print("- " + error)
        return 1

    print(
        "EDU16 CUSTODY BOUNDARY PASS: exact historical evidence preserved; "
        "historical event replay remains unavailable; EDU16-RC1 reconstructs "
        "the claim-bearing developmental state deterministically"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
