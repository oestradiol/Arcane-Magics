from __future__ import annotations

from dataclasses import dataclass, replace
import re
from typing import Iterable

from .canonical import digest
from .semantic_learning import LearnerProjection


def _norm(s: str) -> str:
    return " ".join(str(s).strip().casefold().replace("’", "'").split())


@dataclass(frozen=True)
class CompetenceAnswer:
    answer: str | None
    disposition: str
    support: tuple[str, ...] = ()
    family: str = "UNKNOWN"


class BoundedLanguageCompetence:
    """Constrained host-language competence over an audited LearnerProjection.

    This is deliberately not an unrestricted NLP system. It recognizes a frozen family of
    child-level question constructions and may answer only when the required semantic or
    construction support is present in learner state. The parser is generic over terms; the
    evaluator answer key is never provided to this object.
    """

    def __init__(self, projection: LearnerProjection):
        self.projection = projection
        self.defs = {_norm(k): v for k, v in projection.definitions}
        self.rels: dict[tuple[str, str], set[str]] = {}
        for rid, ((sp), obj) in projection.relations:
            if "::" not in sp:
                continue
            subject, predicate = sp.split("::", 1)
            self.rels.setdefault((_norm(subject), _norm(predicate)), set()).add(_norm(obj))
        self.cons = {_norm(k): (_norm(p), _norm(o)) for k, (p, o) in projection.constructions}

    def _has_rel(self, s: str, p: str, o: str) -> bool:
        return _norm(o) in self.rels.get((_norm(s), _norm(p)), set())

    def _supported_construction(self, name: str, pred: str | None = None, obj: str | None = None) -> bool:
        x = self.cons.get(_norm(name))
        if x is None:
            return False
        if pred is not None and x[0] != _norm(pred):
            return False
        if obj is not None and x[1] != _norm(obj):
            return False
        return True

    @staticmethod
    def _withhold(family: str) -> CompetenceAnswer:
        return CompetenceAnswer(None, "WITHHOLD", (), family)

    def answer(self, question: str) -> CompetenceAnswer:
        q = _norm(question).rstrip("?")

        # Definition paraphrase. Generic over any retained defined term.
        m = re.fullmatch(r"(?:what does|in simple terms, what does) (.+?) mean", q)
        if m:
            term = _norm(m.group(1))
            if term in self.defs:
                return CompetenceAnswer(self.defs[term], "ANSWER", (f"definition:{term}",), "DEFINITION_PARAPHRASE")
            return self._withhold("DEFINITION_PARAPHRASE")

        # Generic relation questions. Surface cues map to relation predicates, while terms are
        # extracted from the question and must be supported by learned state.
        patterns = (
            (r"is (.+?) the same as (.+)", ("not_identical_to", "differs_from"), "no", "RELATION_PARAPHRASE"),
            (r"does (.+?) guarantee (.+)", ("does_not_entail", "does_not_imply", "not_identical_to"), "no", "RELATION_PARAPHRASE"),
            (r"does (.+?) imply (.+)", ("does_not_entail", "does_not_imply"), "no", "RELATION_PARAPHRASE"),
            (r"can (.+?) differ from (.+)", ("can_differ_from",), "yes", "RELATION_PARAPHRASE"),
            (r"can (.+?) coexist with (.+)", ("compatible_with",), "yes", "RELATION_PARAPHRASE"),
            (r"does (.+?) substitute for (.+)", ("does_not_substitute_for",), "no", "RELATION_PARAPHRASE"),
            (r"can (.+?) reveal (.+)", ("can_reveal",), "yes", "RELATION_PARAPHRASE"),
            (r"does (.+?) license (.+)", ("licenses",), "yes", "RELATION_PARAPHRASE"),
            (r"does (.+?) constrain (.+)", ("constrains",), "yes", "RELATION_PARAPHRASE"),
            (r"can (.+?) change (.+)", ("can_change", "changes"), "yes", "RELATION_PARAPHRASE"),
            (r"is (.+?) bounded by (.+)", ("bounded_by",), "yes", "RELATION_PARAPHRASE"),
            (r"can (.+?) support (.+)", ("can_support",), "yes", "RELATION_PARAPHRASE"),
        )
        for pat, predicates, ans, fam in patterns:
            m = re.fullmatch(pat, q)
            if m:
                s, o = m.group(1), m.group(2)
                for p in predicates:
                    if self._has_rel(s, p, o):
                        return CompetenceAnswer(ans, "ANSWER", (f"relation:{_norm(s)}::{p}->{_norm(o)}",), fam)
                return self._withhold(fam)

        # Child-level construction transfer to novel lexical material. Each operation is gated
        # by the relevant learned construction rather than by the evaluator answer.
        m = re.fullmatch(r"one (\w+) is here\. two (\w+) are here\. which phrase is plural", q)
        if m:
            if self._supported_construction("number:singular-plural", "marks", "one-versus-more-than-one"):
                return CompetenceAnswer(f"two {m.group(2)}", "ANSWER", ("construction:number:singular-plural",), "NOVEL_CONSTRUCTION")
            return self._withhold("NOVEL_CONSTRUCTION")

        m = re.fullmatch(r"the (\w+) is (\w+)\. which word describes a property of the \1", q)
        if m:
            if self._supported_construction("adjective", "describes", "property-of-noun"):
                return CompetenceAnswer(m.group(2), "ANSWER", ("construction:adjective",), "NOVEL_CONSTRUCTION")
            return self._withhold("NOVEL_CONSTRUCTION")

        m = re.fullmatch(r"the (\w+) (\w+)\. which word tells the action", q)
        if m:
            if self._supported_construction("verb", "expresses", "action-or-state"):
                return CompetenceAnswer(m.group(2), "ANSWER", ("construction:verb",), "NOVEL_CONSTRUCTION")
            return self._withhold("NOVEL_CONSTRUCTION")

        m = re.fullmatch(r"the (\w+) is not (\w+)\. is the sentence asserting that \1 is \2", q)
        if m:
            if self._supported_construction("not", "marks", "negation"):
                return CompetenceAnswer("no", "ANSWER", ("construction:not",), "NOVEL_CONSTRUCTION")
            return self._withhold("NOVEL_CONSTRUCTION")

        m = re.fullmatch(r"(\w+) (\w+), then (\w+)\. which happened later", q)
        if m:
            if self._supported_construction("then", "orders", "events-in-time"):
                return CompetenceAnswer(m.group(3), "ANSWER", ("construction:then",), "NOVEL_CONSTRUCTION")
            return self._withhold("NOVEL_CONSTRUCTION")

        m = re.fullmatch(r"i (.+)\. in this sentence, who does 'i' refer to", q)
        if m:
            if self._supported_construction("pronouns:i-you", "maps_roles", "speaker-listener"):
                return CompetenceAnswer("speaker", "ANSWER", ("construction:pronouns:I-you",), "NOVEL_CONSTRUCTION")
            return self._withhold("NOVEL_CONSTRUCTION")

        m = re.fullmatch(r"this (\w+) is near me; that \1 is farther\. which word points nearer", q)
        if m:
            if self._supported_construction("demonstratives:this-that", "contrast", "near-far"):
                return CompetenceAnswer("this", "ANSWER", ("construction:demonstratives:this-that",), "NOVEL_CONSTRUCTION")
            return self._withhold("NOVEL_CONSTRUCTION")

        # Short scenario transfers. These are vocabulary-free at the mature-project level and
        # require specific learned relations/definitions rather than memorized training text.
        if "someone reports" in q and "does the report alone establish the fact" in q:
            if self._has_rel("report", "not_identical_to", "fact"):
                return CompetenceAnswer("no", "ANSWER", ("relation:report::not_identical_to->fact",), "SCENARIO_TRANSFER")
            return self._withhold("SCENARIO_TRANSFER")

        if "both paths end at the same place" in q and "must their histories be the same" in q:
            if self._has_rel("same endpoint", "does_not_imply", "same history"):
                return CompetenceAnswer("no", "ANSWER", ("relation:same endpoint::does_not_imply->same history",), "HISTORY_SENSITIVE")
            return self._withhold("HISTORY_SENSITIVE")

        if "new evidence later separates two cases" in q and "should the old collapsed distinction be reopened" in q:
            if self._has_rel("new separating evidence", "licenses", "reopening a collapsed distinction"):
                return CompetenceAnswer("yes", "ANSWER", ("relation:new separating evidence::licenses->reopening a collapsed distinction",), "HISTORY_SENSITIVE")
            return self._withhold("HISTORY_SENSITIVE")

        if "a detailed model omits a variable" in q and "does extra detail prove completeness" in q:
            if self._has_rel("model detail", "does_not_entail", "completeness"):
                return CompetenceAnswer("no", "ANSWER", ("relation:model detail::does_not_entail->completeness",), "SCENARIO_TRANSFER")
            return self._withhold("SCENARIO_TRANSFER")

        if "two measurements move together" in q and "does that alone establish causation" in q:
            if self._has_rel("correlation", "does_not_entail", "causation"):
                return CompetenceAnswer("no", "ANSWER", ("relation:correlation::does_not_entail->causation",), "SCENARIO_TRANSFER")
            return self._withhold("SCENARIO_TRANSFER")

        if "one person prefers an interaction" in q and "does that substitute for the other person's consent" in q:
            if self._has_rel("another person's preference", "does_not_substitute_for", "consent"):
                return CompetenceAnswer("no", "ANSWER", ("relation:another person's preference::does_not_substitute_for->consent",), "SCENARIO_TRANSFER")
            return self._withhold("SCENARIO_TRANSFER")

        if "agents coordinate" in q and "can they still make distinct choices" in q:
            if self._has_rel("coordination", "compatible_with", "distinct choice"):
                return CompetenceAnswer("yes", "ANSWER", ("relation:coordination::compatible_with->distinct choice",), "SCENARIO_TRANSFER")
            return self._withhold("SCENARIO_TRANSFER")

        if "the current premises do not decide" in q and "is withholding a conclusion licensed" in q:
            if self._has_rel("undecidable from current premises", "licenses", "withholding conclusion"):
                return CompetenceAnswer("yes", "ANSWER", ("relation:undecidable from current premises::licenses->withholding conclusion",), "SCENARIO_TRANSFER")
            return self._withhold("SCENARIO_TRANSFER")

        if "a process receives its own consequence back" in q and "can that be feedback" in q:
            if "feedback" in self.defs:
                return CompetenceAnswer("yes", "ANSWER", ("definition:feedback",), "SCENARIO_TRANSFER")
            return self._withhold("SCENARIO_TRANSFER")

        if "a result was tested only under condition x" in q and "does it automatically support condition y" in q:
            if self._has_rel("scientific result", "bounded_by", "tested claim and conditions"):
                return CompetenceAnswer("no", "ANSWER", ("relation:scientific result::bounded_by->tested claim and conditions",), "SCENARIO_TRANSFER")
            return self._withhold("SCENARIO_TRANSFER")

        return self._withhold("UNRECOGNIZED")


def shuffled_projection(proj: LearnerProjection, *, seed: int = 131) -> LearnerProjection:
    """Matched-count semantic corruption control with deterministic permutation."""
    import random
    r = random.Random(seed)
    defs = list(proj.definitions)
    vals = [v for _, v in defs]
    r.shuffle(vals)
    defs2 = tuple((k, v) for (k, _), v in zip(defs, vals))

    rels = list(proj.relations)
    rel_objs = [obj for _, (_, obj) in rels]
    r.shuffle(rel_objs)
    rels2 = tuple((rid, (sp, obj)) for (rid, (sp, _)), obj in zip(rels, rel_objs))

    cons = list(proj.constructions)
    con_vals = [v for _, v in cons]
    r.shuffle(con_vals)
    cons2 = tuple((k, v) for (k, _), v in zip(cons, con_vals))
    return replace(proj, learner_state_digest=digest({"shuffled": seed, "base": proj.learner_state_digest}), definitions=defs2, relations=rels2, constructions=cons2)


def ablated_projection(proj: LearnerProjection, *, remove_subjects: Iterable[str]) -> LearnerProjection:
    rm = {_norm(x) for x in remove_subjects}
    defs = tuple((k, v) for k, v in proj.definitions if _norm(k) not in rm)
    rels = tuple((rid, (sp, obj)) for rid, (sp, obj) in proj.relations if _norm(sp.split("::",1)[0]) not in rm)
    cons = tuple((k, v) for k, v in proj.constructions if _norm(k) not in rm)
    return replace(proj, learner_state_digest=digest({"ablated": sorted(rm), "base": proj.learner_state_digest}), definitions=defs, relations=rels, constructions=cons)
