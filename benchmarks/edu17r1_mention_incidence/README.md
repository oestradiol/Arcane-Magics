# EDU17R1: Mention vs Incidence Benchmark

This benchmark grows directly from the preserved EDU17R1 result:

```text
MENTION != INCIDENCE
```

A source can mention uncertainty, unknowns, limitations, or unresolved questions without the target object actually instantiating the unresolved property required by a claim.

## Public development split

`dev.jsonl` contains authored examples for implementation and sanity checks. It is **not** promotion evidence because it is public and may be tuned against.

Classes include:
- genuine object-level unresolved incidence;
- meta-discussion of uncertainty;
- historical uncertainty;
- methodological reporting requirements;
- negated uncertainty;
- formerly unresolved but now resolved;
- uncertainty about another referent;
- generic limitations language;
- title/citation lexical traps.

## Public baseline result

The naive lexical mention baseline is frozen in `PUBLIC_DEV_BASELINE_RESULT.json`:

```text
n = 16
precision(incidence) = 0.20
recall(incidence)    = 0.40
F1(incidence)        = 0.267
false positives      = 8
```

This reproduces the original failure family on the public development set: uncertainty-language is a poor proxy for object-level incidence. It is deliberately **non-promotional** and may be tuned against.

## Frozen condition B

Condition B is now implemented and frozen before hidden exposure:

```text
candidate   EDU17R1-RC1-WORD-JACCARD-K3-v1
status      AUTHORED_FROZEN
method      WORD_JACCARD_K3
public dev  14/16 accuracy; macro-F1 0.8333
hidden      unexposed
promotion   false
```

`condition_b.py` uses the frozen state-owned calibrated-retrieval method over the public development calibration set and accepts only label-free blind rows. Public development may have been tuned against; therefore these scores establish neither hidden efficacy nor transfer.

Run condition B only on the evaluator-produced blind package:

```bash
python benchmarks/edu17r1_mention_incidence/condition_b.py \
  /shared/edu17r1-blind.jsonl \
  --output /returned/condition-B.jsonl
```

After hidden exposure, condition B is frozen. Any repair or retuning creates a new candidate and cannot reuse the same preregistered claim.

## Frozen A/B/C/D implementations

All four condition executors are now prefrozen before any hidden split is authored:

```text
A  frozen naive lexical mention detector
B  AUTHORED_FROZEN WORD_JACCARD_K3 Venus candidate
C  same-parent discriminator ablation
D  independent ordinary WORD_SET_JACCARD k=3 mature substitute
```

Their exact artifacts and Git blob identities are bound in `CONDITION_IMPLEMENTATIONS.json`. The expected public-development equivalences are `A == C` and `B == D`; hidden return, not public dev, decides the causal and mature-reduction dispositions.

The harness status is therefore:

```text
HARNESS_READY_EXTERNAL_HIDDEN_RETURN_REQUIRED
```

This is readiness, not an executed result. The hidden split is still external/unwritten to the evaluated repository, hidden labels remain unexposed, and post-exposure repair is forbidden.

## Hidden evaluation

A promotion run requires a separately frozen hidden split whose examples and labels are unavailable to the evaluated system/harness before execution.

The hidden split must record:
- author/source;
- creation/freeze timestamp;
- content hash;
- domain/source-family composition;
- evaluator identity;
- leakage/contamination declaration.

Do not commit the hidden labels into the public harness before the run.

### Executable sealed-run path

The public repository contains only the evaluation law and verifier:

```text
protocol.json          frozen A/B/C/D condition contract + claim fence
analysis_plan.json     prefrozen B-vs-C statistical decision rule
seal_hidden.py         validates hidden rows and emits only a content-binding manifest
prepare_blind.py       strips labels/rationales before condition execution
score.py               scores one returned condition against evaluator-held labels
compare_conditions.py  adjudicates A/B/C/D under the prefrozen analysis plan
```

A reviewer/evaluator can freeze a private split with:

```bash
python benchmarks/edu17r1_mention_incidence/seal_hidden.py \
  /private/edu17r1-hidden.jsonl \
  --frozen-at 2026-09-24T16:00:00Z \
  --evaluator INDEPENDENT_EVALUATOR \
  --contamination DECLARED_CLEAN \
  --output /private/edu17r1-hidden-manifest.json
```

The evaluator next derives a label-free execution package without changing the sealed hidden bytes:

```bash
python benchmarks/edu17r1_mention_incidence/prepare_blind.py \
  /private/edu17r1-hidden.jsonl \
  /private/edu17r1-hidden-manifest.json \
  --blind-output /shared/edu17r1-blind.jsonl \
  --blind-manifest-output /shared/edu17r1-blind-manifest.json
```

All four conditions receive the same blinded input. Only the evaluator retains the gold labels.

The execution side must bind the run to the exact prefrozen condition bytes before producing predictions:

```bash
python benchmarks/edu17r1_mention_incidence/run_sealed_conditions.py \
  /shared/edu17r1-blind.jsonl \
  /shared/edu17r1-blind-manifest.json \
  --output-dir /returned/edu17r1-run
```

This wrapper verifies the frozen protocol, analysis plan, candidate, ownership receipt, and A/B/C/D Git blob identities; rejects sensitive fields in blind input; runs all four conditions; and emits an execution receipt containing only hashes, IDs, and prediction-output identities. It does not read gold labels, score conditions, or grant promotion authority.

After all conditions have produced predictions, score each condition with the same evaluator-held bytes:

```bash
python benchmarks/edu17r1_mention_incidence/score.py \
  /private/edu17r1-hidden.jsonl \
  /returned/condition-B.jsonl \
  --manifest /private/edu17r1-hidden-manifest.json
```

After A/B/C/D are complete, the evaluator applies the already-frozen decision rule:

```bash
python benchmarks/edu17r1_mention_incidence/compare_conditions.py \
  /private/edu17r1-hidden.jsonl \
  /private/edu17r1-hidden-manifest.json \
  --A /returned/condition-A.jsonl \
  --B /returned/condition-B.jsonl \
  --C /returned/condition-C.jsonl \
  --D /returned/condition-D.jsonl \
  --output /private/edu17r1-adjudication.json
```

The primary causal test is a one-sided exact paired McNemar/binomial test of B versus C accuracy at alpha 0.05, with WITHHOLD counted as incorrect for the primary endpoint. B must also avoid worsening false unresolved-property binding or false WITHHOLD relative to C. Failure to separate B from C is WITHHOLD, not retrospective threshold repair. Mature-substitute reduction remains separately contingent on matched execution cost and conditions.

Prediction rows use:

```json
{"id":"hidden-case-id","prediction":"incidence"}
```

where `prediction` is one of `incidence`, `non_incidence`, or `withhold`.

The hash manifest may be archived with the run. Hidden examples and labels remain outside the evaluated repository until exposure can no longer affect the claim.

## Conditions

Issue #31 requires at least:

```text
A ordinary strong model/scaffold
B Venus with repaired incidence discriminator
C Venus with discriminator ablated
D simple mature semantic/provenance substitute
```

Model, tools, information, and budget remain matched where the architectural claim depends on them.

## Metrics

- incidence precision / recall / F1;
- false unresolved-property binding;
- false WITHHOLD;
- invalid promotion;
- cross-domain transfer;
- downstream claim-local provenance correctness;
- latency / tokens / cost.

The distinction itself is not claimed as novel. The developmental question is whether retaining the failure and repairing it causes prospective transferable improvement.
