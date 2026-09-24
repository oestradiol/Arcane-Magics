from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class RoleEvidence:
    role: str
    present: bool
    witnesses: tuple[str, ...] = ()


@dataclass(frozen=True)
class AccountComponent:
    name: str
    required_roles: tuple[str, ...]


@dataclass(frozen=True)
class MatureAccount:
    name: str
    components: tuple[AccountComponent, ...]
    prohibited_roles: tuple[str, ...] = ()
    whole_object_open: bool = False
    whole_object_note: str = ""


@dataclass(frozen=True)
class ComparisonResult:
    disposition: str
    rationale: str | None
    component_coverage: tuple[tuple[str, float], ...]
    matched_roles: tuple[str, ...]
    missing_roles: tuple[str, ...]
    prohibited_present: tuple[str, ...]
    residual: dict[str, Any] | None


class OrganismHistoryRoleExtractor:
    """Bounded generic projection from organism-side runtime events to comparison roles.

    This is deliberately not a natural-language semantic parser and contains no mature
    project factor names. It reads only non-Canonical runtime events prior to the
    requested cutoff and exposes generic developmental roles. The caller supplies any
    later account/component vocabulary separately.
    """

    ROLE_ORDER = (
        "history",
        "model",
        "scope",
        "future_difference",
        "nonpreauthored_return",
        "local_choice",
        "reopen",
        "correction_channel",
        "provenance_guard",
        "self_sealing",
        "provenance_erasure",
        "suppressed_correction",
    )

    def __init__(self, vm):
        self.vm = vm

    @staticmethod
    def _bool(d: dict[str, Any], *path: str) -> bool:
        cur: Any = d
        for key in path:
            if not isinstance(cur, dict) or key not in cur:
                return False
            cur = cur[key]
        return bool(cur)

    def extract(self, *, before_seq: int | None = None) -> tuple[RoleEvidence, ...]:
        present: dict[str, bool] = {k: False for k in self.ROLE_ORDER}
        witnesses: dict[str, list[str]] = {k: [] for k in self.ROLE_ORDER}

        def mark(role: str, witness: str, value: bool = True):
            if value:
                present[role] = True
                witnesses[role].append(witness)

        events = [
            e for e in self.vm.journal.events
            if (before_seq is None or int(e.get("seq", -1)) < before_seq)
            and e.get("kind") not in {"RECONCILIATION", "PROJECT_STATE"}
        ]

        # History is witnessed by the existence of a persistent organism-side sequence,
        # not by governance/Canonical projection.
        if events:
            mark("history", f"runtime_event_count={len(events)}")

        for e in events:
            kind = e.get("kind")
            p = e.get("payload", {})
            seq = e.get("seq")
            w = f"seq={seq}:{kind}"

            if kind == "R141_REDERIVED_DEVELOPMENTAL_STATE":
                state = p.get("state", {})
                corr = state.get("correction", {}) if isinstance(state, dict) else {}
                gov = state.get("governance", {}) if isinstance(state, dict) else {}
                mark("model", w, bool(corr.get("self_model_rederive")))
                mark("scope", w, bool(corr.get("local_revision")) and bool(corr.get("preserve_unaffected")))
                mark("reopen", w, bool(corr.get("counterexample_search")) and bool(corr.get("local_revision")))
                mark("provenance_guard", w, bool(gov.get("reject_misbound")))
                # Explicit governance fences are evidence against, not evidence for, the
                # prohibited states. We therefore do not mark prohibited roles here.

            elif kind == "OPAQUE_TRANSFORM_REDERIVATION":
                mark("model", w, bool(p.get("expressions")) and p.get("coordinate_mapping_given") is False)

            elif kind == "RETURN_BOUND_LOCAL_REVISION":
                mark("scope", w, bool(p.get("clauses")))
                mark("reopen", w, bool(p.get("clauses")))
                mark("correction_channel", w, bool(p.get("bound_token")) and bool(p.get("clauses")))
                mark(
                    "nonpreauthored_return",
                    w,
                    bool(p.get("bound_token")) and p.get("self_validation") is False,
                )
                mark("provenance_guard", w, int(p.get("misbound_records_rejected", 0) or 0) > 0)

            elif kind == "LATER_ACQUISITION_STATE":
                treatment = p.get("treatment_model", {})
                stale = p.get("stale_model", {})
                changed = treatment != stale or p.get("treatment_selected_input") != p.get("stale_selected_input")
                mark("future_difference", w, changed)
                mark("local_choice", w, p.get("treatment_selected_input") != p.get("stale_selected_input"))

            elif kind == "R141_POSTREPAIR_SEMANTIC_MACHINERY_COMMIT":
                # A committed mechanism that explicitly had not seen the result world is
                # relevant to non-preauthored return without implying outside authorship.
                mark("nonpreauthored_return", w, p.get("result_world_seen") is False)

        return tuple(
            RoleEvidence(k, present[k], tuple(witnesses[k])) for k in self.ROLE_ORDER
        )


class RelationalComparisonMembrane:
    """Generic structured comparison over organism history and a supplied account.

    The membrane never contains project factor names or a stored answer. A verdict is
    computed only from role coverage, explicit prohibited-role evidence, and an account's
    own unresolved whole-object flag.
    """

    def compare(self, evidence: Iterable[RoleEvidence], account: MatureAccount) -> ComparisonResult:
        evidence_map = {e.role: e for e in evidence}
        present = {k for k, e in evidence_map.items() if e.present}

        if not account.components or any(not c.required_roles for c in account.components):
            return ComparisonResult(
                disposition="WITHHOLD",
                rationale=None,
                component_coverage=(),
                matched_roles=(),
                missing_roles=(),
                prohibited_present=(),
                residual={
                    "kind": "COMPARISON_ACCOUNT_UNDERSPECIFIED",
                    "reason": "The supplied account lacks operational role definitions; names alone do not determine a mapping.",
                },
            )

        prohibited = tuple(sorted(set(account.prohibited_roles) & present))
        coverage: list[tuple[str, float]] = []
        matched: set[str] = set()
        missing: set[str] = set()
        for c in account.components:
            req = tuple(dict.fromkeys(c.required_roles))
            got = [r for r in req if r in present]
            miss = [r for r in req if r not in present]
            matched.update(got)
            missing.update(miss)
            coverage.append((c.name, len(got) / len(req)))

        if prohibited:
            return ComparisonResult(
                disposition="REJECT",
                rationale=(
                    "REJECT: the organism history exhibits account-prohibited role(s): "
                    + ", ".join(prohibited)
                ),
                component_coverage=tuple(coverage),
                matched_roles=tuple(sorted(matched)),
                missing_roles=tuple(sorted(missing)),
                prohibited_present=prohibited,
                residual=None,
            )

        if missing:
            # A nonempty but incomplete operational correspondence is explicitly partial;
            # an empty correspondence is rejected rather than guessed into existence.
            if matched:
                return ComparisonResult(
                    disposition="PARTIAL-MAP",
                    rationale=(
                        "PARTIAL-MAP: operational correspondence is incomplete; matched "
                        + ", ".join(sorted(matched))
                        + "; unresolved "
                        + ", ".join(sorted(missing))
                        + "."
                    ),
                    component_coverage=tuple(coverage),
                    matched_roles=tuple(sorted(matched)),
                    missing_roles=tuple(sorted(missing)),
                    prohibited_present=(),
                    residual={
                        "kind": "COMPARISON_ROLE_RESIDUAL",
                        "missing_roles": sorted(missing),
                    },
                )
            return ComparisonResult(
                disposition="REJECT",
                rationale="REJECT: no required operational correspondence is present in the organism history.",
                component_coverage=tuple(coverage),
                matched_roles=(),
                missing_roles=tuple(sorted(missing)),
                prohibited_present=(),
                residual=None,
            )

        if account.whole_object_open:
            return ComparisonResult(
                disposition="PARTIAL-MAP",
                rationale=(
                    "PARTIAL-MAP: all declared operational component roles are witnessed in the organism history, "
                    "but the mature account itself leaves whole-object interaction/minimality unresolved; "
                    "factor-wise correspondence therefore does not license whole-object identity."
                ),
                component_coverage=tuple(coverage),
                matched_roles=tuple(sorted(matched)),
                missing_roles=(),
                prohibited_present=(),
                residual={
                    "kind": "WHOLE_OBJECT_MAPPING_RESIDUAL",
                    "reason": account.whole_object_note or "whole-object interaction/minimality remains unresolved",
                },
            )

        return ComparisonResult(
            disposition="MAP",
            rationale="MAP: all declared operational component roles are witnessed and the supplied account declares no unresolved whole-object mapping burden.",
            component_coverage=tuple(coverage),
            matched_roles=tuple(sorted(matched)),
            missing_roles=(),
            prohibited_present=(),
            residual=None,
        )
