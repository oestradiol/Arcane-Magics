from __future__ import annotations

"""Capability-specific scaffold for #206 grounded theater-template reconstruction.

This module is deliberately in kernel/development, not kernel/runtime.
It contains no hard-coded language words, relation names, or project answer keys.
All face/atom/relation content arrives as teacher data. A later Internalizer claim
requires compiling any earned consequence into learner-owned state and making
this trainer/source unavailable.
"""

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


def _norm(text: str) -> str:
    return " ".join(str(text).casefold().split())


def char_features(text: str, n: int = 3) -> frozenset[str]:
    value=_norm(text)
    if not value:
        return frozenset()
    if len(value)<n:
        return frozenset((value,))
    return frozenset(value[i:i+n] for i in range(len(value)-n+1))


def jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    u=a|b
    return 0.0 if not u else len(a&b)/len(u)


@dataclass(frozen=True)
class GroundedPrediction:
    relation_id: str | None
    status: str
    atom_scores: tuple[tuple[str,float], ...]
    relation_scores: tuple[tuple[str,float], ...]
    template: Mapping[str,Any] | None


def learn_state(
    grounding: Mapping[str,Any],
    teacher_structures: Mapping[str,Mapping[str,Any]],
    *,
    n: int = 3,
) -> dict[str,Any]:
    """Compile teacher examples/templates into inert learner state.

    The returned state stores only generic surface prototypes, atom composition,
    and teacher-derived opaque templates. It does not retain relation training
    sentences and does not execute teacher code.
    """
    faces=tuple(str(x) for x in grounding["faces"])
    atom_examples: dict[str,dict[str,tuple[tuple[str,...],...]]]={}
    for row in grounding["atoms"]:
        atom=str(row["atom"])
        atom_examples[atom]={}
        for face in faces:
            atom_examples[atom][face]=tuple(
                tuple(sorted(char_features(text,n)))
                for text in row["examples"][face]
            )
    relation_atom_sets={
        str(k):tuple(str(x) for x in v)
        for k,v in grounding["target_relation_atom_sets"].items()
    }
    templates={str(k):dict(v) for k,v in teacher_structures.items()}
    return {
        "schema":"Venus.GroundedTheaterTemplateState.v0.1",
        "n":int(n),
        "faces":faces,
        "atom_examples":atom_examples,
        "relation_atom_sets":relation_atom_sets,
        "templates":templates,
    }


def _atom_score(state: Mapping[str,Any], face: str, atom: str, text: str) -> float:
    n=int(state["n"])
    target=char_features(text,n)
    examples=state["atom_examples"][atom][face]
    if not examples:
        return 0.0
    return max(jaccard(target,frozenset(ex)) for ex in examples)


def predict(
    state: Mapping[str,Any],
    *,
    face: str,
    text: str,
    min_margin: float = 0.002,
) -> GroundedPrediction:
    if state.get("schema")!="Venus.GroundedTheaterTemplateState.v0.1":
        raise ValueError("unsupported grounded-theater state")
    if face not in set(state["faces"]):
        raise ValueError("unknown face")

    atoms=sorted(state["atom_examples"])
    atom_scores={atom:_atom_score(state,face,atom,text) for atom in atoms}
    relation_scores={}
    for relation,required in state["relation_atom_sets"].items():
        vals=[atom_scores[a] for a in required]
        relation_scores[relation]=sum(vals)/len(vals) if vals else 0.0

    ranked=sorted(relation_scores.items(),key=lambda x:(-x[1],x[0]))
    best_relation,best_score=ranked[0]
    second=ranked[1][1] if len(ranked)>1 else 0.0
    margin=best_score-second
    atom_out=tuple(sorted(atom_scores.items(),key=lambda x:(-x[1],x[0])))
    rel_out=tuple(ranked)
    if best_score<=0.0 or margin<min_margin:
        return GroundedPrediction(None,"WITHHOLD_GROUNDED_TEMPLATE_AMBIGUOUS",atom_out,rel_out,None)
    return GroundedPrediction(
        best_relation,
        "PREDICTED_FROM_LEARNED_GROUNDING",
        atom_out,
        rel_out,
        state["templates"][best_relation],
    )
