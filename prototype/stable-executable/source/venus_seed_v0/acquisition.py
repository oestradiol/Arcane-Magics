from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Sequence
from .canonical import digest


@dataclass(frozen=True)
class HigherOrderInput:
    id: str
    payload: Any
    scope: str
    provenance: str
    provenance_fresh: bool = True


@dataclass(frozen=True)
class AcquisitionTask:
    id: str
    scope: str
    corpus: tuple[Any,...]


@dataclass(frozen=True)
class AcquisitionAuthorization:
    object_id: str
    task_id: str
    scope: str
    role: str = 'acquisition_input'
    valid: bool = True


@dataclass(frozen=True)
class PreparedAcquisition:
    task_id: str
    corpus_count: int
    object_id: str | None
    object_read: bool
    read_witness: str | None
    update_count: int
    reasons: tuple[str,...]


def prepare_acquisition(task: AcquisitionTask, h: HigherOrderInput|None, auth: AcquisitionAuthorization|None, *, require_task_corpus: bool=True) -> PreparedAcquisition:
    reasons=[]
    if require_task_corpus and not task.corpus:
        reasons.append('missing substantive acquisition corpus')
    if h is None:
        reasons.append('higher-order object absent')
    if auth is None or not auth.valid:
        reasons.append('acquisition role not authorized')
    elif h is not None:
        if auth.object_id != h.id or auth.task_id != task.id:
            reasons.append('authorization/object/task mismatch')
        if auth.scope != task.scope or h.scope != task.scope:
            reasons.append('scope mismatch')
        if auth.role != 'acquisition_input':
            reasons.append('wrong role')
    if h is not None and not h.provenance_fresh:
        reasons.append('stale provenance')
    ok=not reasons
    witness=digest({'task':task.id,'object':h.id,'corpus':len(task.corpus),'role':'acquisition_input'}) if ok else None
    # X0 barrier: this interface never performs learner-state update.
    return PreparedAcquisition(task.id,len(task.corpus),h.id if ok else None,ok,witness,0,tuple(reasons))
