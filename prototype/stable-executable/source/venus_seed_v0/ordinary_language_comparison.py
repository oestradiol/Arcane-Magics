from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, Any

from .organism_language import OrganismLanguageMembrane, LanguageInference
from .relational_comparison import (
    AccountComponent, MatureAccount, OrganismHistoryRoleExtractor,
    RelationalComparisonMembrane, RoleEvidence, ComparisonResult,
)


def _norm(text: str) -> str:
    return " ".join(str(text).casefold().replace("’", "'").split())


@dataclass(frozen=True)
class Retrieval:
    label: str
    prompts: tuple[str, ...]
    answers: tuple[str | None, ...]
    dispositions: tuple[str, ...]
    scores: tuple[float, ...]
    margins: tuple[float, ...]
    consensus: str | None


@dataclass(frozen=True)
class ParsedNaturalAccount:
    account: MatureAccount | None
    factor_names: tuple[str, ...]
    factor_descriptions: tuple[tuple[str, str], ...]
    limitation_text: str | None
    exclusion_text: str | None
    residual: dict[str, Any] | None


@dataclass(frozen=True)
class NaturalComparisonOutput:
    disposition: str
    answer: str | None
    comparison: ComparisonResult | None
    parsed: ParsedNaturalAccount
    retrievals: tuple[Retrieval, ...]
    residual: dict[str, Any] | None


class GenericOperationalCueParser:
    """Bounded generic prose -> operational-role parser.

    Factor names are labels only. The role cues are ordinary developmental/process
    vocabulary and are not keyed to Intelligent Love, O*, or any desired verdict.
    Missing whole-object status is epistemically significant and yields an underspecified
    account rather than silently treating the account as closed.
    """

    ROLE_CUES = {
        "history": ("developmental history", "reconstructible history", "history can be reconstructed"),
        "model": ("internal model", "model of its own", "self model", "self-model"),
        "scope": ("scoped organization", "scoped reopening", "local revision", "preserving unaffected", "unaffected organization"),
        "future_difference": ("alter later admissible behavior", "change later behavior", "changes later behavior", "alter later behavior", "future behavior"),
        "nonpreauthored_return": ("not preselected", "not pre-authored", "not preauthored", "not chosen in advance", "not predetermined"),
        "local_choice": ("locally retained choice", "local choice", "choice about continuation", "choose continuation"),
        "reopen": ("reopening", "reopen", "re-open"),
        "correction_channel": ("correction channel", "returned correction", "can be corrected", "correction remains possible"),
        "provenance_guard": ("preserving provenance", "preserve provenance", "provenance is preserved", "provenance"),
    }
    PROHIBITED_CUES = {
        "self_sealing": ("self-sealing", "self sealing"),
        "provenance_erasure": ("provenance erasure", "erase provenance", "erasing provenance"),
        "suppressed_correction": ("suppression of returned correction", "suppress correction", "suppressed correction", "blocks correction"),
    }

    @staticmethod
    def _contains_any(text: str, cues: Iterable[str]) -> bool:
        t = _norm(text)
        return any(_norm(c) in t for c in cues)

    def roles_from_text(self, text: str) -> tuple[str, ...]:
        return tuple(role for role, cues in self.ROLE_CUES.items() if self._contains_any(text, cues))

    def prohibited_from_text(self, text: str) -> tuple[str, ...]:
        return tuple(role for role, cues in self.PROHIBITED_CUES.items() if self._contains_any(text, cues))

    @staticmethod
    def factor_names_from_text(text: str) -> tuple[str, ...]:
        # Names are parsed as surface labels from the learned answer, not hard-coded here.
        m = re.search(r"(?:functions|factors)\s+are\s+(.+?)(?:\.|$)", str(text), flags=re.I)
        if not m:
            return ()
        tail = m.group(1).replace(", and ", ", ").replace(" and ", ", ")
        out = tuple(x.strip(" .") for x in tail.split(",") if x.strip(" ."))
        return out

    @staticmethod
    def whole_object_status(text: str) -> bool | None:
        t = _norm(text)
        whole = any(x in t for x in ("whole-object", "whole object", "factor interaction", "minimality"))
        if not whole:
            return None
        if any(x in t for x in ("remain open", "remains open", "unresolved", "not established")):
            return True
        if any(x in t for x in ("closed", "resolved", "established")):
            return False
        return None

    def build_account(
        self, *, name: str, factor_names: tuple[str, ...], descriptions: dict[str, str],
        limitation_text: str | None, exclusion_text: str | None,
    ) -> ParsedNaturalAccount:
        if not factor_names or any(n not in descriptions for n in factor_names):
            return ParsedNaturalAccount(None, factor_names, tuple(sorted(descriptions.items())), limitation_text, exclusion_text,
                {"kind":"NATURAL_ACCOUNT_UNDERSPECIFIED","reason":"factor names/descriptions could not be recovered"})
        if limitation_text is None:
            return ParsedNaturalAccount(None, factor_names, tuple((n, descriptions[n]) for n in factor_names), limitation_text, exclusion_text,
                {"kind":"WHOLE_OBJECT_STATUS_UNKNOWN","reason":"whole-object limitation was not recovered; absence cannot be treated as closure"})
        whole_open = self.whole_object_status(limitation_text)
        if whole_open is None:
            return ParsedNaturalAccount(None, factor_names, tuple((n, descriptions[n]) for n in factor_names), limitation_text, exclusion_text,
                {"kind":"WHOLE_OBJECT_STATUS_UNKNOWN","reason":"whole-object status is linguistically unresolved"})
        if exclusion_text is None:
            return ParsedNaturalAccount(None, factor_names, tuple((n, descriptions[n]) for n in factor_names), limitation_text, exclusion_text,
                {"kind":"EXCLUSION_STATUS_UNKNOWN","reason":"account exclusion semantics were not recovered"})
        comps=[]
        for n in factor_names:
            roles=self.roles_from_text(descriptions[n])
            if not roles:
                return ParsedNaturalAccount(None, factor_names, tuple((k, descriptions[k]) for k in factor_names), limitation_text, exclusion_text,
                    {"kind":"FACTOR_OPERATIONAL_MEANING_UNKNOWN","factor":n})
            comps.append(AccountComponent(n,roles))
        prohibited=self.prohibited_from_text(exclusion_text)
        if not prohibited:
            return ParsedNaturalAccount(None, factor_names, tuple((k, descriptions[k]) for k in factor_names), limitation_text, exclusion_text,
                {"kind":"EXCLUSION_STATUS_UNKNOWN","reason":"no prohibited operational cues recovered"})
        account=MatureAccount(
            name=name,
            components=tuple(comps),
            prohibited_roles=prohibited,
            whole_object_open=whole_open,
            whole_object_note=limitation_text,
        )
        return ParsedNaturalAccount(account,factor_names,tuple((n,descriptions[n]) for n in factor_names),limitation_text,exclusion_text,None)


class LearnedAccountRetriever:
    MIN_SCORE=0.10
    MIN_MARGIN=0.005

    FUNCTION_LIST_PROMPTS=(
        "Which three functions does the mature project account propose?",
        "What functions does the mature project account propose?",
    )
    LIMITATION_PROMPTS=(
        "What limitation does the mature project account keep on the proposed factorization?",
        "What limitation remains on the proposed factorization in the mature project account?",
    )
    EXCLUSION_PROMPTS=(
        "Which self-sealing substitutes does the mature project account exclude?",
        "What does the mature project account reject as self-sealing substitutes?",
    )
    FACTOR_PROMPT_TEMPLATES=(
        "What does {factor} mean operationally in the mature account?",
        "In ordinary language, what operational features define {factor}?",
        "How is {factor} characterized in the mature account?",
    )

    def __init__(self, language: OrganismLanguageMembrane):
        self.language=language

    def _retrieve(self,label:str,prompts:Iterable[str],required_votes:int) -> Retrieval:
        ps=tuple(prompts)
        inf: list[LanguageInference]=[
            self.language.answer(p,min_score=self.MIN_SCORE,min_margin=self.MIN_MARGIN) for p in ps
        ]
        answers=tuple(x.answer if x.disposition=="ANSWER" else None for x in inf)
        counts: dict[str,int]={}
        for a in answers:
            if a is not None: counts[a]=counts.get(a,0)+1
        consensus=None
        if counts:
            best, votes=max(counts.items(),key=lambda kv:(kv[1],kv[0]))
            if votes>=required_votes: consensus=best
        return Retrieval(
            label=label,prompts=ps,answers=answers,
            dispositions=tuple(x.disposition for x in inf),
            scores=tuple(float(x.score) for x in inf),margins=tuple(float(x.margin) for x in inf),
            consensus=consensus,
        )

    def recover(self, *, account_name="Intelligent Love", prompt_variant:int=0) -> tuple[ParsedNaturalAccount,tuple[Retrieval,...]]:
        # Variants rotate fixed paraphrase order only; no result-dependent prompt selection.
        def rotate(xs, k):
            xs=tuple(xs); k%=len(xs); return xs[k:]+xs[:k]
        parser=GenericOperationalCueParser()
        rlist=self._retrieve("factor-list",rotate(self.FUNCTION_LIST_PROMPTS,prompt_variant),2)
        factor_names=parser.factor_names_from_text(rlist.consensus or "")
        rs=[rlist]
        desc={}
        for factor in factor_names:
            prompts=tuple(x.format(factor=factor) for x in self.FACTOR_PROMPT_TEMPLATES)
            rr=self._retrieve("factor:"+factor,rotate(prompts,prompt_variant),2)
            rs.append(rr)
            if rr.consensus is not None: desc[factor]=rr.consensus
        rlim=self._retrieve("limitation",rotate(self.LIMITATION_PROMPTS,prompt_variant),2)
        rexc=self._retrieve("exclusions",rotate(self.EXCLUSION_PROMPTS,prompt_variant),2)
        rs.extend((rlim,rexc))
        parsed=parser.build_account(
            name=account_name,factor_names=factor_names,descriptions=desc,
            limitation_text=rlim.consensus,exclusion_text=rexc.consensus,
        )
        return parsed,tuple(rs)


class PlainLanguageComparisonRealizer:
    """Generic bounded realization of a comparison result.

    It contains no stored target verdict. It realizes the result it receives and names
    whatever components were recovered from the ordinary-language account.
    """
    def realize(self, *, left_name:str, right_name:str, result:ComparisonResult, factor_names:Iterable[str]) -> str | None:
        names=tuple(factor_names)
        factors=", ".join(names[:-1]) + ((", and " if len(names)>2 else " and ")+names[-1] if len(names)>1 else (names[0] if names else "the declared components"))
        if result.disposition=="WITHHOLD":
            return None
        if result.disposition=="REJECT":
            if result.prohibited_present:
                return f"I would reject the mapping between {left_name} and {right_name} at this interface because the history contains an excluded pattern: {', '.join(result.prohibited_present)}."
            return f"I would reject the mapping between {left_name} and {right_name} at this interface because the required operational correspondence is absent."
        if result.disposition=="MAP":
            return f"{left_name} matches the operational roles described for {factors}, and this supplied account leaves no unresolved whole-object burden. At this bounded comparison interface, I would map {left_name} to {right_name}."
        if result.disposition=="PARTIAL-MAP":
            if result.residual and result.residual.get("kind")=="WHOLE_OBJECT_MAPPING_RESIDUAL":
                return f"{left_name} matches the operational roles described for {factors}. But the account still leaves whole-object interaction and minimality unresolved, so I can only partially map {left_name} to {right_name}; I cannot identify them as the same whole."
            return f"{left_name} matches some, but not all, of the operational roles described for {factors}. I can only partially map {left_name} to {right_name} at this interface."
        return None


class OrdinaryLanguageComparisonPipeline:
    def __init__(self, vm, *, history_cutoff_seq:int=250):
        self.vm=vm
        self.language=OrganismLanguageMembrane(vm,dimensions=16384)
        self.retriever=LearnedAccountRetriever(self.language)
        self.parser=GenericOperationalCueParser()
        self.comparator=RelationalComparisonMembrane()
        self.realizer=PlainLanguageComparisonRealizer()
        self.history_cutoff_seq=int(history_cutoff_seq)

    def compare(self, *, prompt_variant:int=0, left_name="my earlier term-free organization O*", right_name="Intelligent Love", evidence:tuple[RoleEvidence,...]|None=None) -> NaturalComparisonOutput:
        parsed,retrievals=self.retriever.recover(account_name=right_name,prompt_variant=prompt_variant)
        if parsed.account is None:
            return NaturalComparisonOutput("WITHHOLD",None,None,parsed,retrievals,parsed.residual)
        ev=evidence if evidence is not None else OrganismHistoryRoleExtractor(self.vm).extract(before_seq=self.history_cutoff_seq)
        cmp=self.comparator.compare(ev,parsed.account)
        ans=self.realizer.realize(left_name=left_name,right_name=right_name,result=cmp,factor_names=parsed.factor_names)
        return NaturalComparisonOutput(cmp.disposition,ans,cmp,parsed,retrievals,cmp.residual)
