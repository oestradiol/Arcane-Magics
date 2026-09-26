from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


ALLOWED_STATUS=frozenset({
    "KNOWN_TRUE","KNOWN_FALSE","UNKNOWN","WITHHELD","REPORTED_TRUE","REPORTED_FALSE"
})


def _canonical(obj: Any)->str:
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":"))


def digest(obj: Any)->str:
    return hashlib.sha256(_canonical(obj).encode("utf-8")).hexdigest()


def validate(state: Mapping[str,Any])->None:
    if state.get("schema")!="Venus.CognitiveTheaterState.v0.1":
        raise ValueError("wrong TheaterState schema")
    participants=list(state.get("participants") or [])
    if not participants or len(participants)!=len(set(participants)):
        raise ValueError("participants must be nonempty and unique")
    pset=set(participants)
    local=state.get("local_kfs") or {}
    if set(local)!=pset:
        raise ValueError("local_kfs must be indexed by every and only participant")
    for pid,kfs in local.items():
        if not isinstance(kfs,dict):
            raise ValueError(f"local_kfs[{pid}] must be a mapping")
        for prop,status in kfs.items():
            if not str(prop):
                raise ValueError("empty proposition")
            if status not in ALLOWED_STATUS:
                raise ValueError(f"invalid epistemic status {status}")
    seen_events=set()
    for event in state.get("events") or []:
        eid=str(event.get("event_id") or "")
        if not eid or eid in seen_events:
            raise ValueError("event ids must be nonempty and unique")
        seen_events.add(eid)
        actor=event.get("actor")
        if actor is not None and actor not in pset:
            raise ValueError("event actor must be an indexed participant or null")
        visible=event.get("visible_to") or []
        if any(x not in pset for x in visible):
            raise ValueError("visible_to contains unknown participant")
        for eff in event.get("effects") or []:
            if eff.get("participant") not in pset:
                raise ValueError("effect participant is unknown")
            if eff.get("status") not in ALLOWED_STATUS:
                raise ValueError("effect status invalid")
            if not str(eff.get("proposition") or ""):
                raise ValueError("effect proposition empty")


def traverse(state: Mapping[str,Any], *, prefix: int|None=None)->dict[str,dict[str,str]]:
    validate(state)
    current={pid:dict(kfs) for pid,kfs in state["local_kfs"].items()}
    events=list(state.get("events") or [])
    if prefix is not None:
        if prefix<0:
            raise ValueError("prefix must be >=0")
        events=events[:prefix]
    for event in events:
        for eff in event.get("effects") or []:
            current[eff["participant"]][eff["proposition"]]=eff["status"]
    return current


def local_view(state: Mapping[str,Any], participant: str, *, prefix: int|None=None)->dict[str,Any]:
    validate(state)
    if participant not in state["participants"]:
        raise KeyError(participant)
    events=list(state.get("events") or [])
    if prefix is not None:
        events=events[:prefix]
    visible=[
        {
            "event_id":e["event_id"],
            "actor":e.get("actor"),
            "relation":e.get("relation"),
            "objects":list(e.get("objects") or []),
        }
        for e in events
        if participant in set(e.get("visible_to") or [])
    ]
    return {
        "participant":participant,
        "kfs":traverse(state,prefix=prefix)[participant],
        "visible_events":visible,
        "residuals":list(state.get("residuals") or []),
    }


def alpha_normal_form(state: Mapping[str,Any])->dict[str,Any]:
    validate(state)
    mapping={pid:f"p{i}" for i,pid in enumerate(state["participants"])}
    def rename_obj(x):
        if isinstance(x,str) and x in mapping:
            return mapping[x]
        if isinstance(x,list):
            return [rename_obj(v) for v in x]
        if isinstance(x,dict):
            return {k:rename_obj(v) for k,v in x.items()}
        return x
    out=rename_obj(dict(state))
    out["participants"]=[mapping[x] for x in state["participants"]]
    out["local_kfs"]={mapping[pid]:dict(state["local_kfs"][pid]) for pid in state["participants"]}
    return out


def endpoint_digest(state: Mapping[str,Any])->str:
    return digest(traverse(state))


def history_digest(state: Mapping[str,Any])->str:
    validate(state)
    alpha=alpha_normal_form(state)
    return digest(alpha.get("events") or [])


def same_endpoint(a: Mapping[str,Any],b: Mapping[str,Any])->bool:
    return endpoint_digest(a)==endpoint_digest(b)


def same_history(a: Mapping[str,Any],b: Mapping[str,Any])->bool:
    return history_digest(a)==history_digest(b)
