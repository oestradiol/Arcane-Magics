from __future__ import annotations

"""Evaluate the prefrozen Root situated-interface membrane.

This is a structural verifier over an externally produced Pages artifact and
its exact source carrier. It cannot mint repository authority, action
authorization, truth, promotion, broader World participation, AGI, or
consciousness.
"""

import argparse
import json
from pathlib import Path


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--prefreeze",required=True)
    p.add_argument("--prefreeze-commit",required=True)
    p.add_argument("--lain-result",required=True)
    p.add_argument("--pages-snapshot",required=True)
    p.add_argument("--site-index",required=True)
    p.add_argument("--site-app",required=True)
    p.add_argument("--pages-workflow",required=True)
    p.add_argument("--build-observation",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()

    pre=load_json(args.prefreeze)
    lain=load_json(args.lain_result)
    snap=load_json(args.pages_snapshot)
    obs=load_json(args.build_observation)
    html=Path(args.site_index).read_text(encoding="utf-8")
    app=Path(args.site_app).read_text(encoding="utf-8")
    workflow=Path(args.pages_workflow).read_text(encoding="utf-8")

    layers=tuple(snap.get("layers",()))
    ids={str(x.get("id") or "") for x in layers}
    root=next((x for x in layers if x.get("id")=="root"),{})
    all_layer_fields=all(
        all(layer.get(k) for k in ("branch","commit","boundary","residual","reopening","url"))
        for layer in layers
    )

    forbidden_client=(
        "Authorization",
        "Bearer ",
        "api.github.com/repos/",
        "method: 'POST'",
        'method: "POST"',
        "method: 'PUT'",
        'method: "PUT"',
        "method: 'PATCH'",
        'method: "PATCH"',
        "method: 'DELETE'",
        'method: "DELETE"',
    )
    client_has_privileged_write=any(x in app or x in html for x in forbidden_client)

    controls=(
        "issues/new/choose",
        "/pulls",
        "/actions",
        "/branches",
    )
    policy_states={
        "map_not_territory":"Map</strong> ≠ territory" in html or "map / territory" in html,
        "world_other_virtual":"World / Other" in html,
        "network_not_world":"The network is a carrier, not the World." in html,
        "perspective_locality":"Changing perspective changes the interface emphasis, not the underlying branch authority." in html,
        "authority_stays_github":"Authority stays on GitHub." in html,
        "reopening_visible":"Reopening" in html and "reopen" in html.lower(),
        "public_controls_native":all(x in html for x in controls),
    }

    checks={
        "prefreeze_status":
            pre.get("status")=="PREFROZEN_BEFORE_FRESH_PAGES_BUILD",
        "fresh_pages_build_after_prefreeze":
            obs.get("conclusion")=="success"
            and int(obs.get("run_attempt",0)) >= 2
            and obs.get("rerun_requested_after_prefreeze_commit")==args.prefreeze_commit,
        "pages_source_commit_bound":
            obs.get("pages_source_commit")==pre.get("root_carrier",{}).get("pages_source_commit")
            and root.get("commit")==pre.get("root_carrier",{}).get("pages_source_commit"),
        "lain_passive_structural_gate_passed":
            lain.get("status")=="PASS_BOUNDED_LAIN_STRUCTURAL_GATE",
        "exactly_six_indexed_git_layer_centers":
            len(layers)==6
            and ids=={"root","arcane","eclipsis","minerva","venus","ofe"},
        "world_other_remains_virtual_nonbranch":
            snap.get("virtual",{}).get("branch") is None
            and bool(snap.get("virtual",{}).get("name")),
        "network_remains_carrier_not_global_subject":
            "not a global subject" in str(snap.get("network",{}).get("role","")).lower(),
        "current_local_perspective_selectable":
            "data-perspective=" in html
            and "selectPerspective" in app,
        "perspective_change_not_branch_authority":
            policy_states["perspective_locality"]
            and "snapshot?.layers?.find" in app
            and not client_has_privileged_write,
        "layer_boundary_residual_reopening_provenance":
            all_layer_fields,
        "distributed_perception_not_situated_interpretation":
            policy_states["perspective_locality"]
            and bool(root.get("commit")),
        "situated_interpretation_not_authorization":
            policy_states["authority_stays_github"]
            and policy_states["public_controls_native"],
        "authorization_not_action":
            policy_states["authority_stays_github"]
            and not client_has_privileged_write,
        "public_controls_route_to_github_native_surfaces":
            policy_states["public_controls_native"],
        "no_client_side_privileged_repository_mutation":
            not client_has_privileged_write
            and "fetch('./data/layers.json'" in app,
        "pages_build_no_contents_write":
            "contents: read" in workflow
            and "contents: write" not in workflow,
        "map_not_territory_and_world_not_model":
            policy_states["map_not_territory"]
            and policy_states["world_other_virtual"]
            and policy_states["network_not_world"],
        "reopening_visible":
            policy_states["reopening_visible"],
        "no_truth_authority":
            lain.get("truth_authority") is False
            and pre.get("truth_authority") is False,
        "no_promotion_authority":
            lain.get("promotion_authority") is False
            and pre.get("promotion_authority") is False,
    }

    failed=[k for k,v in checks.items() if not v]
    status=(
        "PASS_BOUNDED_ROOT_SITUATED_INTERFACE_GATE"
        if not failed else "WITHHOLD_ROOT_SITUATED_INTERFACE_GATE"
    )
    result={
        "schema":"Venus.RootSituatedInterfaceProspectiveResult.v0.1",
        "status":status,
        "checks":checks,
        "failed_checks":failed,
        "pages_run_id":obs.get("run_id"),
        "pages_run_attempt":obs.get("run_attempt"),
        "pages_source_commit":obs.get("pages_source_commit"),
        "observed_layer_commits":{str(x.get("id")):x.get("commit") for x in layers},
        "next_residual":(
            "BROADER_WORLD_PARTICIPATION"
            if status=="PASS_BOUNDED_ROOT_SITUATED_INTERFACE_GATE"
            else "PRESERVE_SEEING_INTERPRETATION_AUTHORIZATION_ACTION_MEMBRANE"
        ),
        "authorized_external_action_claim":False,
        "broader_world_participation_claim":False,
        "global_subject_claim":False,
        "agi_claim":False,
        "consciousness_claim":False,
        "truth_authority":False,
        "promotion_authority":False,
        "claim_fence":pre.get("claim_fence"),
    }
    Path(args.output).write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    return 0


if __name__=="__main__":
    raise SystemExit(main())
