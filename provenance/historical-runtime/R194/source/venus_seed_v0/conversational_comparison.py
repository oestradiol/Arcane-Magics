from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

from .ordinary_language_comparison import OrdinaryLanguageComparisonPipeline, NaturalComparisonOutput
from .relational_comparison import RoleEvidence


def _norm(text: str) -> str:
    return " ".join(str(text).casefold().replace("’", "'").split())


@dataclass(frozen=True)
class ConversationRoute:
    disposition: str
    left_name: str | None
    right_name: str | None
    comparison_cues: tuple[str, ...]
    left_cues: tuple[str, ...]
    right_cues: tuple[str, ...]
    context_resolved: bool
    reason: str


@dataclass(frozen=True)
class ConversationalComparisonOutput:
    disposition: str
    answer: str | None
    route: ConversationRoute
    comparison: NaturalComparisonOutput | None
    residual: dict | None


class BoundedComparisonIntentRouter:
    """Generic bounded dialogue router for relation/comparison questions.

    This router does not contain the target verdict, factor names, factor roles, or the
    Intelligent-Love decomposition. It only decides whether a short dialogue asks for a
    comparison between the earlier term-free organization and the already-admitted mature
    account. Ambiguous or unrelated dialogue fails closed.
    """

    COMPARE_CUES = (
        "same", "identical", "equal", "equivalent", "amount to", "map", "match",
        "correspond", "overlap", "relation", "relate", "compare", "comparison",
        "how far", "how much", "basically", "identify", "alignment", "line up",
    )
    LEFT_CUES = (
        "o*", "term-free", "term free", "earlier organization", "earlier structure",
        "old organization", "previous organization", "what existed before",
        "what you built before", "what you reconstructed before", "before the name",
        "before the label", "pre-name", "pre name",
    )
    RIGHT_CUES = (
        "intelligent love", "mature account", "mature project account", "project account",
        "current account", "named account", "thing you now call intelligent love",
        "account you now call intelligent love",
    )
    BOTH_PRONOUN_CUES = ("are they", "do they", "between them", "compare them")
    RIGHT_PRONOUN_CUES = ("amount to it", "equal it", "match it", "map to it", "relate to it")

    @staticmethod
    def _hits(text: str, cues: Iterable[str]) -> tuple[str, ...]:
        t = _norm(text)
        return tuple(c for c in cues if c in t)

    def route(self, turns: Iterable[str]) -> ConversationRoute:
        raw = tuple(str(t) for t in turns if str(t).strip())
        if not raw:
            return ConversationRoute("WITHHOLD", None, None, (), (), (), False, "empty conversation")
        joined = " \n ".join(raw)
        last = raw[-1]
        comparison = self._hits(last, self.COMPARE_CUES)
        left_all = self._hits(joined, self.LEFT_CUES)
        right_all = self._hits(joined, self.RIGHT_CUES)
        left_last = self._hits(last, self.LEFT_CUES)
        right_last = self._hits(last, self.RIGHT_CUES)
        context_resolved = False

        # Two-turn anaphora is licensed only when earlier turns contain explicit referents.
        prior = " \n ".join(raw[:-1])
        prior_left = bool(self._hits(prior, self.LEFT_CUES))
        prior_right = bool(self._hits(prior, self.RIGHT_CUES))
        last_norm = _norm(last)
        both_pronoun = any(c in last_norm for c in self.BOTH_PRONOUN_CUES)
        right_pronoun = any(c in last_norm for c in self.RIGHT_PRONOUN_CUES)
        if both_pronoun and prior_left and prior_right:
            context_resolved = True
            left_last = left_last or ("context:left",)
            right_last = right_last or ("context:right",)
        elif right_pronoun and bool(left_last or prior_left) and prior_right:
            context_resolved = True
            right_last = right_last or ("context:right",)

        left_present = bool(left_last or (prior_left and context_resolved))
        right_present = bool(right_last or (prior_right and context_resolved))
        if not comparison:
            return ConversationRoute("WITHHOLD", None, None, (), left_all, right_all, context_resolved,
                                     "no comparison relation requested")
        if not left_present or not right_present:
            missing = []
            if not left_present: missing.append("earlier term-free organization")
            if not right_present: missing.append("mature account")
            return ConversationRoute("WITHHOLD", None, None, comparison, left_all, right_all, context_resolved,
                                     "missing comparison referent: " + ", ".join(missing))
        right_name = "Intelligent Love" if "intelligent love" in _norm(joined) else "the mature project account"
        return ConversationRoute(
            "ROUTE",
            "my earlier term-free organization O*",
            right_name,
            comparison,
            left_all,
            right_all,
            context_resolved,
            "bounded comparison intent with both referents resolved",
        )


class ConversationalComparisonPipeline:
    """Bounded short-dialogue front end over the R146 ordinary-language comparison.

    It adds no new account facts and teaches no mapping answer. Once a comparison request is
    routed, the mature account is still reconstructed from organism-owned learned prose and
    compared against pre-T10 organism history by the inherited R146 machinery.
    """

    def __init__(self, vm, *, history_cutoff_seq: int = 250):
        self.vm = vm
        self.router = BoundedComparisonIntentRouter()
        self.pipeline = OrdinaryLanguageComparisonPipeline(vm, history_cutoff_seq=history_cutoff_seq)

    def compare(self, turns: Iterable[str], *, evidence: tuple[RoleEvidence, ...] | None = None) -> ConversationalComparisonOutput:
        route = self.router.route(turns)
        if route.disposition != "ROUTE":
            return ConversationalComparisonOutput("WITHHOLD", None, route, None,
                {"kind": "CONVERSATIONAL_COMPARISON_UNRESOLVED", "reason": route.reason})
        out = self.pipeline.compare(
            left_name=route.left_name or "my earlier term-free organization O*",
            right_name=route.right_name or "the mature project account",
            evidence=evidence,
        )
        return ConversationalComparisonOutput(out.disposition, out.answer, route, out, out.residual)
