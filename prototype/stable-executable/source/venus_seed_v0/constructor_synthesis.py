from __future__ import annotations
from collections import defaultdict
from typing import Sequence

CONSTS=(-2,-1,0,1,2)
MAX_COST=6

def evaluate_expr(expr,x:int)->int:
    t=expr[0]
    if t=="x": return int(x)
    if t=="c": return int(expr[1])
    if t=="neg": return -evaluate_expr(expr[1],x)
    if t=="abs": return abs(evaluate_expr(expr[1],x))
    a=evaluate_expr(expr[1],x); b=evaluate_expr(expr[2],x)
    if t=="add": return a+b
    if t=="sub": return a-b
    if t=="mul": return a*b
    raise KeyError(t)

def source(expr)->str:
    t=expr[0]
    if t=="x": return "x"
    if t=="c": return str(expr[1])
    if t=="neg": return f"(-{source(expr[1])})"
    if t=="abs": return f"abs({source(expr[1])})"
    op={"add":"+","sub":"-","mul":"*"}[t]
    return f"({source(expr[1])}{op}{source(expr[2])})"

def _canon_bin(t,a,b):
    if t in ("add","mul") and source(a)>source(b): a,b=b,a
    return (t,a,b)

def enumerate_programs(inputs:Sequence[int], max_cost:int=MAX_COST):
    inputs=tuple(int(x) for x in inputs); best={}; by_cost=defaultdict(list)
    def add(cost,e):
        sig=tuple(evaluate_expr(e,x) for x in inputs)
        if any(abs(v)>100000 for v in sig): return
        cand=(cost,len(source(e)),source(e),e)
        old=best.get(sig)
        if old is None or cand[:3]<old[:3]: best[sig]=cand
    for e in [("x",)]+[("c",c) for c in CONSTS]: add(1,e)
    by_cost[1]=[z[3] for z in best.values() if z[0]==1]
    for cost in range(2,max_cost+1):
        snap=list(best.values())
        for z in snap:
            if z[0]==cost-1:
                add(cost,("neg",z[3])); add(cost,("abs",z[3]))
        for ca in range(1,cost-1):
            cb=cost-1-ca
            A=[z[3] for z in list(best.values()) if z[0]==ca]
            B=[z[3] for z in list(best.values()) if z[0]==cb]
            for a in A:
                for b in B:
                    for t in ("add","sub","mul"): add(cost,_canon_bin(t,a,b))
        by_cost[cost]=[z[3] for z in best.values() if z[0]==cost]
    return sorted(best.values(),key=lambda z:z[:3])

def synthesize(inputs:Sequence[int], labels:Sequence[int], max_cost:int=MAX_COST):
    target=tuple(int(y) for y in labels)
    exact=[z for z in enumerate_programs(inputs,max_cost) if tuple(evaluate_expr(z[3],x) for x in inputs)==target]
    return min(exact,key=lambda z:z[:3]) if exact else None
