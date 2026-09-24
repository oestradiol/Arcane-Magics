from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Iterable
from .canonical import chain_digest

class TrajectoryJournal:
    """Append-only authority-bearing history. Current state is a projection of this log."""
    GENESIS="0"*64
    def __init__(self,path: str|Path|None=None):
        self.path=Path(path) if path else None
        self.events=[]
        if self.path and self.path.exists(): self._load()
    @property
    def head(self): return self.events[-1]["digest"] if self.events else self.GENESIS
    def append(self,kind:str,payload:dict[str,Any],*,route=(),source=None):
        previous=self.head
        body={"seq":len(self.events),"kind":kind,"payload":payload,"route":list(route),"source":source,"previous":previous}
        body["digest"]=chain_digest(previous,kind,{"payload":payload,"route":list(route),"source":source,"seq":body["seq"]})
        self.events.append(body)
        if self.path:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            with self.path.open("a",encoding="utf-8") as f: f.write(json.dumps(body,sort_keys=True,separators=(",",":"))+"\n")
        return body
    def _load(self):
        previous=self.GENESIS
        for i,line in enumerate(self.path.read_text().splitlines()):
            e=json.loads(line)
            if e["seq"]!=i or e["previous"]!=previous: raise ValueError("trajectory chain order mismatch")
            d=chain_digest(previous,e["kind"],{"payload":e["payload"],"route":e.get("route",[]),"source":e.get("source"),"seq":i})
            if d!=e["digest"]: raise ValueError("trajectory chain digest mismatch")
            self.events.append(e); previous=d
    def route_fingerprint(self):
        return tuple((e["kind"],tuple(e.get("route",[])),e.get("source")) for e in self.events)
