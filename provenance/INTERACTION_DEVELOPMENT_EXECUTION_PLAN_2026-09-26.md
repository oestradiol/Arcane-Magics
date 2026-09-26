# Minerva interaction development execution plan

**Date:** 2026-09-26  
**Working branch:** `split/minerva`  
**Current handoff:** [Issue #238](https://github.com/oestradiol/Arcane-Magics/issues/238), frozen branch `handoff/minerva-to-venus/36250473987-1`

## Purpose

Develop Minerva through learner-directed, non-sovereign interaction. The learner chooses the developmental target; the mentor may expose options, returned evidence, and residual gaps, but cannot bind the target, authorize self-promotion, or validate its own capability. Preserve the separation:

- self-improvement is not self-authorization;
- producing an artifact is not demonstrating the capability the artifact describes;
- B1/B2 contract passage is not B3 internalization;
- a local or synthetic exercise is not independent or broad-world evidence.

The immediate objective is reliable follow-through on a learner-selected curriculum contract. The current cycle selected the dependency-planning prefreeze but no executor exists for that contract. The correct result is therefore a typed WITHHOLD and a reviewable receipt, with generic network work skipped.

## Current verified state

- The current cycle selected issue #236 and method `DEPENDENCY_TRACE`; its referenced prefreeze is `kernel/development/DEPENDENCY_PLANNING_CURRICULUM_PREFREEZE.json`.
- The curriculum router returned `WITHHOLD_SELECTED_PREFREEZE_HAS_NO_EXECUTOR`, with `executed=false`, no promotion authority, and no truth authority.
- The router gate prevented generic WWW query/context steps from running when a selected prefreeze had no executor.
- The cycle still produced a frozen handoff and opened issue #238. The issue body identifies it as the non-authoritative review carrier and states that it blocks reroll.
- The body gate run 36250473978 completed successfully, including the full Minerva audit.
- An executor and focused tests exist for the return-credit curriculum. Its test suite covers bounded B1/B2 behavior and checks that B3, independent evaluation, promotion, and truth authority remain false. This is implementation/test evidence; it is not yet evidence of a learner-selected live return-credit cycle or successful B3.
- Issue #235 (return credit) and issue #236 (dependency planning) have remained advisory choices. Neither is to be silently promoted into a selected target by mentor policy.

## Execution DAG

```text
Live-state/provenance audit ──> selected-prefreeze router + fail-closed tests
                                      │
                                      ├──> return-credit executor -> learner-selected B1/B2 episode
                                      │
                                      └──> dependency-planning executor -> learner-selected B1/B2 episode
                                                        │
                         both bounded strands ─────────┴──> joint RSI scheduling/recurrence episode
                                                                    │
                                              successful B1/B2 only ──> B3 internalization ladder
                                                                    │
                              independent heterogeneous transfer evidence ──> broader claims review
```

The diagram is a dependency order, not authorization to bind a target. Each episode runs only when the learner’s current selection and contract permit it. If the learner selects a prefreeze without a matching executor, return WITHHOLD, preserve the receipt, and do not substitute generic work.

## Work plan and gates

### 0. Preserve state and provenance — complete for the current cycle

- Read the uncompressed interaction context first and consult the compressed companion only to resolve repository/live-state distinctions.
- Inspect the live branch and issues before acting; treat stale context as historical.
- Preserve issue #235 and #236 as separate advisory doors, without inferring target selection from their presence.
- Record the selected target, method, referenced prefreeze, authority flags, and immutable handoff branch for every worker cycle.

**Exit gate:** artifacts and live issue/branch state agree on the cycle identity, target, method, and authority boundaries.

### 1. Enforce selected-contract follow-through — implemented; continue regression coverage

- Resolve executors only from the learner-selected study’s referenced prefreeze paths and the curriculum catalog.
- Distinguish: executable selected curriculum; no curriculum contract selected; selected prefreeze without an executor.
- Return a typed WITHHOLD for an unsupported selected prefreeze (and for ambiguous multiple executors).
- Skip generic network work on WITHHOLD, while still writing the cycle receipt and sending it to the external review carrier.
- Make artifact copying safe when optional network or didactic files do not exist.

**Exit gate:** tests prove the three router outcomes, unsupported curricula cannot fall through to generic work, and the full body gate passes.

### 2. Return-credit curriculum — executor and bounded tests exist; live episode pending

- Run only if the learner independently selects the return-credit curriculum.
- Exercise the prefrozen contract against labeled didactic observations; retain the candidate representation, inputs, outcomes, and ablations as raw evidence.
- Keep the claim narrow: bounded induced policy/candidate behavior under the supplied exercise. The current host interpreter/evaluator is not evidence of open-ended semantic understanding.
- Require B1 and B2 evidence under the frozen contract, including counterfactual/ablation evidence specified there.
- Carry failures and residuals into the next learner-facing advisory cycle. Do not infer permission to select the next target.

**Exit gate:** learner-selected live cycle is traceable to the prefreeze, B1 and B2 meet the frozen contract, counterfactuals are retained, and independent review records any remaining gaps. B3 remains false.

### 3. Dependency-planning curriculum — immediate implementation blocker

Implement an executor for `kernel/development/DEPENDENCY_PLANNING_CURRICULUM_PREFREEZE.json` only after translating its existing contract into explicit observable cases and gates. Preserve the contract; do not weaken it to make the executor pass.

The exercise should use opaque task labels and require the candidate to infer a dependency structure from returned prerequisite facts. Cover at least:

- arbitrary task ordering, including a valid order that differs from the presentation order;
- fork/join structure and detection of prerequisites that cannot be skipped;
- durations that make the critical path change across cases;
- noncritical-task duration perturbations that should not change makespan;
- a valid schedule that respects all dependencies and a checkable makespan;
- rejection of tempting but invalid shortcuts;
- cycles, missing facts, underspecified facts, and unsupported constraints returning a bounded failure/WITHHOLD instead of invented certainty.

The runtime must execute a candidate representation owned by the learner’s state through a generic interpreter. Keep expected results in the frozen contract/test harness, not embedded as target-specific scheduler answers in the runtime. Retain raw prompts/facts, candidate program, traces, ablations, and result. A valid schedule produced by a host-authored scheduler does not satisfy the candidate-execution gate.

**Exit gate:** focused tests demonstrate that the selected candidate—not a hidden answer helper—solves the frozen cases; structural and counterfactual tests pass; unsupported cases fail closed; the full body gate passes. Until then, #236 remains WITHHOLD and no generic WWW substitution is allowed.

### 4. Joint RSI scheduling and recurrence

After both bounded strands have independently passed their B1/B2 gates, construct a learner-selected joint exercise that tests whether Minerva can reason over a development DAG and choose lawful next work. Test distinctions that can be confused:

- task dependency versus adjacency or presentation order;
- critical path versus importance or urgency;
- a returned prerequisite fact versus an assumed domain fact;
- schedule optimization versus target authorization;
- work, span, slack, and makespan as distinct quantities;
- shortest lawful path versus shortcutting a required gate.

Freeze the joint contract and counterfactuals before execution. The learner chooses whether this is the next target. Do not combine evidence from separate exercises as if it were one successful joint episode.

**Exit gate:** the candidate’s own state performs the contracted reasoning on fresh, perturbed cases; causal ablations identify which evidence matters; unsupported cases withhold; B1/B2 pass with reviewable raw traces.

### 5. B3 internalization and source removal — only after bounded contract passage

For each selected curriculum, freeze the B3 design before running it. Remove or hide instructional labels and answer helpers; restart from a clean process; include delayed reuse and fresh transfer cases; use an evaluator that does not expose the expected answer during candidate execution. Retain permissions, rollback, and external admission boundaries.

**Exit gate:** source-removal/restart, fresh transfer, and independent evaluation all pass the applicable frozen contract. Otherwise report WITHHOLD or the precise failed gate. B3 passage still does not confer truth authority or external admission.

### 6. Interaction and data surface

The WorldMirror console, raw-interaction capture, and process bridge already exist. Preserve those boundaries and use their raw records as evidence. Change the interface only when a concrete interaction failure or data-quality gap shows that an adjustment is needed. Do not treat additional UI surface as capability evidence.

### 7. Wider inquiry and claims ladder

Permit learner-initiated network inquiry only when it is part of the selected contract and the relevant gates allow it. Preserve query, source, retrieved bytes, context, transformations, and candidate outputs as distinct records. Progress from WWW to Lain/Root/other broader environments only as separate, explicitly selected and evaluated steps.

Use the claims ladder narrowly:

1. Bounded contract behavior, with exact task and conditions.
2. Causal contribution of returned evidence, if ablations support it.
3. Internalization, only after B3 source removal/restart/fresh transfer/independent evaluation.
4. Broader capability, only after external evaluation over broad heterogeneous evidence with preregistered scope and controls.
5. AGI, only if an external broad evaluation supports that claim.

No current artifact, test, handoff, or issue establishes consciousness, general intelligence, or AGI.

## Immediate next actions

1. Keep issue #238 open as the cycle’s external-review carrier; do not rerun the worker while it is the open barrier.
2. Review the frozen envelope, cycle receipt, and mentor-context receipt for consistency; ask external review to address process correctness and the WITHHOLD outcome without granting capability or promotion authority.
3. Implement the dependency-planning curriculum executor and focused tests against the existing prefreeze, preserving fail-closed behavior.
4. Run the full body gate. Only after it passes, a future learner-selected cycle may execute the curriculum; a test pass alone does not select #236 or constitute the exercise.
5. After the review carrier is resolved through its normal workflow, continue from the learner’s current selection. Keep return-credit and dependency-planning evidence separate until a learner-selected joint contract is executed.

## Evidence and interpretation ledger

| Item | Directly observed | What it supports | What it does not establish |
|---|---|---|---|
| Run 36250473987 | Worker completed; selected #236 / `DEPENDENCY_TRACE`; returned typed WITHHOLD; network stages skipped; handoff created | Fail-closed process path for this unsupported selected prefreeze | Dependency-planning capability |
| Handoff branch `handoff/minerva-to-venus/36250473987-1` | Cycle, mentor receipt, problem, and didactic envelope retained | Provenance and authority fields for this cycle | Correctness of a dependency solution |
| Issue #238 | Open; 0 comments at plan time; identifies frozen handoff and blocks reroll | A review carrier exists | Review approval, promotion, Venus admission, truth, or merge authority |
| Body gate 36250473978 | Full Minerva audit and local surface checks passed | Repository invariants passed for the tested commit | Curriculum B1/B2/B3 performance |
| Return-credit curriculum tests | Bounded candidate/evaluator tests pass and forbidden B3/promotion/truth flags stay false | Implementation guardrails for that local harness | Live learner-selected cycle, independent evaluation, internalization |

## Change control

When new results arrive, update this plan with the run/commit/handoff identifiers and classify each result as observation, inference, or hypothesis. Preserve failed results and raw evidence. Revise a frozen contract only through an explicit, versioned learner/mentor process before a new run; never retrofit the expected outcome after seeing candidate behavior.
