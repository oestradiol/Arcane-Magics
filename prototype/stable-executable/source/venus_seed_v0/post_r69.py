from __future__ import annotations
from dataclasses import dataclass
import hashlib, json
from pathlib import Path
from typing import Any

PASS_DONOR_PREFIXES=("EXECUTABLE_PASS","EVIDENCE_VERIFIED","NOT_APPLICABLE")
REPLAY_REQUIRED={"RESULT_BEARING","NEGATIVE_RESULT","INVALID_LINEAGE","ENGINEERING_CONTRACT","FORMAL_OBLIGATION"}

@dataclass(frozen=True)
class ReconciliationFailure:
    r_id:str
    reason:str

class PostR69Registry:
    def __init__(self,data:dict[str,Any],root:Path):
        self.data=data; self.root=Path(root); self.entries=list(data["entries"])
    @classmethod
    def load(cls,path:str|Path, root:str|Path|None=None):
        path=Path(path)
        return cls(json.loads(path.read_text(encoding="utf-8")), Path(root) if root else path.parents[1])
    def validate_sequence(self):
        if not self.entries:
            raise ValueError("post-R69 ledger is empty")
        got=[int(e["ordinal"]) for e in self.entries]
        last=got[-1]
        if last < 70:
            raise ValueError(f"post-R69 terminal ordinal must be >=70, got {last}")
        exp=list(range(70,last+1))
        if got!=exp:
            raise ValueError(f"post-R69 sequence mismatch: expected R70..R{last}, got {got}")
        if [e["r_id"] for e in self.entries] != [f"R{i}" for i in exp]:
            raise ValueError("r_id/ordinal mismatch")
        return True
    def entry(self,r:int|str):
        key=f"R{r}" if isinstance(r,int) else r
        return next(e for e in self.entries if e["r_id"]==key)
    def _verify_descriptors(self,descriptors,prefix="source"):
        problems=[]
        for s in descriptors:
            p=self.root/s["path"]
            if not p.exists(): problems.append(f"missing_{prefix}:{s['path']}"); continue
            raw=p.read_bytes()
            if len(raw)!=s["bytes"]: problems.append(f"bytes_{prefix}:{s['path']}")
            if hashlib.sha256(raw).hexdigest()!=s["sha256"]: problems.append(f"sha256_{prefix}:{s['path']}")
        return problems
    def verify_sources(self,e):
        if not e.get("sources"):
            return ["no bound source artifact"]
        return self._verify_descriptors(e["sources"])
    def source_digest_map(self,e):
        return {s["path"]:s["sha256"] for s in e.get("sources",[])}

class PostR69ConservationGate:
    def __init__(self,registry:PostR69Registry): self.registry=registry
    def evaluate(self):
        failures:list[ReconciliationFailure]=[]
        try: self.registry.validate_sequence()
        except Exception as ex:
            failures.append(ReconciliationFailure("SEQUENCE",str(ex)))
        for e in self.registry.entries:
            rid=e["r_id"]
            for p in self.registry.verify_sources(e): failures.append(ReconciliationFailure(rid,p))
            native=str(e.get("native_obligation_test",""))
            if not native.startswith("PASS_"): failures.append(ReconciliationFailure(rid,f"native_obligation_test={native}"))
            if e.get("gate_class") in REPLAY_REQUIRED:
                donor=str(e.get("donor_replay",""))
                if not donor.startswith(PASS_DONOR_PREFIXES): failures.append(ReconciliationFailure(rid,f"donor_replay={donor}"))
        return {
            "status":"PASS" if not failures else "BLOCKED",
            "entries":len(self.registry.entries),
            "required_replay":sum(e.get("gate_class") in REPLAY_REQUIRED for e in self.registry.entries),
            "failures":[f.__dict__ for f in failures],
            "current_vm_eligible":not failures,
        }

def _merge(dst:dict[str,Any],src:dict[str,Any]):
    for k,v in src.items():
        if isinstance(v,dict) and isinstance(dst.get(k),dict): _merge(dst[k],v)
        elif isinstance(v,dict): dst[k]=json.loads(json.dumps(v))
        else: dst[k]=v
    return dst

def project_state(registry:PostR69Registry, through:int=131):
    registry.validate_sequence()
    state={
      "schema":"Venus.ProjectState.PostR69.v0.1",
      "base":"R69 integrated VM checkpoint",
      "through":"R69",
      "canon":{},"science":{},"developmental":{},"representation":{},"formal":{},
      "governance":{},"routing":{},"engineering":{},"externality":{},"invalid":{},"provenance":{},"authority":{}
    }
    for e in registry.entries:
        if e["ordinal"]>through: break
        _merge(state,e.get("state_delta",{})); state["through"]=e["r_id"]
    return state

def replay_reconciliations(vm,registry:PostR69Registry,through:int=131):
    registry.validate_sequence()
    existing={x.get("r_id") for x in getattr(vm,"reconciliations",[]) if isinstance(x,dict)}
    for e in registry.entries:
        if e["ordinal"]>through: break
        if e["r_id"] in existing: continue
        payload={
          "r_id":e["r_id"],"ordinal":e["ordinal"],"transaction_class":e["transaction_class"],
          "gate_class":e["gate_class"],"scientific_effect":e["scientific_effect"],"label":e["label"],
          "source_digests":registry.source_digest_map(e),
          "attestation_digests":{s["path"]:s["sha256"] for s in e.get("attestation_sources",[])},
          "source_residual":e.get("source_residual"),
          "donor_replay":e["donor_replay"],
          "native_obligation_test":e["native_obligation_test"],"state_delta":e.get("state_delta",{})
        }
        vm._record("RECONCILIATION",payload,route=("post-r69","reconciliation"),source="canonical-repository")
    state=project_state(registry,through=through)
    vm._record("PROJECT_STATE",state,route=("projection","project-state"),source="reconciliation-ledger")
    return state
