from __future__ import annotations
from dataclasses import dataclass, asdict, replace
from collections import deque, defaultdict
from typing import Iterable, Any

from .canonical import digest
from .capability_pressure import MachineryMembrane


@dataclass(frozen=True)
class MultiMachineryConfig:
    recent_capacity: int = 1
    associative_memory: bool = True
    binding_capacity: int = 2
    stack_depth: int = 0
    composition_depth: int = 0
    hypothesis_slots: int = 1
    revision_memory: bool = False
    plan_slots: int = 0
    source_indexed: bool = False

    def validate(self) -> None:
        if not (1 <= self.recent_capacity <= 16): raise ValueError('recent_capacity')
        if not (0 <= self.binding_capacity <= 32): raise ValueError('binding_capacity')
        if self.associative_memory and self.binding_capacity < 1: raise ValueError('binding_capacity')
        if not (0 <= self.stack_depth <= 8): raise ValueError('stack_depth')
        if not (0 <= self.composition_depth <= 8): raise ValueError('composition_depth')
        if not (1 <= self.hypothesis_slots <= 8): raise ValueError('hypothesis_slots')
        if not (0 <= self.plan_slots <= 16): raise ValueError('plan_slots')


@dataclass(frozen=True)
class Event:
    op: str
    args: tuple[str, ...] = ()

@dataclass(frozen=True)
class MultiPressureWorld:
    id: str
    family: str
    events: tuple[Event, ...]
    expected: str
    split: str

@dataclass(frozen=True)
class MultiReturn:
    world_id: str
    family: str
    answer: str | None
    expected: str
    success: bool
    config_digest: str

@dataclass(frozen=True)
class MultiProposal:
    id: str
    parent_digest: str
    candidate: MultiMachineryConfig
    mutation: str

@dataclass(frozen=True)
class MultiEvaluation:
    proposal_id: str
    baseline: float
    candidate: float
    gain: float
    accepted: bool
    family: str
    world_ids: tuple[str, ...]


class GenericCognitiveMachine:
    """Bounded generic machinery for P0-P8 pressure worlds.

    Event semantics are fixed environment/interface semantics. The configurable machinery
    controls retention, binding, composition, competing hypotheses, correction memory,
    planning and source-indexed retrieval. No project-language meanings occur here.
    """
    def __init__(self, cfg: MultiMachineryConfig):
        cfg.validate(); self.cfg=cfg
        self.recent=deque(maxlen=cfg.recent_capacity)
        self.assoc={}; self.assoc_order=deque(maxlen=max(1,cfg.binding_capacity))
        self.frames=[]
        self.parts={}
        self.hyp=defaultdict(dict)
        self.plan=[]
        self.source_claims=defaultdict(dict); self.source_trust={}

    def _store(self,k,v):
        self.recent.append((k,v))
        if self.cfg.associative_memory:
            if k not in self.assoc and len(self.assoc_order)>=self.cfg.binding_capacity:
                old=self.assoc_order.popleft(); self.assoc.pop(old,None)
            if k in self.assoc:
                try:self.assoc_order.remove(k)
                except ValueError:pass
            self.assoc[k]=v; self.assoc_order.append(k)

    def _get(self,k):
        for kk,v in reversed(self.recent):
            if kk==k:return v
        return self.assoc.get(k) if self.cfg.associative_memory else None

    def process(self,e:Event):
        op,a=e.op,e.args
        if op=='PUT': self._store(a[0],a[1]); return None
        if op=='NOISE': self.recent.append(('__noise__',a[0] if a else '')); return None
        if op=='GET': return self._get(a[0])
        if op=='PUSH':
            if self.cfg.stack_depth<=0 or len(self.frames)>=self.cfg.stack_depth:return None
            self.frames.append({}); return None
        if op=='BIND':
            if not self.frames:return None
            self.frames[-1][a[0]]=a[1]; return None
        if op=='POP':
            if self.frames:self.frames.pop()
            return None
        if op=='LOOKUP':
            for fr in reversed(self.frames):
                if a[0] in fr:return fr[a[0]]
            return None
        if op=='PART': self.parts[a[0]]=a[1]; return None
        if op in {'ASSEMBLE','RENDER'}:
            if self.cfg.composition_depth<=0:return None
            vals=[]
            for name in a:
                if name not in self.parts:return None
                vals.append(self.parts[name])
            if len(vals)>self.cfg.composition_depth:return None
            return '|'.join(vals)
        if op=='HYP':
            group,label,score=a[0],a[1],float(a[2])
            if label not in self.hyp[group] and len(self.hyp[group])>=self.cfg.hypothesis_slots:return None
            self.hyp[group][label]=score; return None
        if op=='EVIDENCE':
            group,label,delta=a[0],a[1],float(a[2])
            if label in self.hyp[group]: self.hyp[group][label]+=delta
            return None
        if op=='BEST':
            group=a[0]
            if not self.hyp[group]:return None
            return max(self.hyp[group].items(),key=lambda kv:(kv[1],kv[0]))[0]
        if op=='CORRECT':
            if self.cfg.revision_memory:self._store(a[0],a[1])
            return None
        if op=='STEP':
            if self.cfg.plan_slots<=0 or len(self.plan)>=self.cfg.plan_slots:return None
            self.plan.append(a[0]); return None
        if op=='PLAN': return '>'.join(self.plan) if self.plan else None
        if op=='TRUST': self.source_trust[a[0]]=float(a[1]); return None
        if op=='SOURCE':
            if self.cfg.source_indexed:self.source_claims[a[1]][a[0]]=a[2]
            return None
        if op=='ASK_TRUSTED':
            if not self.cfg.source_indexed:return None
            claims=self.source_claims[a[0]]
            if not claims:return None
            src=max(claims,key=lambda s:(self.source_trust.get(s,0.0),s))
            return claims[src]
        return None

    def run(self,w:MultiPressureWorld)->MultiReturn:
        ans=None
        for e in w.events:
            out=self.process(e)
            if out is not None: ans=out
        return MultiReturn(w.id,w.family,ans,w.expected,ans==w.expected,digest(asdict(self.cfg)))


class MultiMachineryState:
    SCHEMA='Venus.MachineryState.MultiPressure.v0.1'
    def __init__(self,cfg:MultiMachineryConfig): cfg.validate(); self.config=cfg
    @property
    def state_digest(self):return digest({'schema':self.SCHEMA,'config':asdict(self.config)})
    def snapshot(self):return {'schema':self.SCHEMA,'config':asdict(self.config)}
    @classmethod
    def from_snapshot(cls,d):
        if d.get('schema')!=cls.SCHEMA:raise ValueError('schema')
        return cls(MultiMachineryConfig(**d['config']))


class MultiMachineryMembrane:
    VERSION='CAPABILITY_PRESSURE_MULTIFAMILY_v0.1'
    RES='MULTI_MACHINERY_RESIDUAL'; PROP='MULTI_MACHINERY_PROPOSAL'; EVAL='MULTI_MACHINERY_EVALUATION'; COMMIT='MULTI_MACHINERY_COMMIT'
    def __init__(self,vm):
        self.vm=vm
        # Inherit generic memory parameters from the already-persisted R137 machinery state.
        r137=MachineryMembrane(vm).state.config
        self.state=MultiMachineryState(MultiMachineryConfig(r137.recent_capacity,r137.associative_memory,r137.binding_capacity))
        self._replay()
    def _replay(self):
        accepted={}
        for e in self.vm.journal.events:
            p=e.get('payload',{}); k=e.get('kind')
            if k==self.EVAL and p.get('accepted'): accepted[p['proposal_id']]=p
            elif k==self.COMMIT:
                if p.get('proposal_id') not in accepted:raise RuntimeError('commit without external accept')
                st=MultiMachineryState.from_snapshot(p['state'])
                if st.state_digest!=p.get('state_digest'):raise RuntimeError('digest mismatch')
                self.state=st
    @staticmethod
    def score(cfg,worlds):
        ws=tuple(worlds); return sum(GenericCognitiveMachine(cfg).run(w).success for w in ws)/len(ws) if ws else 0.0
    def retain_residual(self,w,ret):
        rid=digest({'world':w.id,'family':w.family,'answer':ret.answer,'expected':ret.expected,'state':self.state.state_digest})
        self.vm.record_interface_event(self.RES,{'id':rid,'world_id':w.id,'family':w.family,'state_digest':self.state.state_digest,'version':self.VERSION},route=('World^4','failure','Residual','machinery-search'),source='multi-pressure-world')
        return rid
    def proposals(self):
        c=self.state.config; parent=self.state.state_digest; rows=[]
        def add(name,cfg):
            cfg.validate(); rows.append(MultiProposal(digest({'parent':parent,'mutation':name,'candidate':asdict(cfg)}),parent,cfg,name))
        if c.stack_depth<8:add('stack_depth+2',replace(c,stack_depth=min(8,c.stack_depth+2)))
        if c.composition_depth<8:add('composition_depth+3',replace(c,composition_depth=min(8,c.composition_depth+3)))
        if c.hypothesis_slots<8:add('hypothesis_slots+2',replace(c,hypothesis_slots=min(8,c.hypothesis_slots+2)))
        if not c.revision_memory:add('enable_revision_memory',replace(c,revision_memory=True))
        if c.plan_slots<16:add('plan_slots+4',replace(c,plan_slots=min(16,c.plan_slots+4)))
        if not c.source_indexed:add('enable_source_indexing',replace(c,source_indexed=True))
        if c.binding_capacity<32:add('binding_capacity+3',replace(c,binding_capacity=min(32,c.binding_capacity+3)))
        if c.recent_capacity<16:add('recent_capacity+3',replace(c,recent_capacity=min(16,c.recent_capacity+3)))
        out=[];seen=set()
        for p in rows:
            h=digest(asdict(p.candidate))
            if h not in seen:seen.add(h);out.append(p)
        return tuple(out)
    def record_proposal(self,p):
        self.vm.record_interface_event(self.PROP,{**asdict(p),'candidate':asdict(p.candidate),'version':self.VERSION},route=('Residual','candidate-machinery','sandbox'),source='organism-machinery-search')
    def evaluate(self,p,worlds,*,family,min_gain=.40):
        ws=tuple(worlds); b=self.score(self.state.config,ws); c=self.score(p.candidate,ws)
        ev=MultiEvaluation(p.id,b,c,c-b,(c-b)>=min_gain,family,tuple(w.id for w in ws))
        self.vm.record_interface_event(self.EVAL,{**asdict(ev),'version':self.VERSION,'evaluator':'external-matched-multifamily-v0.1'},route=('sandbox','external-evaluation','retain-revise-reject'),source='external-evaluator')
        return ev
    def commit(self,p,ev):
        if p.parent_digest!=self.state.state_digest:raise RuntimeError('stale proposal')
        if ev.proposal_id!=p.id or not ev.accepted:raise ValueError('unaccepted')
        st=MultiMachineryState(p.candidate)
        self.vm.record_interface_event(self.COMMIT,{'proposal_id':p.id,'evaluation':asdict(ev),'state':st.snapshot(),'state_digest':st.state_digest,'version':self.VERSION,'project_state_write':False},route=('external-validation','provenance-bound-commit','MachineryState'),source='governed-machinery-commit')
        self.state=st


def make_family_worlds(family:str,*,split:str,count:int=24):
    out=[]
    for i in range(count):
        k=f'k{(i*7+3)%101}'; v=f'v{(i*11+5)%127}'
        if family=='P0': ev=(Event('PUT',(k,v)),Event('GET',(k,))); exp=v
        elif family=='P1': ev=(Event('PUT',(k,v)),*(Event('NOISE',(f'n{i}_{j}',)) for j in range(5+i%2)),Event('PUT',(f'x{i}',f'y{i}',)),Event('GET',(k,))); exp=v
        elif family=='P2': ev=(Event('PUSH'),Event('BIND',('x',v)),Event('PUSH'),Event('BIND',('x',f'inner{i}')),Event('POP'),Event('LOOKUP',('x',))); exp=v
        elif family=='P3': ev=(Event('PART',('a',f'A{i}')),Event('PART',('b',f'B{i}')),Event('PART',('c',f'C{i}')),Event('ASSEMBLE',('a','b','c'))); exp=f'A{i}|B{i}|C{i}'
        elif family=='P4': ev=(Event('HYP',('g','left','0.3')),Event('HYP',('g','right','0.4')),Event('EVIDENCE',('g','right','0.5')),Event('BEST',('g',))); exp='right'
        elif family=='P5': ev=(Event('PUT',(k,'old')),*(Event('NOISE',(f'n{i}_{j}',)) for j in range(3)),Event('CORRECT',(k,v)),*(Event('NOISE',(f'm{i}_{j}',)) for j in range(3)),Event('GET',(k,))); exp=v
        elif family=='P6': ev=(Event('STEP',(f's{i}a',)),Event('STEP',(f's{i}b',)),Event('STEP',(f's{i}c',)),Event('PLAN')); exp=f's{i}a>s{i}b>s{i}c'
        elif family=='P7': ev=(Event('PART',('p',f'P{i}')),Event('PART',('q',f'Q{i}')),Event('RENDER',('q','p'))); exp=f'Q{i}|P{i}'
        elif family=='P8': ev=(Event('TRUST',('s1','0.2')),Event('TRUST',('s2','0.9')),Event('SOURCE',('s1',k,'wrong')),Event('SOURCE',('s2',k,v)),Event('ASK_TRUSTED',(k,))); exp=v
        else: raise ValueError(family)
        out.append(MultiPressureWorld(f'{family}-{split}-{i:03d}',family,tuple(ev),exp,split))
    return tuple(out)


def mixed_worlds(*,split:str,count_per_family:int=8):
    rows=[]
    for f in [f'P{i}' for i in range(9)]: rows.extend(make_family_worlds(f,split=split,count=count_per_family))
    return tuple(rows)
