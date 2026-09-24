from __future__ import annotations
from dataclasses import dataclass
import json
from pathlib import Path

PASS_PREFIXES=("EXECUTABLE_PASS","PASS","EVIDENCE_VERIFIED","NOT_APPLICABLE")
REQUIRED={"ENGINEERING_CONTRACT","RESULT_BEARING","NEGATIVE_RESULT","INVALID_LINEAGE"}
@dataclass(frozen=True)
class GateFailure:
    id:str; reason:str
class HeritageRegistry:
    def __init__(self,data): self.data=data; self.entries={e["id"]:e for e in data["entries"]}
    @classmethod
    def load(cls,path): return cls(json.loads(Path(path).read_text()))
    def required(self): return [e for e in self.entries.values() if e["gate_class"] in REQUIRED]
    def unmapped_material_findings(self):
        return [e["id"] for e in self.required() if not e.get("obligation") or not e.get("source_paths")]
class ConservationGate:
    def __init__(self,registry:HeritageRegistry): self.registry=registry
    def evaluate(self):
        failures=[]
        for e in self.registry.required():
            d=str(e.get("donor_replay","")); n=str(e.get("native_obligation_test",""))
            if not d.startswith(PASS_PREFIXES): failures.append(GateFailure(e["id"],f"donor_replay={d}"))
            if not n.startswith(PASS_PREFIXES): failures.append(GateFailure(e["id"],f"native_obligation_test={n}"))
        for x in self.registry.unmapped_material_findings(): failures.append(GateFailure(x,"missing obligation/source mapping"))
        return {"status":"PASS" if not failures else "BLOCKED","required":len(self.registry.required()),"failures":[f.__dict__ for f in failures],"m6_unlocked":not failures}
