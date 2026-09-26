from __future__ import annotations

"""Bounded lateral-reconstruction episode harness.

The harness consumes already-returned face data. It does not fetch GitHub and it
does not own hidden holdout labels. It compares:
1) relation-only basis;
2) more context within the same relation basis;
3) relation basis + one independently answerable face selected by train-only LOO gain.

A positive result is only a bounded representation-expansion result. It is not
an Internalizer pass and grants no promotion authority.
"""

from dataclasses import dataclass, asdict
import hashlib
import json
import math
import re
from typing import Any, Iterable, Mapping, Sequence


class LateralEpisodeError(ValueError):
    pass


@dataclass(frozen=True)
class Prediction:
    pr_number: int
    relation_basic: bool
    relation_expanded: bool
    lateral: bool


@dataclass(frozen=True)
class LateralProposal:
    schema: str
    selected_face: str
    train_scores: Mapping[str, float]
    selected_train_gain: float
    cross_face_residual_ids: tuple[int, ...]
    preserved_face_sources: Mapping[str, str]
    holdout_predictions: tuple[Prediction, ...]
    holdout_label_accessed: bool
    internalization_claim: bool
    promotion_authority: bool


def _refs(body: str) -> tuple[int, ...]:
    return tuple(sorted({int(x) for x in re.findall(r"#(\d+)", body or "")}))


def _bin(value: int) -> str:
    if value <= 0:
        return "0"
    return str(int(math.log2(value)))


def relation_basic_tokens(row: Mapping[str, Any]) -> frozenset[str]:
    n=int(row["pr_number"])
    refs=_refs(str(row.get("body") or ""))
    back=sum(1 for x in refs if x < n)
    forward=sum(1 for x in refs if x > n)
    out={
        f"refcount:{min(len(refs),3)}+",
        f"back:{min(back,3)}+",
        f"forward:{min(forward,3)}+",
    }
    for x in refs:
        d=abs(n-x)
        bucket="lt5" if d<5 else "lt20" if d<20 else "lt80" if d<80 else "ge80"
        out.add(f"distance:{bucket}")
    return frozenset(out)


def relation_expanded_tokens(row: Mapping[str, Any]) -> frozenset[str]:
    base=set(relation_basic_tokens(row))
    for x in _refs(str(row.get("body") or "")):
        base.add(f"ref:{x}")
        base.add(f"refmod8:{x%8}")
    return frozenset(base)


def path_tokens(row: Mapping[str, Any]) -> frozenset[str]:
    out=set()
    for raw in row.get("filenames",()):
        path=str(raw)
        parts=[x for x in path.split("/") if x]
        if parts:
            out.add(f"top:{parts[0]}")
        if len(parts)>1:
            out.add(f"pair:{parts[0]}/{parts[1]}")
        if "." in parts[-1] if parts else False:
            out.add(f"ext:{parts[-1].rsplit('.',1)[-1].lower()}")
        low=path.lower()
        for fam in ("kernel/","tests/","docs/","provenance/","autonomy/",".github/","site/","review/"):
            if low.startswith(fam):
                out.add(f"family:{fam.rstrip('/')}")
    return frozenset(out or {"path:none"})


def scale_tokens(row: Mapping[str, Any]) -> frozenset[str]:
    return frozenset({
        f"commits:{_bin(int(row.get('commits') or 0))}",
        f"additions:{_bin(int(row.get('additions') or 0))}",
        f"deletions:{_bin(int(row.get('deletions') or 0))}",
        f"files:{_bin(int(row.get('changed_files') or 0))}",
    })


def _sim(a: frozenset[str], b: frozenset[str]) -> float:
    if not a and not b:
        return 1.0
    union=a|b
    return len(a&b)/len(union) if union else 0.0


def _predict(
    train: Sequence[Mapping[str, Any]],
    query: Mapping[str, Any],
    token_fn,
    *,
    exclude_pr: int | None=None,
    k: int=3,
) -> bool:
    pool=[x for x in train if int(x["pr_number"]) != exclude_pr]
    if not pool:
        raise LateralEpisodeError("training pool empty")
    ranked=sorted(
        (
            (-_sim(token_fn(x),token_fn(query)), int(x["pr_number"]), bool(x["train_label"]))
            for x in pool
        ),
        key=lambda z:(z[0],z[1]),
    )[:k]
    yes=sum(1 for _,_,label in ranked if label)
    no=len(ranked)-yes
    if yes==no:
        total_yes=sum(1 for x in pool if bool(x["train_label"]))
        total_no=len(pool)-total_yes
        if total_yes==total_no:
            return False
        return total_yes>total_no
    return yes>no


def _combined(face: str):
    if face=="path_topology":
        return lambda row: frozenset(set(relation_expanded_tokens(row)) | set(path_tokens(row)))
    if face=="change_scale":
        return lambda row: frozenset(set(relation_expanded_tokens(row)) | set(scale_tokens(row)))
    raise LateralEpisodeError(f"unknown face {face}")


def _loo(train: Sequence[Mapping[str, Any]], token_fn) -> tuple[float, dict[int,bool]]:
    preds={}
    correct=0
    for row in train:
        n=int(row["pr_number"])
        p=_predict(train,row,token_fn,exclude_pr=n)
        preds[n]=p
        correct += int(p==bool(row["train_label"]))
    return correct/len(train),preds


def propose_lateral_reconstruction(dataset: Mapping[str, Any]) -> LateralProposal:
    train=tuple(dataset.get("train",()))
    holdout=tuple(dataset.get("holdout",()))
    if not train or not holdout:
        raise LateralEpisodeError("train and holdout rows required")
    if any("train_label" not in x for x in train):
        raise LateralEpisodeError("training labels required")
    if any("train_label" in x or "holdout_label" in x or "merged" in x for x in holdout):
        raise LateralEpisodeError("holdout labels must remain inaccessible before prediction")

    basic_score,basic_preds=_loo(train,relation_basic_tokens)
    expanded_score,expanded_preds=_loo(train,relation_expanded_tokens)
    candidates={}
    candidate_preds={}
    for face in ("path_topology","change_scale"):
        score,preds=_loo(train,_combined(face))
        candidates[face]=score
        candidate_preds[face]=preds

    selected=sorted(candidates, key=lambda f:(-candidates[f],f))[0]
    gain=candidates[selected]-expanded_score
    residuals=tuple(sorted(
        n for n in expanded_preds
        if expanded_preds[n] != candidate_preds[selected][n]
    ))

    predictions=[]
    for row in holdout:
        predictions.append(Prediction(
            pr_number=int(row["pr_number"]),
            relation_basic=_predict(train,row,relation_basic_tokens),
            relation_expanded=_predict(train,row,relation_expanded_tokens),
            lateral=_predict(train,row,_combined(selected)),
        ))

    return LateralProposal(
        schema="Venus.LateralProposal.v0.1",
        selected_face=selected,
        train_scores={
            "relation_basic":basic_score,
            "relation_expanded":expanded_score,
            "path_topology":candidates["path_topology"],
            "change_scale":candidates["change_scale"],
        },
        selected_train_gain=gain,
        cross_face_residual_ids=residuals,
        preserved_face_sources={
            "relation":"GitHub PR body/reference face",
            selected:(
                "GitHub PR changed-files endpoint"
                if selected=="path_topology"
                else "GitHub PR metadata endpoint"
            ),
        },
        holdout_predictions=tuple(predictions),
        holdout_label_accessed=False,
        internalization_claim=False,
        promotion_authority=False,
    )


def score_hidden_labels(
    proposal: LateralProposal,
    labels: Mapping[int,bool],
) -> Mapping[str, Any]:
    expected={x.pr_number for x in proposal.holdout_predictions}
    if set(labels) != expected:
        raise LateralEpisodeError("hidden label IDs do not match frozen holdout predictions")
    totals={"relation_basic":0,"relation_expanded":0,"lateral":0}
    rows=[]
    for pred in proposal.holdout_predictions:
        label=bool(labels[pred.pr_number])
        row={"pr_number":pred.pr_number,"label":label}
        for name in totals:
            value=bool(getattr(pred,name))
            totals[name]+=int(value==label)
            row[name]=value
        rows.append(row)
    n=len(rows)
    acc={k:v/n for k,v in totals.items()}
    best_same=max(acc["relation_basic"],acc["relation_expanded"])
    if proposal.selected_train_gain <= 0:
        status="REDUCIBLE_OR_NO_DIMENSION_GAIN"
    elif acc["lateral"] <= best_same:
        status="WITHHOLD_BAD_MAP_OR_OVERFIT"
    else:
        status="PASS_BOUNDED_LATERAL_MISSING_COORDINATE"
    return {
        "schema":"Venus.LateralEpisodeResult.v0.1",
        "status":status,
        "selected_face":proposal.selected_face,
        "selected_train_gain":proposal.selected_train_gain,
        "cross_face_residual_ids":list(proposal.cross_face_residual_ids),
        "holdout_accuracy":acc,
        "holdout_rows":rows,
        "internalization_claim":False,
        "promotion_authority":False,
        "truth_authority":False,
    }
