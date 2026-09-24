from __future__ import annotations

from dataclasses import asdict, is_dataclass
from enum import Enum
import hashlib
import json
from typing import Any


def _normalize(value: Any) -> Any:
    """Normalize new Venus objects into a deterministic JSON-compatible form.

    This is the canonicalizer for new repository/runtime objects. The VMK2
    checkpoint retains its historical hash contract in vmk2.py; changing that
    contract would invalidate admitted IG10 roots.
    """
    if is_dataclass(value):
        return _normalize(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(k): _normalize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize(v) for v in value]
    if isinstance(value, (set, frozenset)):
        normalized = [_normalize(v) for v in value]
        return sorted(
            normalized,
            key=lambda v: json.dumps(
                v, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ),
        )
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(
        _normalize(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def chain_digest(previous: str, kind: str, payload: Any) -> str:
    return digest({"previous": previous, "kind": kind, "payload": payload})
