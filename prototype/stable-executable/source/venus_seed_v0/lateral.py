from __future__ import annotations
from .model import LateralComparison

def compare(left_ids,right_ids,*,unresolved=()):
    l=set(left_ids); r=set(right_ids)
    return LateralComparison(tuple(sorted(l&r)),tuple(sorted(l-r)),tuple(sorted(r-l)),tuple(sorted(set(unresolved))),False)

def merge_is_implicit(_: LateralComparison) -> bool:
    return False
