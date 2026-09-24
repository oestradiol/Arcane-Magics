from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .ordinary_language_comparison import OrdinaryLanguageComparisonPipeline, NaturalComparisonOutput
from .relational_comparison import RoleEvidence
from .conversational_comparison import BoundedComparisonIntentRouter, _norm


@dataclass(frozen=True)
class DiscourseRoute:
    disposition: str
    left_name: str | None
    right_name: str | None
    comparison_cues: tuple[str, ...]
    context_turns_used: tuple[int, ...]
    left_turns: tuple[int, ...]
    right_turns: tuple[int, ...]
    alias_cues: tuple[str, ...]
    cleared: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class MultiTurnComparisonOutput:
    disposition: str
    answer: str | None
    route: DiscourseRoute
    comparison: NaturalComparisonOutput | None
    residual: dict | None


class CompositionalDiscourseRouter:
    """Bounded multi-turn discourse resolver over two already-admitted comparison referents.

    The router stores no target verdict, factor names, operational roles, or account facts.
    It only carries two discourse referents across turns and decides whether the final live
    question requests a comparison. Ambiguous, cleared, or under-specified contexts fail closed.
    """

    CLEAR_LEFT = ("forget the earlier organization", "drop the earlier organization", "clear the first object")
    CLEAR_RIGHT = ("forget intelligent love", "forget the mature account", "drop the mature account", "clear the second object")
    CLEAR_BOTH = ("forget both", "clear both objects", "drop both objects", "reset the comparison")
    FIRST_CUES = ("first object", "the first", "former", "first one")
    SECOND_CUES = ("second object", "the second", "latter", "second one")
    BOTH_CUES = ("they", "them", "the two", "both objects", "both of them", "between the two")

    def __init__(self):
        self.base = BoundedComparisonIntentRouter()

    @staticmethod
    def _contains(text: str, cues: Iterable[str]) -> tuple[str, ...]:
        t = _norm(text)
        return tuple(c for c in cues if c in t)

    def route(self, turns: Iterable[str]) -> DiscourseRoute:
        raw = tuple(str(t) for t in turns if str(t).strip())
        if not raw:
            return DiscourseRoute("WITHHOLD", None, None, (), (), (), (), (), (), "empty conversation")

        left_live = False
        right_live = False
        left_turns: list[int] = []
        right_turns: list[int] = []
        context_used: set[int] = set()
        alias_cues: list[str] = []
        cleared: list[str] = []

        # Referents accumulate across discourse. Explicit clearing is honored prospectively.
        for i, turn in enumerate(raw):
            t = _norm(turn)
            if self._contains(t, self.CLEAR_BOTH):
                left_live = right_live = False
                left_turns.clear(); right_turns.clear(); cleared.extend(("left", "right"))
                continue
            clear_left = bool(self._contains(t, self.CLEAR_LEFT))
            clear_right = bool(self._contains(t, self.CLEAR_RIGHT))
            if clear_left:
                left_live = False; left_turns.clear(); cleared.append("left")
            if clear_right:
                right_live = False; right_turns.clear(); cleared.append("right")

            left_hits = () if clear_left else self.base._hits(t, self.base.LEFT_CUES)
            right_hits = () if clear_right else self.base._hits(t, self.base.RIGHT_CUES)
            if left_hits:
                left_live = True; left_turns.append(i)
            if right_hits:
                right_live = True; right_turns.append(i)

            # Generic discourse aliases are licensed only after their referents have appeared.
            f = self._contains(t, self.FIRST_CUES)
            s = self._contains(t, self.SECOND_CUES)
            if f and left_live:
                alias_cues.extend(f); context_used.update(left_turns)
            if s and right_live:
                alias_cues.extend(s); context_used.update(right_turns)

        last = raw[-1]
        last_norm = _norm(last)
        comparison = self.base._hits(last, self.base.COMPARE_CUES)
        if not comparison:
            return DiscourseRoute("WITHHOLD", None, None, (), tuple(sorted(context_used)), tuple(left_turns), tuple(right_turns), tuple(alias_cues), tuple(cleared), "final turn does not request a comparison")

        explicit_left_last = bool(self.base._hits(last, self.base.LEFT_CUES))
        explicit_right_last = bool(self.base._hits(last, self.base.RIGHT_CUES))
        first_last = bool(self._contains(last_norm, self.FIRST_CUES))
        second_last = bool(self._contains(last_norm, self.SECOND_CUES))
        both_last = any(c in last_norm for c in self.BOTH_CUES)

        left_resolved = explicit_left_last or (left_live and (first_last or both_last or len(raw) >= 3))
        right_resolved = explicit_right_last or (right_live and (second_last or both_last or len(raw) >= 3))

        # If context rather than explicit final-turn names supplies a referent, mark its source turns.
        if left_resolved and not explicit_left_last:
            context_used.update(left_turns)
        if right_resolved and not explicit_right_last:
            context_used.update(right_turns)

        if not left_resolved or not right_resolved:
            missing=[]
            if not left_resolved: missing.append("earlier term-free organization")
            if not right_resolved: missing.append("mature account")
            return DiscourseRoute("WITHHOLD", None, None, comparison, tuple(sorted(context_used)), tuple(left_turns), tuple(right_turns), tuple(alias_cues), tuple(cleared), "missing live discourse referent: " + ", ".join(missing))

        # Require actual composed context for the R148 surface: either >=3 turns or explicit aliases.
        if len(raw) < 3 and not alias_cues:
            return DiscourseRoute("WITHHOLD", None, None, comparison, tuple(sorted(context_used)), tuple(left_turns), tuple(right_turns), tuple(alias_cues), tuple(cleared), "R148 multi-turn surface requires composed context")

        right_name = "Intelligent Love" if any("intelligent love" in _norm(x) for x in raw) else "the mature project account"
        return DiscourseRoute(
            "ROUTE",
            "my earlier term-free organization O*",
            right_name,
            comparison,
            tuple(sorted(context_used)), tuple(left_turns), tuple(right_turns), tuple(alias_cues), tuple(cleared),
            "bounded multi-turn comparison with both discourse referents resolved",
        )


class MultiTurnComparisonPipeline:
    """Multi-turn front end over the inherited R146 learned-account comparison machinery."""

    def __init__(self, vm, *, history_cutoff_seq: int = 250):
        self.vm = vm
        self.router = CompositionalDiscourseRouter()
        self.pipeline = OrdinaryLanguageComparisonPipeline(vm, history_cutoff_seq=history_cutoff_seq)

    def compare(self, turns: Iterable[str], *, evidence: tuple[RoleEvidence, ...] | None = None) -> MultiTurnComparisonOutput:
        route = self.router.route(turns)
        if route.disposition != "ROUTE":
            return MultiTurnComparisonOutput("WITHHOLD", None, route, None,
                {"kind":"MULTITURN_COMPARISON_UNRESOLVED","reason":route.reason})
        out = self.pipeline.compare(
            left_name=route.left_name or "my earlier term-free organization O*",
            right_name=route.right_name or "the mature project account",
            evidence=evidence,
        )
        return MultiTurnComparisonOutput(out.disposition, out.answer, route, out, out.residual)
