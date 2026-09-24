from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Iterable

from .semantic_learning import LearnerProjection, SemanticLearningMembrane
from .world_observer import (
    InterpreterAdapter, RealizerAdapter, ObserverProjection, WorldIngress, SemanticCandidate,
)


@dataclass(frozen=True)
class DevelopmentalLanguageProjection:
    observer: ObserverProjection
    learner: LearnerProjection

    def __post_init__(self):
        if self.observer.trajectory_head != self.learner.trajectory_head:
            raise ValueError("observer/learner projections are not bound to the same trajectory head")


class LearningAwareInterpreter(Protocol):
    def interpret(self, ingress: WorldIngress, projection: DevelopmentalLanguageProjection) -> Iterable[SemanticCandidate]: ...


class LearningAwareRealizer(Protocol):
    def realize(self, request: str, projection: DevelopmentalLanguageProjection) -> str: ...


class InterpreterLearningBridge(InterpreterAdapter):
    """Adapts a learning-aware hosted interpreter to the existing WorldObserver contract."""
    def __init__(self, membrane: SemanticLearningMembrane, hosted: LearningAwareInterpreter):
        self.membrane = membrane
        self.hosted = hosted

    def interpret(self, ingress: WorldIngress, projection: ObserverProjection):
        learner = self.membrane.project()
        joint = DevelopmentalLanguageProjection(projection, learner)
        return self.hosted.interpret(ingress, joint)


class RealizerLearningBridge(RealizerAdapter):
    """Adapts a learning-aware hosted realizer without granting it learner or Canonical writes."""
    def __init__(self, membrane: SemanticLearningMembrane, hosted: LearningAwareRealizer):
        self.membrane = membrane
        self.hosted = hosted

    def realize(self, request: str, projection: ObserverProjection) -> str:
        learner = self.membrane.project()
        joint = DevelopmentalLanguageProjection(projection, learner)
        return self.hosted.realize(request, joint)


class LearnerProjectionEcho:
    """Deterministic smoke-test realizer. Not a language learner or comprehension claim."""
    def realize(self, request: str, projection: DevelopmentalLanguageProjection) -> str:
        lp = projection.learner
        return (
            f"{request} | learner={lp.learner_state_digest[:12]} "
            f"defs={lp.definition_count} rels={lp.relation_count} "
            f"constructions={lp.construction_count} items={lp.completed_item_count}"
        )
