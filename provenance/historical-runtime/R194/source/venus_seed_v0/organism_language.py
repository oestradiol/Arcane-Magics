from __future__ import annotations

from dataclasses import dataclass
from collections import Counter, defaultdict
import hashlib
import math
import re
from typing import Any, Iterable

from .canonical import digest

_TOKEN_RE = re.compile(r"[\w']+|[^\w\s]", re.UNICODE)


def generic_tokens(text: str) -> tuple[str, ...]:
    """Frozen non-semantic surface tokenizer shared by every arm."""
    return tuple(t.casefold() for t in _TOKEN_RE.findall(str(text)))


def _feature_strings(text: str) -> tuple[str, ...]:
    # Frozen generic lexical surface features only. No semantic dictionaries or task rules.
    toks = generic_tokens(text)
    feats: list[str] = []
    for t in toks:
        feats.append("w:" + t)
    for n in (2, 3):
        for i in range(max(0, len(toks) - n + 1)):
            feats.append(f"w{n}:" + "\u241f".join(toks[i:i+n]))
    return tuple(feats)


def hashed_surface_vector(text: str, *, dimensions: int = 4096) -> dict[int, float]:
    if dimensions < 128:
        raise ValueError("dimensions must be >=128")
    counts: Counter[int] = Counter()
    for feat in _feature_strings(text):
        h = int.from_bytes(hashlib.blake2s(feat.encode("utf-8"), digest_size=4).digest(), "big")
        counts[h % dimensions] += 1
    norm = math.sqrt(sum(v*v for v in counts.values())) or 1.0
    return {k: v / norm for k, v in counts.items()}


def sparse_dot(a: dict[int, float], b: dict[int, float]) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(v * b.get(k, 0.0) for k, v in a.items())


@dataclass(frozen=True)
class LanguageInference:
    disposition: str
    answer: str | None
    score: float
    margin: float
    state_digest: str
    support_count: int


class RepSysLanguageState:
    """Persistent organism-owned learned surface->response association state.

    The learner has no question templates, semantic predicates, project synonym tables,
    or intent labels. Its only fixed host-facing operation is generic feature extraction.
    All response selection parameters are learned from raw dialogue/correction episodes.
    """

    SCHEMA = "Venus.RepSys.LanguageState.R134.v0.1"

    def __init__(self, *, dimensions: int = 4096):
        self.dimensions = int(dimensions)
        self.prototype_sums: dict[str, dict[int, float]] = {}
        self.prototype_counts: dict[str, int] = {}
        self.episode_ids: set[str] = set()
        self.level_counts: Counter[str] = Counter()
        self.correction_count = 0
        self._centroid_cache: dict[str, dict[int, float]] = {}
        self._digest_cache: str | None = None
        self._idf_cache: dict[int, float] | None = None

    def learn(self, *, episode_id: str, prompt: str, teacher_response: str,
              level: str, correction: bool = False, weight: float = 1.0) -> None:
        if not episode_id or episode_id in self.episode_ids:
            raise ValueError("duplicate/empty language episode id")
        if not str(prompt).strip() or not str(teacher_response).strip():
            raise ValueError("prompt and teacher_response must be non-empty")
        x = hashed_surface_vector(prompt, dimensions=self.dimensions)
        dst = self.prototype_sums.setdefault(teacher_response, {})
        for k, v in x.items():
            dst[k] = dst.get(k, 0.0) + float(weight) * v
        self.prototype_counts[teacher_response] = self.prototype_counts.get(teacher_response, 0) + 1
        self._centroid_cache.clear()
        self._idf_cache = None
        self._digest_cache = None
        self.episode_ids.add(episode_id)
        self.level_counts[str(level)] += 1
        if correction:
            self.correction_count += 1

    def _idf(self) -> dict[int, float]:
        if self._idf_cache is not None:
            return self._idf_cache
        n=max(1,len(self.prototype_sums))
        df: Counter[int] = Counter()
        for vec in self.prototype_sums.values():
            for k in vec:
                df[k] += 1
        self._idf_cache = {k: math.log((n+1)/(v+1))+1.0 for k,v in df.items()}
        return self._idf_cache

    def _centroid(self, response: str) -> dict[int, float]:
        cached = self._centroid_cache.get(response)
        if cached is not None:
            return cached
        src = self.prototype_sums[response]
        idf=self._idf()
        weighted={k:v*idf.get(k,1.0) for k,v in src.items()}
        norm = math.sqrt(sum(v*v for v in weighted.values())) or 1.0
        out = {k: v / norm for k, v in weighted.items()}
        self._centroid_cache[response] = out
        return out

    def infer(self, prompt: str, *, min_score: float = 0.16, min_margin: float = 0.015) -> LanguageInference:
        x0 = hashed_surface_vector(prompt, dimensions=self.dimensions)
        idf=self._idf()
        x={k:v*idf.get(k,1.0) for k,v in x0.items()}
        xnorm=math.sqrt(sum(v*v for v in x.values())) or 1.0
        x={k:v/xnorm for k,v in x.items()}
        if not self.prototype_sums:
            return LanguageInference("WITHHOLD", None, 0.0, 0.0, self.state_digest, 0)
        ranked = sorted(
            ((sparse_dot(x, self._centroid(response)), response) for response in self.prototype_sums),
            reverse=True,
        )
        best_score, best = ranked[0]
        second = ranked[1][0] if len(ranked) > 1 else 0.0
        margin = best_score - second
        if best_score < min_score or margin < min_margin:
            return LanguageInference("WITHHOLD", None, best_score, margin, self.state_digest, 0)
        return LanguageInference(
            "ANSWER", best, best_score, margin, self.state_digest,
            self.prototype_counts.get(best, 0),
        )

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": self.SCHEMA,
            "dimensions": self.dimensions,
            "prototype_sums": {
                r: {str(k): v for k, v in sorted(vec.items())}
                for r, vec in sorted(self.prototype_sums.items())
            },
            "prototype_counts": dict(sorted(self.prototype_counts.items())),
            "episode_ids": sorted(self.episode_ids),
            "level_counts": dict(sorted(self.level_counts.items())),
            "correction_count": self.correction_count,
        }

    @classmethod
    def from_snapshot(cls, data: dict[str, Any]) -> "RepSysLanguageState":
        if data.get("schema") != cls.SCHEMA:
            raise ValueError("unexpected language-state schema")
        obj = cls(dimensions=int(data["dimensions"]))
        obj.prototype_sums = {
            r: {int(k): float(v) for k, v in vec.items()}
            for r, vec in data.get("prototype_sums", {}).items()
        }
        obj.prototype_counts = {str(k): int(v) for k, v in data.get("prototype_counts", {}).items()}
        obj.episode_ids = set(str(x) for x in data.get("episode_ids", []))
        obj.level_counts = Counter({str(k): int(v) for k, v in data.get("level_counts", {}).items()})
        obj.correction_count = int(data.get("correction_count", 0))
        return obj

    @property
    def state_digest(self) -> str:
        if self._digest_cache is None:
            self._digest_cache = digest(self.snapshot())
        return self._digest_cache

    def shuffled_copy(self) -> "RepSysLanguageState":
        """Deterministic comparator: keep learned vectors/counts, rotate response ownership."""
        out = RepSysLanguageState(dimensions=self.dimensions)
        labels = sorted(self.prototype_sums)
        if not labels:
            return out
        rotated = labels[1:] + labels[:1]
        for src, dst in zip(labels, rotated):
            out.prototype_sums[dst] = dict(self.prototype_sums[src])
            out.prototype_counts[dst] = self.prototype_counts[src]
        out.episode_ids = set(self.episode_ids)
        out.level_counts = Counter(self.level_counts)
        out.correction_count = self.correction_count
        return out


@dataclass(frozen=True)
class OrganismLanguageProjection:
    trajectory_head: str
    language_state_digest: str
    episode_count: int
    response_prototype_count: int
    level_counts: tuple[tuple[str, int], ...]
    correction_count: int


class OrganismLanguageMembrane:
    """Trajectory-persistent RepSys.Lang learner.

    Training events contain raw prompt + raw teacher response. Replay reconstructs the
    learned parameters deterministically. Nothing here writes ProjectState or Canonical.
    """

    EVENT_KIND = "ORGANISM_LANGUAGE_LEARN"
    BATCH_EVENT_KIND = "ORGANISM_LANGUAGE_BATCH"
    VERSION = "ORGANISM_LANGUAGE_R134_v0.1"

    def __init__(self, vm, *, dimensions: int = 4096):
        self.vm = vm
        self.state = RepSysLanguageState(dimensions=dimensions)
        self._replay()

    def _replay(self) -> None:
        for e in self.vm.journal.events:
            kind = e.get("kind")
            if kind == self.EVENT_KIND:
                rows = (e.get("payload", {}),)
            elif kind == self.BATCH_EVENT_KIND:
                rows = tuple(e.get("payload", {}).get("episodes", ()))
            else:
                continue
            for p in rows:
                self.state.learn(
                    episode_id=p["episode_id"], prompt=p["prompt"], teacher_response=p["teacher_response"],
                    level=p["level"], correction=bool(p.get("correction", False)), weight=float(p.get("weight", 1.0)),
                )

    def teach(self, *, episode_id: str, prompt: str, teacher_response: str,
              level: str, source_id: str = "curriculum-teacher", correction: bool = False,
              weight: float = 1.0) -> str:
        if episode_id in self.state.episode_ids:
            raise ValueError("episode already learned")
        payload = {
            "version": self.VERSION,
            "episode_id": episode_id,
            "prompt": prompt,
            "teacher_response": teacher_response,
            "level": level,
            "source_id": source_id,
            "correction": bool(correction),
            "weight": float(weight),
            "semantic_slots": None,
            "intent_label": None,
            "project_state_write": False,
        }
        self.vm.record_interface_event(
            self.EVENT_KIND, payload,
            route=("World^4", "raw-dialogue", "RepSys.Lang", "persistent-revision"),
            source=source_id,
        )
        self.state.learn(
            episode_id=episode_id, prompt=prompt, teacher_response=teacher_response,
            level=level, correction=correction, weight=weight,
        )
        return self.state.state_digest


    def teach_batch(self, episodes: Iterable[dict[str, Any]], *, source_id: str = "curriculum-teacher") -> str:
        rows=[]
        seen=set()
        for row in episodes:
            episode_id=str(row["episode_id"])
            if episode_id in self.state.episode_ids or episode_id in seen:
                raise ValueError(f"duplicate language episode id: {episode_id}")
            seen.add(episode_id)
            prompt=str(row["prompt"]); response=str(row["teacher_response"]); level=str(row["level"])
            if not prompt.strip() or not response.strip():
                raise ValueError("batch prompt/teacher_response must be non-empty")
            rows.append({
                "episode_id":episode_id,"prompt":prompt,"teacher_response":response,"level":level,
                "correction":bool(row.get("correction",False)),"weight":float(row.get("weight",1.0)),
                "semantic_slots":None,"intent_label":None,"project_state_write":False,
            })
        payload={"version":self.VERSION,"source_id":source_id,"episode_count":len(rows),"episodes":rows}
        self.vm.record_interface_event(
            self.BATCH_EVENT_KIND,payload,
            route=("World^4","raw-dialogue-batch","RepSys.Lang","persistent-revision"),source=source_id,
        )
        for p in rows:
            self.state.learn(
                episode_id=p["episode_id"],prompt=p["prompt"],teacher_response=p["teacher_response"],
                level=p["level"],correction=p["correction"],weight=p["weight"],
            )
        return self.state.state_digest

    def answer(self, prompt: str, **kwargs) -> LanguageInference:
        return self.state.infer(prompt, **kwargs)

    def project(self) -> OrganismLanguageProjection:
        return OrganismLanguageProjection(
            trajectory_head=self.vm.journal.head,
            language_state_digest=self.state.state_digest,
            episode_count=len(self.state.episode_ids),
            response_prototype_count=len(self.state.prototype_sums),
            level_counts=tuple(sorted(self.state.level_counts.items())),
            correction_count=self.state.correction_count,
        )


class OrganismLanguageRealizer:
    """WorldObserver realizer backed only by organism-owned learned language state."""
    def __init__(self, membrane: OrganismLanguageMembrane):
        self.membrane = membrane

    def _latest_world_input(self) -> str | None:
        for e in reversed(self.membrane.vm.journal.events):
            if e.get("kind") == "WORLD_INPUT":
                return e.get("payload", {}).get("content")
        return None

    def realize(self, request: str, projection) -> str:
        text = self._latest_world_input()
        if not text:
            return "WITHHOLD"
        ans = self.membrane.answer(text)
        return ans.answer if ans.disposition == "ANSWER" and ans.answer else "WITHHOLD"
