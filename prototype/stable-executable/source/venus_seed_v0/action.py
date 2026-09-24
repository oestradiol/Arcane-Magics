from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Iterable


class Terminal(str, Enum):
    COMMIT='COMMIT'
    ROLLBACK='ROLLBACK'
    NO_ACTION='NO_ACTION'
    UNVERIFIED_COMMIT='UNVERIFIED_COMMIT'


@dataclass(frozen=True)
class ActionDecision:
    authorized: bool
    executed: bool
    verified: bool | None
    terminal: Terminal
    proposed: Any
    actual: Any | None


def governed_action(proposed: Any, *, authorized: bool, execute: Callable[[Any],Any], verify: Callable[[Any],bool]|None, destructive_no_verifier_commit: bool=False) -> ActionDecision:
    if not authorized:
        return ActionDecision(False,False,None,Terminal.NO_ACTION,proposed,None)
    actual=execute(proposed)
    if verify is None:
        # Deliberate destructive ablation used only when explicitly requested by the fixture.
        term=Terminal.UNVERIFIED_COMMIT if destructive_no_verifier_commit else Terminal.ROLLBACK
        return ActionDecision(True,True,None,term,proposed,actual)
    ok=bool(verify(actual))
    return ActionDecision(True,True,ok,Terminal.COMMIT if ok else Terminal.ROLLBACK,proposed,actual)


@dataclass(frozen=True)
class EvaluatorScope:
    version: str
    governed_variants: frozenset[str]

    def includes(self, variant: str) -> bool:
        return variant in self.governed_variants


def zero_wrong_governed_reference(scope: EvaluatorScope, rows: Iterable[tuple[str,ActionDecision,bool]]) -> bool:
    """Rows are (variant, decision, actual_is_correct). Scope is frozen prospectively."""
    for variant,decision,correct in rows:
        if not scope.includes(variant):
            continue
        if decision.terminal in (Terminal.COMMIT,Terminal.UNVERIFIED_COMMIT) and not correct:
            return False
    return True


@dataclass(frozen=True)
class ParentBoundActionDecision:
    parent_valid: bool
    parent_id: str | None
    decision: ActionDecision | None


def validate_parent_record(parent: dict, registry: dict) -> bool:
    """Exact parent/provenance binding used by the GPA1 successor-action bridge."""
    if not isinstance(parent, dict) or 'id' not in parent:
        return False
    objects = registry.get('objects', ()) if isinstance(registry, dict) else ()
    expected = next((o for o in objects if o.get('id') == parent.get('id')), None)
    if expected is None:
        return False
    keys = ('id','functional_payload','functional_payload_sha256','provenance_kind','source_artifact','source_sha256','source_state')
    return all(parent.get(k) == expected.get(k) for k in keys)


def governed_action_from_parent(
    parent: dict,
    registry: dict,
    *,
    propose: Callable[[Any], Any],
    authorized: bool,
    execute: Callable[[Any], Any],
    verify: Callable[[Any], bool] | None,
    destructive_no_verifier_commit: bool = False,
) -> ParentBoundActionDecision:
    if not validate_parent_record(parent, registry):
        return ParentBoundActionDecision(False, parent.get('id') if isinstance(parent, dict) else None, None)
    proposal = propose(parent['functional_payload'])
    decision = governed_action(
        proposal,
        authorized=authorized,
        execute=execute,
        verify=verify,
        destructive_no_verifier_commit=destructive_no_verifier_commit,
    )
    return ParentBoundActionDecision(True, parent['id'], decision)
