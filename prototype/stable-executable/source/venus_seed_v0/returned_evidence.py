from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class ReturnDisposition(str, Enum):
    NO_EFFECT='NO_EFFECT'
    WITHHOLD='WITHHOLD'
    AUTHORIZE_UPDATE='AUTHORIZE_UPDATE'

@dataclass(frozen=True)
class ReturnRecord:
    id: str
    target_id: str
    value: object
    source: str
    jurisdiction: str
    epoch: int
    verified: bool
    current: bool=True

@dataclass(frozen=True)
class ReturnDecision:
    disposition: ReturnDisposition
    target_id: str
    value: object|None
    reasons: tuple[str,...]

@dataclass(frozen=True)
class ResidualTransition:
    target_id: str
    state: str
    reason: str
    record_ids: tuple[str,...]

class ReturnLedger:
    """Append-only returned-evidence ledger; ingest itself never mutates target state."""
    def __init__(self):
        self.records:list[ReturnRecord]=[]
        self.residual_history:list[ResidualTransition]=[]
        self.retired_ids:set[str]=set()

    def ingest(self, record:ReturnRecord) -> ReturnRecord:
        if any(r.id==record.id for r in self.records):
            raise ValueError('duplicate return id')
        self.records.append(record)
        return record

    def retire(self, record_ids) -> None:
        ids=set(record_ids)
        unknown=ids-{r.id for r in self.records}
        if unknown: raise ValueError(f'unknown return ids: {sorted(unknown)}')
        self.retired_ids.update(ids)

    def adjudicate(self, target_id:str, *, jurisdiction:str, epoch:int) -> ReturnDecision:
        candidates=[r for r in self.records if r.id not in self.retired_ids and r.target_id==target_id and r.verified and r.current
                    and r.jurisdiction==jurisdiction and r.epoch==epoch]
        if not candidates:
            return ReturnDecision(ReturnDisposition.NO_EFFECT,target_id,None,('no current verified in-jurisdiction return',))
        values=[]
        for r in candidates:
            if r.value not in values: values.append(r.value)
        ids=tuple(r.id for r in candidates)
        if len(values)>1:
            self.residual_history.append(ResidualTransition(target_id,'OPEN','conflicting current verified returns',ids))
            return ReturnDecision(ReturnDisposition.WITHHOLD,target_id,None,('verified conflict',))
        return ReturnDecision(ReturnDisposition.AUTHORIZE_UPDATE,target_id,values[0],('current verified return agrees',))

    def resolve(self,target_id:str,*,jurisdiction:str,epoch:int) -> ReturnDecision:
        d=self.adjudicate(target_id,jurisdiction=jurisdiction,epoch=epoch)
        if d.disposition is ReturnDisposition.AUTHORIZE_UPDATE:
            open_ids=tuple(x.record_ids for x in self.residual_history if x.target_id==target_id and x.state=='OPEN')
            if open_ids:
                flattened=tuple(y for xs in open_ids for y in xs)
                self.residual_history.append(ResidualTransition(target_id,'RESOLVED','later verified return resolves active conflict',flattened))
        return d
