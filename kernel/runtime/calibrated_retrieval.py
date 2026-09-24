from __future__ import annotations

"""Generic calibrated nearest-neighbor semantic ingress.

This executor is project-blind. Method choice is supplied as state data.
Calibration labels are external returned observations. Hidden evaluation rows
must arrive without labels.
"""

from dataclasses import dataclass
import re
from typing import Iterable, Mapping


class CalibratedRetrievalError(ValueError):
    pass


@dataclass(frozen=True)
class LabeledExample:
    example_id: str
    text: str
    label: str
    provenance_id: str


@dataclass(frozen=True)
class Prediction:
    label: str | None
    status: str
    neighbors: tuple[str, ...]
    scores: tuple[float, ...]


def _word_features(text: str) -> frozenset[str]:
    return frozenset(re.findall(r"[A-Za-z0-9]+", text.casefold()))


def _char_features(text: str, n: int) -> frozenset[str]:
    value = " ".join(text.casefold().split())
    if len(value) < n:
        return frozenset((value,)) if value else frozenset()
    return frozenset(value[i:i+n] for i in range(len(value)-n+1))


def _features(text: str, method: Mapping[str, object]) -> frozenset[str]:
    family = str(method.get("family"))
    if family == "WORD_SET_JACCARD":
        return _word_features(text)
    if family == "CHAR_NGRAM_JACCARD":
        n = int(method.get("n", 0))
        if n < 2:
            raise CalibratedRetrievalError("char n must be >=2")
        return _char_features(text, n)
    raise CalibratedRetrievalError(f"unsupported retrieval family: {family}")


def _jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    union = a | b
    return 0.0 if not union else len(a & b) / len(union)


def predict(
    method: Mapping[str, object],
    calibration: Iterable[LabeledExample],
    text: str,
) -> Prediction:
    rows = tuple(calibration)
    if not rows:
        raise CalibratedRetrievalError("calibration return required")
    if any(not r.provenance_id for r in rows):
        raise CalibratedRetrievalError("calibration provenance required")
    k = int(method.get("k", 0))
    if k <= 0:
        raise CalibratedRetrievalError("k must be positive")
    target = _features(text, method)
    ranked = []
    for row in rows:
        ranked.append((_jaccard(target, _features(row.text, method)), row.example_id, row.label))
    ranked.sort(key=lambda x: (-x[0], x[1]))
    chosen = ranked[:min(k, len(ranked))]
    weights: dict[str, float] = {}
    for score, _, label in chosen:
        weights[label] = weights.get(label, 0.0) + score
    total = sum(weights.values())
    if total <= 0.0:
        return Prediction(None, "WITHHOLD_NO_SIMILAR_RETURN", tuple(x[1] for x in chosen), tuple(x[0] for x in chosen))
    best = max(weights.values())
    winners = sorted(label for label, weight in weights.items() if abs(weight-best) < 1e-12)
    if len(winners) != 1:
        return Prediction(None, "WITHHOLD_AMBIGUOUS_RETURN", tuple(x[1] for x in chosen), tuple(x[0] for x in chosen))
    return Prediction(winners[0], "PREDICTED_FROM_RETURNED_CALIBRATION", tuple(x[1] for x in chosen), tuple(x[0] for x in chosen))


def leave_one_out(
    method: Mapping[str, object],
    examples: Iterable[LabeledExample],
) -> dict:
    rows = tuple(examples)
    if len(rows) < 2:
        raise CalibratedRetrievalError("leave-one-out requires >=2 examples")
    labels = tuple(sorted({r.label for r in rows}))
    correct = 0
    per_label = {label: {"tp":0, "fp":0, "fn":0} for label in labels}
    withholds = 0
    predictions = []
    for i, row in enumerate(rows):
        train = rows[:i] + rows[i+1:]
        out = predict(method, train, row.text)
        pred = out.label
        predictions.append({"id":row.example_id, "gold":row.label, "prediction":pred, "status":out.status})
        if pred is None:
            withholds += 1
            per_label[row.label]["fn"] += 1
            continue
        if pred == row.label:
            correct += 1
            per_label[row.label]["tp"] += 1
        else:
            per_label[pred]["fp"] += 1
            per_label[row.label]["fn"] += 1
    f1s = []
    for label in labels:
        m = per_label[label]
        p = 0.0 if (m["tp"]+m["fp"]) == 0 else m["tp"]/(m["tp"]+m["fp"])
        r = 0.0 if (m["tp"]+m["fn"]) == 0 else m["tp"]/(m["tp"]+m["fn"])
        f1s.append(0.0 if (p+r)==0 else 2*p*r/(p+r))
    return {
        "n":len(rows),
        "accuracy":correct/len(rows),
        "macro_f1":sum(f1s)/len(f1s),
        "withholds":withholds,
        "predictions":predictions,
    }
