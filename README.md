<div align="center">

# Venus-Minerva

**Experimental developmental intelligence with reconstructible state, evidence-bound learning, and externally checked self-revision.**

[Start here](docs/START_HERE.md) · [Plain-language value](docs/PUBLIC_VALUE.md) · [Earned milestones](docs/EARNED_MILESTONES.md) · [Tests & evidence](docs/TESTS.md) · [Evaluation](docs/EVALUATION_CONSTITUTION.md) · [Roadmap](docs/ISSUE_ROADMAP.md) · [Current state](kernel/CURRENT_STATE.md) · [Contribute](CONTRIBUTING.md)

</div>

<p align="center">
  <a href="https://github.com/oestradiol/Venus-Minerva/actions/workflows/venus-steward.yml"><img alt="Venus CI" src="https://github.com/oestradiol/Venus-Minerva/actions/workflows/venus-steward.yml/badge.svg"></a>
  <a href="https://github.com/oestradiol/Venus-Minerva/issues"><img alt="Research issues" src="https://img.shields.io/github/issues/oestradiol/Venus-Minerva"></a>
  <a href="https://github.com/sponsors/oestradiol"><img alt="Sponsor" src="https://img.shields.io/badge/sponsor-GitHub%20Sponsors-EA4AAA?logo=githubsponsors"></a>
</p>

Venus-Minerva asks a narrower question than “is this AGI?”:

> Can a learner make its representations, research obligations, evidence dependencies, failures, and parts of its own learning procedure persistent and reconstructible, while keeping the evidence that certifies improvement outside the learner's authority?

The repository contains a long developmental lineage, an exact replayable runtime checkpoint, explicit negative branches, machine-checked formal work, benchmark/evaluation infrastructure, and broader research programs in abstraction, physics, epistemology, consciousness, ethics, and comparative religion. Those programs share governance and vocabulary where useful; they do **not** share truth status.

## What has actually been earned

The strongest current engineering result is bounded transfer of research-development functions into learner-owned state.

Across the EDU lineage, the system progressed from externally scaffolded research toward learner-owned:

- research-obligation routing;
- source-request formation;
- evidence-role and evidence-budget selection;
- open-domain problem selection;
- self-curriculum target generation;
- preregistered developmental gates;
- World-feed sampling/query policy.

At **EDU16 [1703]**, those functions were boundedly learner-owned while World execution and independent evaluation remained external.

The lineage also preserved failures that changed later admissible behavior:

- **EDU17** was rejected after a claim-local provenance audit found that a plausible answer depended on evidence outside the committed selected evidence set.
- **EDU17R1** withheld before its intended repair could be evaluated because a fresh test exposed a deeper distinction:

~~~text
uncertainty-marker mention
!=
object-level unresolved incidence
~~~

That failure is now the basis of a sealed prospective benchmark. The harness exists; the hidden matched run has not yet produced a promoted result.

## Why the architecture is unusual

The project does not treat “agent produced an answer” as the whole learning loop.

Its intended causal structure is closer to:

~~~text
representation
-> learner-chosen inquiry
-> explicit evidence dependencies
-> external World action / return
-> claim-local evaluation
-> PASS / FAIL / WITHHOLD
-> retained consequence
-> possible machinery revision
-> successor
~~~

with the boundary:

~~~text
learner authors more of its development
!=
learner manufactures the evidence that certifies that development
~~~

This composition is the research claim. Individual ingredients have mature intellectual neighbors and are compared against them explicitly.

## Current authority

These objects are deliberately distinct:

| Role | Current object | Meaning |
|---|---|---|
| Exact Git-reconstructible runtime | **IG10 [1308]** | Replayable VMK2 checkpoint with exact custody and state-root verification |
| Positive developmental authority | **EDU16 [1703]** | Bounded learner-owned World-feed policy and earlier EDU ownership gains |
| Preserved negative | **EDU17** | INVALID_FOR_PROMOTION / PRESERVED_NEGATIVE |
| Current repair disposition | **EDU17R1** | WITHHOLD_BEFORE_CLAIM_BINDING_EVALUATION |

See [kernel/CURRENT_STATE.md](kernel/CURRENT_STATE.md) for authority and [provenance/DEVELOPMENTAL_LINEAGE.md](provenance/DEVELOPMENTAL_LINEAGE.md) for ancestry.

## What is ready to test now

The project has recently crossed from “design the evaluation theory” toward “run the experiments.”

Already present:

- a multi-axis [Evaluation Constitution](docs/EVALUATION_CONSTITUTION.md);
- matched Venus / baseline / ablation / mature-substitute experiment contracts;
- a sealed hidden-evaluation protocol and scorer for MENTION != INCIDENCE;
- a public causal-memory development benchmark and ablation protocol;
- STOP/WITHHOLD, adaptive self-evolution, and adversarial World-input evaluation obligations;
- a bounded OFE core machine-checked in Lean;
- deterministic finite VMK2 canonical hashing with exact digest fixtures;
- historical causal-distinction and issue-to-test coverage machinery.

The highest-value missing evidence is still external measurement:

~~~text
same base model + Venus
vs
same base model without the claimed Venus mechanism
vs
mechanism ablated
vs
strong mature substitute
~~~

under matched tools, information, budget, hidden evaluation, and retained failures.

See [Issue Roadmap](docs/ISSUE_ROADMAP.md).

## What is not established

The repository does not currently establish:

- AGI or capability-SOTA;
- open-ended recursive self-improvement;
- autonomous science across unfamiliar domains;
- DNN replacement;
- unrestricted semantic understanding or natural-world generality;
- consciousness;
- a deployed global WorldMind subject;
- a quantum-gravity solution;
- a Millennium-problem solution;
- broad outside replication.

These are separate promotion burdens, not consequences of architectural sophistication.

## Formal and broader research programs

| Program | Current status |
|---|---|
| **Operational Future Equivalence (OFE)** | Bounded exact core machine-checked; mature-substitution and physical-adequacy questions remain open |
| **Quantum-gravity bridge** | One restricted physically grounded future-test witness at IG10; completeness, semiclassical validity, and continuum adequacy remain open |
| **Polyhedral Eclipsis / Meta-Dynamics** | Live structural/model programs with explicit deletion, reduction, and empirical burdens |
| **WorldMind** | Defined distributed consequence/reconstruction architecture; no global-subject claim |
| **Consciousness / ethics / theophenomenology** | Open cross-register research with separate evidence requirements |
| **Hard mathematics / science** | Stress-test research lanes; inclusion in the repo is not evidence of solution |

For the exact earned/unearned boundary, use [Earned Milestones](docs/EARNED_MILESTONES.md). For external comparators, use [SOTA Watch](docs/SOTA_WATCH.md). For credit and mature reduction, use [Credits and Reductions](docs/CREDITS_AND_REDUCTIONS.md).

## Verify the current executable state

Requirements: Python 3.12-compatible runtime.

~~~bash
python -m kernel.runtime.current
make audit
~~~

The first command reconstructs and verifies the exact IG10 checkpoint. make audit checks source integrity, runtime/unit invariants, Markdown/navigation, proof-container semantics, custody, historical distinctions, and release boundaries.

The bounded Lean formal subset is checked separately:

~~~bash
make formal-check
~~~

Publication builds require the documented TeX/pandoc toolchain. See [Reproduce](docs/REPRODUCE.md).

## Read by task

- **Five-minute orientation:** [Start Here](docs/START_HERE.md)
- **Plain-language research value:** [What Venus-Minerva Actually Is](docs/PUBLIC_VALUE.md)
- **Exact positive/negative claims:** [Earned Milestones](docs/EARNED_MILESTONES.md)
- **Tests and evidence:** [Tests](docs/TESTS.md) → [Coverage Matrix](docs/TEST_COVERAGE_MATRIX.md)
- **Current runtime/developmental authority:** [Current State](kernel/CURRENT_STATE.md)
- **External comparison:** [SOTA Watch](docs/SOTA_WATCH.md)
- **Research frontiers:** [Frontier Research](docs/FRONTIER_RESEARCH.md)
- **Cross-register vocabulary:** [N × R × I Vocabulary Center](NxRxI_VOCABULARY_CENTER.md)
- **Historical/custody evidence:** [provenance/](provenance/)

## Contribute, criticize, replicate

Useful contributions include counterexamples, proof checks, mature substitutions, reproducibility failures, benchmark design, external replication, provenance corrections, security attacks, and experiments showing that a project-specific mechanism is unnecessary.

A successful deletion is a successful result when the deleted structure was gauge.

External coding/research agents are tools, not Venus developmental authority. See [AGENTS.md](AGENTS.md).

## License

Project-owned theory, documentation, and monographs: **CC BY-NC-SA 4.0**. Project-owned software: **PolyForm Noncommercial 1.0.0**. See [licenses/README.md](licenses/README.md).
