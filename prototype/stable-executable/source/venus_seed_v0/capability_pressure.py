from __future__ import annotations

from dataclasses import dataclass, asdict
from collections import deque
from typing import Iterable, Any

from .canonical import digest


@dataclass(frozen=True)
class MachineryConfig:
    """Bounded organism-owned machinery state.

    The constructor vocabulary is deliberately generic: finite recent-history capacity,
    optional key/value associative retention, and a bounded number of stored bindings.
    It contains no task-family names or answer-specific semantic rules.
    """
    recent_capacity: int = 1
    associative_memory: bool = False
    binding_capacity: int = 0

    def validate(self) -> None:
        if not (1 <= self.recent_capacity <= 16):
            raise ValueError("recent_capacity out of bounded range")
        if not (0 <= self.binding_capacity <= 32):
            raise ValueError("binding_capacity out of bounded range")
        if self.associative_memory and self.binding_capacity < 1:
            raise ValueError("associative_memory requires positive binding_capacity")


@dataclass(frozen=True)
class PressureTurn:
    kind: str
    tokens: tuple[str, ...]


@dataclass(frozen=True)
class PressureWorld:
    id: str
    turns: tuple[PressureTurn, ...]
    expected: str
    split: str


@dataclass(frozen=True)
class WorldReturn:
    world_id: str
    answer: str | None
    expected: str
    success: bool
    machinery_digest: str


@dataclass(frozen=True)
class ResidualRecord:
    id: str
    world_id: str
    trace_digest: str
    prior_machinery_digest: str
    observed_success: bool


@dataclass(frozen=True)
class MachineryProposal:
    id: str
    parent_digest: str
    candidate: MachineryConfig
    mutation: str


@dataclass(frozen=True)
class MachineryEvaluation:
    proposal_id: str
    baseline_score: float
    candidate_score: float
    gain: float
    accepted: bool
    evaluation_world_ids: tuple[str, ...]


class BoundedTaskMachine:
    """Generic bounded state machine used inside capability-pressure worlds.

    World syntax is intentionally tiny and mechanical:
      PUT key value  -> present a binding
      NOISE token    -> unrelated intervening material
      GET key        -> request the currently retained value for key

    The machinery does not know which world family it is in. It receives only turns.
    """
    def __init__(self, config: MachineryConfig):
        config.validate()
        self.config = config
        self.recent: deque[tuple[str, str]] = deque(maxlen=config.recent_capacity)
        self.assoc: dict[str, str] = {}
        self.assoc_order: deque[str] = deque(maxlen=max(1, config.binding_capacity))

    def _put_assoc(self, key: str, value: str) -> None:
        if not self.config.associative_memory:
            return
        if key not in self.assoc and len(self.assoc_order) >= self.config.binding_capacity:
            old = self.assoc_order.popleft()
            self.assoc.pop(old, None)
        if key in self.assoc:
            try:
                self.assoc_order.remove(key)
            except ValueError:
                pass
        self.assoc[key] = value
        self.assoc_order.append(key)

    def process(self, turn: PressureTurn) -> str | None:
        kind = turn.kind
        toks = turn.tokens
        if kind == "PUT":
            if len(toks) != 2:
                return None
            key, value = toks
            self.recent.append((key, value))
            self._put_assoc(key, value)
            return None
        if kind == "NOISE":
            # Noise consumes recent-state capacity without supplying a retrievable binding.
            self.recent.append(("__noise__", toks[0] if toks else ""))
            return None
        if kind == "GET":
            if len(toks) != 1:
                return None
            key = toks[0]
            for k, v in reversed(self.recent):
                if k == key:
                    return v
            if self.config.associative_memory:
                return self.assoc.get(key)
            return None
        return None

    def run(self, world: PressureWorld) -> WorldReturn:
        answer = None
        for turn in world.turns:
            out = self.process(turn)
            if turn.kind == "GET":
                answer = out
        return WorldReturn(
            world_id=world.id,
            answer=answer,
            expected=world.expected,
            success=(answer == world.expected),
            machinery_digest=digest(asdict(self.config)),
        )


class MachineryState:
    SCHEMA = "Venus.MachineryState.CapabilityPressure.v0.1"

    def __init__(self, config: MachineryConfig | None = None):
        self.config = config or MachineryConfig()
        self.config.validate()

    @property
    def state_digest(self) -> str:
        return digest({"schema": self.SCHEMA, "config": asdict(self.config)})

    def snapshot(self) -> dict[str, Any]:
        return {"schema": self.SCHEMA, "config": asdict(self.config)}

    @classmethod
    def from_snapshot(cls, data: dict[str, Any]) -> "MachineryState":
        if data.get("schema") != cls.SCHEMA:
            raise ValueError("unexpected machinery schema")
        return cls(MachineryConfig(**data["config"]))


class MachineryMembrane:
    """Trajectory-persistent machinery state with fail-closed replay.

    Proposals may be generated locally, but acceptance is bound to an external evaluation
    receipt. The membrane cannot validate its own proposal merely by proposing it.
    """
    PROPOSAL_KIND = "MACHINERY_PROPOSAL"
    RESIDUAL_KIND = "MACHINERY_RESIDUAL"
    EVALUATION_KIND = "MACHINERY_EVALUATION"
    COMMIT_KIND = "MACHINERY_COMMIT"
    VERSION = "CAPABILITY_PRESSURE_MACHINERY_v0.1"

    def __init__(self, vm):
        self.vm = vm
        self.state = MachineryState()
        self._replay()

    def _replay(self) -> None:
        accepted: dict[str, dict[str, Any]] = {}
        for e in self.vm.journal.events:
            kind = e.get("kind")
            p = e.get("payload", {})
            if kind == self.EVALUATION_KIND and p.get("accepted") is True:
                accepted[p["proposal_id"]] = p
            elif kind == self.COMMIT_KIND:
                proposal_id = p.get("proposal_id")
                if proposal_id not in accepted:
                    raise RuntimeError("machinery commit without accepted external evaluation")
                self.state = MachineryState.from_snapshot(p["state"])
                if self.state.state_digest != p.get("state_digest"):
                    raise RuntimeError("machinery commit digest mismatch")

    def retain_residual(self, world: PressureWorld, returned: WorldReturn) -> ResidualRecord:
        trace = {
            "world_id": world.id,
            "turns": [(t.kind, list(t.tokens)) for t in world.turns],
            "answer": returned.answer,
            "success": returned.success,
        }
        rid = digest({"kind": "capability-pressure-residual", "trace": trace, "state": self.state.state_digest})
        rec = ResidualRecord(rid, world.id, digest(trace), self.state.state_digest, returned.success)
        self.vm.record_interface_event(
            self.RESIDUAL_KIND,
            {**asdict(rec), "version": self.VERSION},
            route=("World^4", "returned-failure", "Residual", "machinery-search"),
            source="capability-pressure-world",
        )
        return rec

    def candidate_proposals(self) -> tuple[MachineryProposal, ...]:
        """Generic local mutation grammar; no task-family or answer-specific branches."""
        parent = self.state.state_digest
        c = self.state.config
        candidates: list[tuple[str, MachineryConfig]] = []
        if c.recent_capacity < 16:
            for step in (1, 3):
                nr = min(16, c.recent_capacity + step)
                if nr != c.recent_capacity:
                    candidates.append((f"recent_capacity+{step}", MachineryConfig(nr, c.associative_memory, c.binding_capacity)))
        if not c.associative_memory:
            candidates.append(("enable_associative_memory", MachineryConfig(c.recent_capacity, True, max(2, c.binding_capacity))))
        elif c.binding_capacity < 32:
            for step in (1, 3):
                nb = min(32, c.binding_capacity + step)
                candidates.append((f"binding_capacity+{step}", MachineryConfig(c.recent_capacity, True, nb)))
        # deterministic de-duplication by config digest
        out=[]; seen=set()
        for mutation, cand in candidates:
            cand.validate(); cd=digest(asdict(cand))
            if cd in seen: continue
            seen.add(cd)
            pid=digest({"parent":parent,"candidate":asdict(cand),"mutation":mutation})
            out.append(MachineryProposal(pid,parent,cand,mutation))
        return tuple(out)

    @staticmethod
    def score(config: MachineryConfig, worlds: Iterable[PressureWorld]) -> float:
        rows=tuple(worlds)
        if not rows:
            return 0.0
        good=0
        for w in rows:
            if BoundedTaskMachine(config).run(w).success:
                good += 1
        return good/len(rows)

    def evaluate_proposal(self, proposal: MachineryProposal, worlds: Iterable[PressureWorld], *, min_gain: float = 0.20) -> MachineryEvaluation:
        rows=tuple(worlds)
        baseline=self.score(self.state.config, rows)
        candidate=self.score(proposal.candidate, rows)
        ev=MachineryEvaluation(
            proposal.id, baseline, candidate, candidate-baseline,
            (candidate-baseline) >= min_gain,
            tuple(w.id for w in rows),
        )
        self.vm.record_interface_event(
            self.EVALUATION_KIND,
            {**asdict(ev), "version": self.VERSION, "evaluator": "external-matched-capability-pressure-v0.1"},
            route=("sandbox", "external-evaluation", "retain-revise-reject"),
            source="external-evaluator",
        )
        return ev

    def record_proposal(self, proposal: MachineryProposal) -> None:
        self.vm.record_interface_event(
            self.PROPOSAL_KIND,
            {"id": proposal.id, "parent_digest": proposal.parent_digest, "candidate": asdict(proposal.candidate), "mutation": proposal.mutation, "version": self.VERSION},
            route=("Residual", "candidate-machinery", "sandbox"),
            source="organism-machinery-search",
        )

    def commit(self, proposal: MachineryProposal, evaluation: MachineryEvaluation) -> str:
        if evaluation.proposal_id != proposal.id or not evaluation.accepted:
            raise ValueError("cannot commit machinery without matching accepted evaluation")
        # Fail closed if state moved since proposal generation.
        if proposal.parent_digest != self.state.state_digest:
            raise RuntimeError("stale machinery proposal")
        new_state=MachineryState(proposal.candidate)
        self.vm.record_interface_event(
            self.COMMIT_KIND,
            {"proposal_id": proposal.id, "evaluation": asdict(evaluation), "state": new_state.snapshot(), "state_digest": new_state.state_digest, "version": self.VERSION, "project_state_write": False},
            route=("external-validation", "provenance-bound-commit", "MachineryState"),
            source="governed-machinery-commit",
        )
        self.state = new_state
        return self.state.state_digest


def make_pressure_worlds(*, split: str, count: int = 24, delay: int = 4) -> tuple[PressureWorld, ...]:
    """Deterministic bounded worlds with arbitrary keys/values and intervening noise."""
    rows=[]
    for i in range(count):
        key=f"k{(i*7+3)%101}"
        value=f"v{(i*11+5)%127}"
        turns=[PressureTurn("PUT",(key,value))]
        for j in range(delay + (i % 3)):
            turns.append(PressureTurn("NOISE",(f"n{i}_{j}",)))
        # Interleave unrelated binding to defeat single-slot recent retention.
        other=f"x{(i*13+1)%97}"; oval=f"y{(i*17+2)%109}"
        turns.append(PressureTurn("PUT",(other,oval)))
        turns.append(PressureTurn("GET",(key,)))
        rows.append(PressureWorld(f"{split}-{i:03d}",tuple(turns),value,split))
    return tuple(rows)
