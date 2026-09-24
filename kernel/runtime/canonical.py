from __future__ import annotations
import hashlib, json
from typing import Any
from dataclasses import is_dataclass, asdict
from enum import Enum

def _normalize(value: Any):
    if is_dataclass(value): return _normalize(asdict(value))
    if isinstance(value, Enum): return value.value
    if isinstance(value, dict): return {str(k):_normalize(v) for k,v in value.items()}
    if isinstance(value, (list,tuple,set)): return [_normalize(v) for v in value]
    return value

def canonical_json(value: Any) -> str:
    return json.dumps(_normalize(value), sort_keys=True, separators=(",",":"), ensure_ascii=False)

def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()

def chain_digest(previous: str, kind: str, payload: Any) -> str:
    return digest({"previous": previous, "kind": kind, "payload": payload})
