from __future__ import annotations
class DependencyGraph:
    def __init__(self): self.parents={}; self.children={}
    def add(self,node,parents=()):
        self.parents.setdefault(node,set()).update(parents)
        for p in parents:self.children.setdefault(p,set()).add(node)
    def affected_closure(self,roots):
        out=set(roots); q=list(roots)
        while q:
            x=q.pop()
            for y in self.children.get(x,()):
                if y not in out: out.add(y); q.append(y)
        return out
