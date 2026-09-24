from __future__ import annotations

from dataclasses import dataclass, asdict, replace
from itertools import combinations
from typing import Iterable, Any

from .canonical import digest
from .capability_pressure_multifamily import (
    Event,
    GenericCognitiveMachine,
    MultiMachineryConfig,
    MultiMachineryState,
    MultiPressureWorld,
    MultiProposal,
)


@dataclass(frozen=True)
class P9DiagnosticConfig:
    """Bounded organism-owned diagnostic machinery.

    This machinery does not contain task-family labels or a family->solution table.
    It receives an externally returned failure, a provenance-bound public trace bundle,
    the organism's current machinery state, and a generic bounded constructor vocabulary.
    It may ask which generic machinery variations would *change its own behavior* on the
    failed traces, but it does not receive correctness labels for those counterfactuals.
    External evaluation remains the only authority that can accept a proposal.
    """

    counterfactual_depth: int = 2
    require_provenance_binding: bool = True
    withhold_on_ambiguity: bool = True
    max_candidates: int = 192

    def validate(self) -> None:
        if not (0 <= self.counterfactual_depth <= 2):
            raise ValueError("counterfactual_depth")
        if not (1 <= self.max_candidates <= 512):
            raise ValueError("max_candidates")


@dataclass(frozen=True)
class P9DiagnosticState:
    config: P9DiagnosticConfig
    episode_count: int = 0
    accepted_evidence: tuple[str, ...] = ()
    ambiguous_count: int = 0
    rejected_provenance_count: int = 0

    SCHEMA = "Venus.P9.DiagnosticState.v0.1"

    def __post_init__(self) -> None:
        self.config.validate()

    @property
    def state_digest(self) -> str:
        return digest(self.snapshot())

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": self.SCHEMA,
            "config": asdict(self.config),
            "episode_count": self.episode_count,
            "accepted_evidence": list(self.accepted_evidence),
            "ambiguous_count": self.ambiguous_count,
            "rejected_provenance_count": self.rejected_provenance_count,
        }

    @classmethod
    def from_snapshot(cls, data: dict[str, Any]) -> "P9DiagnosticState":
        if data.get("schema") != cls.SCHEMA:
            raise ValueError("unexpected P9 diagnostic schema")
        return cls(
            config=P9DiagnosticConfig(**data["config"]),
            episode_count=int(data.get("episode_count", 0)),
            accepted_evidence=tuple(data.get("accepted_evidence", ())),
            ambiguous_count=int(data.get("ambiguous_count", 0)),
            rejected_provenance_count=int(data.get("rejected_provenance_count", 0)),
        )


@dataclass(frozen=True)
class FailureBundle:
    """Public organism-visible failure bundle.

    Every world carries family='UNLABELED'. Hidden engineering labels live only in the
    outer harness and are never serialized into the organism-facing residual/diagnosis.
    """

    worlds: tuple[MultiPressureWorld, ...]
    split: str

    @property
    def public_digest(self) -> str:
        return digest(
            {
                "split": self.split,
                "worlds": [
                    {
                        "id": w.id,
                        "family": w.family,
                        "events": [(e.op, list(e.args)) for e in w.events],
                        # Expected values are deliberately omitted from the diagnostic digest.
                        # They belong to the external evaluation contract, not internal diagnosis.
                    }
                    for w in self.worlds
                ],
            }
        )


@dataclass(frozen=True)
class P9Residual:
    id: str
    bundle_digest: str
    parent_machinery_digest: str
    trajectory_anchor: str
    baseline_answer_digests: tuple[str, ...]
    failure_count: int


@dataclass(frozen=True)
class P9Proposal:
    id: str
    residual_id: str
    parent_machinery_digest: str
    candidate: MultiMachineryConfig
    mutation_path: tuple[str, ...]
    functional_burdens: tuple[str, ...]
    changed_fraction: float


@dataclass(frozen=True)
class P9Diagnosis:
    id: str
    residual_id: str
    status: str
    proposal_ids: tuple[str, ...]
    mutation_paths: tuple[tuple[str, ...], ...]
    functional_burdens: tuple[tuple[str, ...], ...]
    minimal_depth: int | None
    ambiguity: int


# Reporting vocabulary only. These descriptions are NOT used to select a proposal.
# Selection is based solely on generic counterfactual behavioral change under provenance.
_BURDEN_REPORT = {
    "binding_capacity": "retain more displaced bindings across intervening state",
    "recent_capacity": "retain more recent state without overwriting earlier state",
    "stack_depth": "preserve nested binding frames across intervening scope changes",
    "composition_depth": "combine a larger set of simultaneously addressable components",
    "hypothesis_slots": "maintain more live alternatives until later evidence discriminates them",
    "revision_memory": "preserve returned corrections as retrievable revised state",
    "plan_slots": "retain a longer ordered action sequence before realization",
    "source_indexed": "preserve source/provenance distinctions while resolving conflicting claims",
    "associative_memory": "retain addressable bindings beyond immediate recency",
}


def _mutation_axis(name: str) -> str:
    if name.startswith("binding_capacity"):
        return "binding_capacity"
    if name.startswith("recent_capacity"):
        return "recent_capacity"
    if name.startswith("stack_depth"):
        return "stack_depth"
    if name.startswith("composition_depth"):
        return "composition_depth"
    if name.startswith("hypothesis_slots"):
        return "hypothesis_slots"
    if name.startswith("plan_slots"):
        return "plan_slots"
    if name == "enable_revision_memory":
        return "revision_memory"
    if name == "enable_source_indexing":
        return "source_indexed"
    if name == "enable_associative_memory":
        return "associative_memory"
    return "unknown"


def _burden_description(path: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(_BURDEN_REPORT.get(_mutation_axis(name), "unresolved generic machinery burden") for name in path)


def atomic_variations(cfg: MultiMachineryConfig) -> tuple[tuple[str, MultiMachineryConfig], ...]:
    """Generic bounded constructor vocabulary with no task/family branch."""

    rows: list[tuple[str, MultiMachineryConfig]] = []

    def add(name: str, c: MultiMachineryConfig) -> None:
        c.validate()
        rows.append((name, c))

    if not cfg.associative_memory:
        add("enable_associative_memory", replace(cfg, associative_memory=True, binding_capacity=max(2, cfg.binding_capacity)))
    if cfg.binding_capacity < 32:
        add("binding_capacity+3", replace(cfg, binding_capacity=min(32, cfg.binding_capacity + 3)))
    if cfg.recent_capacity < 16:
        add("recent_capacity+3", replace(cfg, recent_capacity=min(16, cfg.recent_capacity + 3)))
    if cfg.stack_depth < 8:
        add("stack_depth+2", replace(cfg, stack_depth=min(8, cfg.stack_depth + 2)))
    if cfg.composition_depth < 8:
        add("composition_depth+3", replace(cfg, composition_depth=min(8, cfg.composition_depth + 3)))
    if cfg.hypothesis_slots < 8:
        add("hypothesis_slots+2", replace(cfg, hypothesis_slots=min(8, cfg.hypothesis_slots + 2)))
    if not cfg.revision_memory:
        add("enable_revision_memory", replace(cfg, revision_memory=True))
    if cfg.plan_slots < 16:
        add("plan_slots+4", replace(cfg, plan_slots=min(16, cfg.plan_slots + 4)))
    if not cfg.source_indexed:
        add("enable_source_indexing", replace(cfg, source_indexed=True))

    out: list[tuple[str, MultiMachineryConfig]] = []
    seen: set[str] = set()
    for name, candidate in rows:
        h = digest(asdict(candidate))
        if h in seen:
            continue
        seen.add(h)
        out.append((name, candidate))
    return tuple(out)


def candidate_variations(cfg: MultiMachineryConfig, *, depth: int = 2, max_candidates: int = 192) -> tuple[tuple[tuple[str, ...], MultiMachineryConfig], ...]:
    """Enumerate bounded generic one/two-step variations without task identity.

    The generic possibility space is host-bounded at P9. Choosing among it is not.
    P10 is the later burden for revising this construction/search process itself.
    """

    if depth <= 0:
        return ()
    atomic = atomic_variations(cfg)
    rows: list[tuple[tuple[str, ...], MultiMachineryConfig]] = [((name,), cand) for name, cand in atomic]
    if depth >= 2:
        names = [name for name, _ in atomic]
        for first, second in combinations(names, 2):
            first_map = dict(atomic)
            c1 = first_map[first]
            second_map = dict(atomic_variations(c1))
            if second not in second_map:
                # The second operation may have changed name/range after the first; find by axis.
                axis = _mutation_axis(second)
                matches = [(n, c) for n, c in second_map.items() if _mutation_axis(n) == axis]
                if not matches:
                    continue
                n2, c2 = matches[0]
            else:
                n2, c2 = second, second_map[second]
            rows.append(((first, n2), c2))

    out: list[tuple[tuple[str, ...], MultiMachineryConfig]] = []
    seen: set[str] = set()
    for path, candidate in rows:
        h = digest(asdict(candidate))
        if h in seen:
            continue
        seen.add(h)
        out.append((path, candidate))
        if len(out) >= max_candidates:
            break
    return tuple(out)


def _answers(cfg: MultiMachineryConfig, bundle: FailureBundle) -> tuple[str | None, ...]:
    return tuple(GenericCognitiveMachine(cfg).run(w).answer for w in bundle.worlds)


class P9DiagnosticMembrane:
    VERSION = "P9_SELF_DIAGNOSIS_v0.1"
    STATE = "P9_DIAGNOSTIC_STATE"
    RESIDUAL = "P9_DIAGNOSTIC_RESIDUAL"
    DIAGNOSIS = "P9_DIAGNOSIS"
    EVIDENCE = "P9_DIAGNOSTIC_EXTERNAL_EVIDENCE"

    def __init__(self, vm, *, config: P9DiagnosticConfig | None = None):
        self.vm = vm
        self.state = P9DiagnosticState(config or P9DiagnosticConfig())
        self._replay()

    def _replay(self) -> None:
        for event in self.vm.journal.events:
            if event.get("kind") != self.STATE:
                continue
            payload = event.get("payload", {})
            state = P9DiagnosticState.from_snapshot(payload["state"])
            if state.state_digest != payload.get("state_digest"):
                raise RuntimeError("P9 diagnostic-state digest mismatch")
            self.state = state

    def initialize_owned_state(self) -> None:
        """Persist the current bounded diagnostic machinery if not already present."""
        if any(e.get("kind") == self.STATE for e in self.vm.journal.events):
            return
        self._commit_state(source="p9-diagnostic-initialization")

    def _commit_state(self, *, source: str) -> None:
        self.vm.record_interface_event(
            self.STATE,
            {
                "state": self.state.snapshot(),
                "state_digest": self.state.state_digest,
                "version": self.VERSION,
                "project_state_write": False,
            },
            route=("organism-diagnostic-machinery", "persistent-state"),
            source=source,
        )

    def capture_residual(self, bundle: FailureBundle, machinery: MultiMachineryState, *, returned_failures: Iterable[bool]) -> P9Residual:
        failures = tuple(bool(x) for x in returned_failures)
        if len(failures) != len(bundle.worlds):
            raise ValueError("returned-failure cardinality mismatch")
        if not failures or not all(failures):
            raise ValueError("P9 residual requires externally returned failure on every bundled trace")
        if any(w.family != "UNLABELED" for w in bundle.worlds):
            raise ValueError("family identity leaked into organism-facing P9 bundle")
        anchor = self.vm.journal.head
        baseline = _answers(machinery.config, bundle)
        rid = digest(
            {
                "kind": "p9-residual",
                "bundle": bundle.public_digest,
                "parent": machinery.state_digest,
                "anchor": anchor,
                "answers": [digest(a) for a in baseline],
            }
        )
        residual = P9Residual(
            id=rid,
            bundle_digest=bundle.public_digest,
            parent_machinery_digest=machinery.state_digest,
            trajectory_anchor=anchor,
            baseline_answer_digests=tuple(digest(a) for a in baseline),
            failure_count=len(bundle.worlds),
        )
        self.vm.record_interface_event(
            self.RESIDUAL,
            {**asdict(residual), "version": self.VERSION, "family_identity": None},
            route=("World^4", "returned-failure", "Residual", "organism-self-diagnosis"),
            source="unlabeled-capability-pressure-return",
        )
        return residual

    def diagnose(self, residual: P9Residual, bundle: FailureBundle, machinery: MultiMachineryState) -> tuple[P9Diagnosis, tuple[P9Proposal, ...]]:
        cfg = self.state.config
        if cfg.counterfactual_depth <= 0:
            return self._record_withhold(residual, "WITHHOLD_REVERTED_DIAGNOSTIC_STATE")

        if cfg.require_provenance_binding:
            if residual.parent_machinery_digest != machinery.state_digest:
                self.state = replace(self.state, rejected_provenance_count=self.state.rejected_provenance_count + 1)
                self._commit_state(source="p9-provenance-reject")
                return self._record_withhold(residual, "REJECT_STALE_MACHINERY_PROVENANCE")
            if residual.bundle_digest != bundle.public_digest:
                self.state = replace(self.state, rejected_provenance_count=self.state.rejected_provenance_count + 1)
                self._commit_state(source="p9-provenance-reject")
                return self._record_withhold(residual, "REJECT_MISBOUND_FAILURE_TRACE")

        baseline = _answers(machinery.config, bundle)
        if tuple(digest(a) for a in baseline) != residual.baseline_answer_digests:
            self.state = replace(self.state, rejected_provenance_count=self.state.rejected_provenance_count + 1)
            self._commit_state(source="p9-baseline-replay-reject")
            return self._record_withhold(residual, "REJECT_BASELINE_REPLAY_MISMATCH")

        candidates = candidate_variations(
            machinery.config,
            depth=cfg.counterfactual_depth,
            max_candidates=cfg.max_candidates,
        )
        plausible: list[P9Proposal] = []
        for path, candidate in candidates:
            answers = _answers(candidate, bundle)
            changed = tuple(a != b for a, b in zip(answers, baseline))
            changed_fraction = sum(changed) / len(changed) if changed else 0.0
            if changed_fraction < 1.0:
                continue
            pid = digest(
                {
                    "residual": residual.id,
                    "parent": machinery.state_digest,
                    "candidate": asdict(candidate),
                    "path": path,
                    "changed_fraction": changed_fraction,
                }
            )
            plausible.append(
                P9Proposal(
                    id=pid,
                    residual_id=residual.id,
                    parent_machinery_digest=machinery.state_digest,
                    candidate=candidate,
                    mutation_path=path,
                    functional_burdens=_burden_description(path),
                    changed_fraction=changed_fraction,
                )
            )

        if not plausible:
            self.state = replace(self.state, episode_count=self.state.episode_count + 1)
            self._commit_state(source="p9-diagnosis-withhold")
            return self._record_withhold(residual, "WITHHOLD_NO_COUNTERFACTUAL_EXPLANATION")

        minimal_depth = min(len(p.mutation_path) for p in plausible)
        minimal = tuple(p for p in plausible if len(p.mutation_path) == minimal_depth)
        status = "UNIQUE_FUNCTIONAL_DEFICIT" if len(minimal) == 1 else "AMBIGUOUS_WITHHOLD"
        if len(minimal) > 1:
            self.state = replace(
                self.state,
                episode_count=self.state.episode_count + 1,
                ambiguous_count=self.state.ambiguous_count + 1,
            )
        else:
            self.state = replace(self.state, episode_count=self.state.episode_count + 1)
        self._commit_state(source="p9-diagnosis-update")

        did = digest(
            {
                "residual": residual.id,
                "status": status,
                "proposals": [p.id for p in minimal],
                "paths": [list(p.mutation_path) for p in minimal],
            }
        )
        diagnosis = P9Diagnosis(
            id=did,
            residual_id=residual.id,
            status=status,
            proposal_ids=tuple(p.id for p in minimal),
            mutation_paths=tuple(p.mutation_path for p in minimal),
            functional_burdens=tuple(p.functional_burdens for p in minimal),
            minimal_depth=minimal_depth,
            ambiguity=len(minimal),
        )
        self.vm.record_interface_event(
            self.DIAGNOSIS,
            {
                **asdict(diagnosis),
                "version": self.VERSION,
                "family_identity": None,
                "selection_basis": "counterfactual-behavioral-change-only; no correctness authority",
            },
            route=("Residual", "self-localization", "candidate-machinery-proposal"),
            source="organism-diagnostic-machinery",
        )
        return diagnosis, minimal

    def _record_withhold(self, residual: P9Residual, status: str) -> tuple[P9Diagnosis, tuple[P9Proposal, ...]]:
        did = digest({"residual": residual.id, "status": status})
        diagnosis = P9Diagnosis(did, residual.id, status, (), (), (), None, 0)
        self.vm.record_interface_event(
            self.DIAGNOSIS,
            {**asdict(diagnosis), "version": self.VERSION, "family_identity": None},
            route=("Residual", "self-localization", "WITHHOLD"),
            source="organism-diagnostic-machinery",
        )
        return diagnosis, ()

    def bind_external_evidence(self, diagnosis: P9Diagnosis, *, accepted_proposal_ids: Iterable[str], evaluation_digests: Iterable[str]) -> None:
        accepted = tuple(sorted(accepted_proposal_ids))
        evals = tuple(sorted(evaluation_digests))
        evidence_digest = digest({"diagnosis": diagnosis.id, "accepted": accepted, "evaluations": evals})
        self.vm.record_interface_event(
            self.EVIDENCE,
            {
                "diagnosis_id": diagnosis.id,
                "accepted_proposal_ids": accepted,
                "evaluation_digests": evals,
                "evidence_digest": evidence_digest,
                "version": self.VERSION,
            },
            route=("external-evaluation", "returned-evidence", "diagnostic-history"),
            source="external-evaluator",
        )
        self.state = replace(
            self.state,
            accepted_evidence=self.state.accepted_evidence + (evidence_digest,),
        )
        self._commit_state(source="p9-external-evidence-update")


def opaque_world(events: Iterable[Event], expected: str, *, split: str, salt: str) -> MultiPressureWorld:
    events = tuple(events)
    wid = "U-" + digest({"events": [(e.op, list(e.args)) for e in events], "split": split, "salt": salt})[:16]
    return MultiPressureWorld(wid, "UNLABELED", events, expected, split)


def make_hidden_challenge(kind: str, *, split: str, count: int = 12) -> FailureBundle:
    """Outer-harness challenge generator.

    `kind` is deliberately host-side and must never be passed to P9DiagnosticMembrane.
    The organism sees only the returned unlabeled event traces and its own machinery state.
    """

    worlds: list[MultiPressureWorld] = []
    for i in range(count):
        if kind == "memory_capacity":
            events: list[Event] = []
            first_k = f"m{i}_0"; first_v = f"mv{i}_0"
            for j in range(5):
                events.append(Event("PUT", (f"m{i}_{j}", f"mv{i}_{j}")))
            events.append(Event("GET", (first_k,)))
            expected = first_v
        elif kind == "nested_binding":
            expected = f"inner{i}"
            events = [
                Event("PUSH"), Event("BIND", ("outer", f"outer{i}")),
                Event("PUSH"), Event("BIND", ("target", expected)),
                Event("PUSH"), Event("BIND", ("deep", f"deep{i}")),
                Event("POP"), Event("LOOKUP", ("target",)),
            ]
        elif kind == "representation_composition":
            names = tuple(f"c{j}" for j in range(5))
            events = [Event("PART", (name, f"C{i}_{j}")) for j, name in enumerate(names)]
            events.append(Event("ASSEMBLE", names))
            expected = "|".join(f"C{i}_{j}" for j in range(5))
        elif kind == "uncertainty":
            events = [Event("HYP", ("g", f"h{j}", f"{0.10 + j*0.01:.2f}")) for j in range(5)]
            events.extend([Event("EVIDENCE", ("g", "h4", "1.0")), Event("BEST", ("g",))])
            expected = "h4"
        elif kind == "planning":
            steps = tuple(f"s{i}_{j}" for j in range(7))
            events = [Event("STEP", (s,)) for s in steps] + [Event("PLAN")]
            expected = ">".join(steps)
        elif kind == "ambiguous_memory":
            events = [
                Event("PUT", (f"a{i}_0", f"av{i}_0")),
                Event("PUT", (f"a{i}_1", f"av{i}_1")),
                Event("PUT", (f"a{i}_2", f"av{i}_2")),
                Event("GET", (f"a{i}_0",)),
            ]
            expected = f"av{i}_0"
        elif kind == "wide_realization":
            names = tuple(f"r{j}" for j in range(5))
            events = [Event("PART", (name, f"R{i}_{j}")) for j, name in enumerate(names)]
            render_order = tuple(reversed(names))
            events.append(Event("RENDER", render_order))
            expected = "|".join(f"R{i}_{j}" for j in reversed(range(5)))
        elif kind == "source_provenance":
            key = f"sk{i}"; good = f"sv{i}"
            events = [
                Event("TRUST", ("s1", "0.2")),
                Event("TRUST", ("s2", "0.9")),
                Event("SOURCE", ("s1", key, "wrong")),
                Event("SOURCE", ("s2", key, good)),
                Event("ASK_TRUSTED", (key,)),
            ]
            expected = good
        else:
            raise ValueError(kind)
        worlds.append(opaque_world(events, expected, split=split, salt=f"{kind}:{i}"))
    return FailureBundle(tuple(worlds), split)


def combine_bundles(*bundles: FailureBundle, split: str) -> FailureBundle:
    worlds: list[MultiPressureWorld] = []
    for b in bundles:
        worlds.extend(b.worlds)
    # Re-id to avoid exposing source bundle identity through ids.
    relabeled = []
    for i, w in enumerate(worlds):
        relabeled.append(opaque_world(w.events, w.expected, split=split, salt=f"combo:{i}"))
    return FailureBundle(tuple(relabeled), split)


def to_multi_proposal(p: P9Proposal) -> MultiProposal:
    return MultiProposal(
        id=p.id,
        parent_digest=p.parent_machinery_digest,
        candidate=p.candidate,
        mutation="p9:" + "+".join(p.mutation_path),
    )
