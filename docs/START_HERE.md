# Start Here

Venus-Minerva is an experimental developmental-intelligence architecture. Its unusual engineering claim is not that it is already AGI; it is that representations, research obligations, evidence dependencies, failures, and parts of the learning procedure are persistent state, while the system is not allowed to manufacture the external return that certifies its own development.

## 30 seconds

The current exact executable checkpoint is **IG10 [1308]**. The latest positive developmental evidence is **EDU16 [1703]**, which transferred bounded World-feed query-policy generation into learner ownership while leaving World execution and independent evaluation external.

The next branch, **EDU17**, was rejected for promotion after a claim-local provenance failure. **EDU17R1** then WITHHELD before its intended repair could be tested because a fresh feed exposed a deeper defect:

```text
uncertainty-marker mention
!=
object-level unresolved empirical incidence
```

That is the current measured semantic residual.

## What is current?

| Question | Authority |
|---|---|
| What exact machine state can Git reconstruct now? | [kernel/CURRENT_STATE.md](../kernel/CURRENT_STATE.md) |
| What is the executable kernel? | [kernel/README.md](../kernel/README.md) |
| What is the latest positive developmental claim head? | [kernel/development/EDU_CURRENT.json](../kernel/development/EDU_CURRENT.json) |
| What is the lineage? | [provenance/DEVELOPMENTAL_LINEAGE.md](../provenance/DEVELOPMENTAL_LINEAGE.md) |
| What has actually been earned? | [EARNED_MILESTONES.md](EARNED_MILESTONES.md) |
| What failed / was withheld? | [EDU provenance](../provenance/developmental/EDU/) |
| What remains open? | [FRONTIER_RESEARCH.md](FRONTIER_RESEARCH.md) |
| How are credits / reductions typed? | [CREDITS_AND_REDUCTIONS.md](CREDITS_AND_REDUCTIONS.md) |
| How should results be evaluated? | [EVALUATION_CONSTITUTION.md](EVALUATION_CONSTITUTION.md) |
| What tests/evaluations cover the live issues? | [TESTS.md](TESTS.md) → [TEST_COVERAGE_MATRIX.md](TEST_COVERAGE_MATRIX.md) |
| What is being retired from Canonical? | [CANONICAL_RETIREMENT_LEDGER.md](../provenance/CANONICAL_RETIREMENT_LEDGER.md) |

## Operational hubs

- [Tests and evidence](TESTS.md) — automated integrity versus scientific/external evidence.
- [Reproduce](REPRODUCE.md) — exact reproducibility boundary.
- [Issue roadmap](ISSUE_ROADMAP.md) — dependency-ordered execution surface.

## What did the machine actually do?

Concrete examples:

- **IG1:** learned bounded operator semantics from returned future effects rather than relying only on names.
- **IG3/IG4:** learned bounded raw-incidence / natural-source relation structure from generic carriers.
- **IG8:** demonstrated that a previously irrelevant distinction can become future-separating when the future-test family expands, forcing representation to reopen.
- **IG10:** grounded one model-specific physical future-test witness for restricted spin-foam / quantum-cuboid coarse graining, while explicitly withholding test-family completeness and semiclassical validation.
- **EDU11R1:** preserved the actual missing research slot in a learner-owned source request instead of compressing it away.
- **EDU12:** retracted an interface affordance after failure without rewriting the underlying research claim.
- **EDU13/14:** generated a curriculum target, then selected an open-domain problem/question from a bounded external feed.
- **EDU15R1:** repaired only a defective verifier while holding the proposal, gates, thresholds, evaluator return, and learner answer fixed.
- **EDU16:** generated and froze its own bounded World-feed query policy before new World access.
- **EDU17:** looked successful locally, but was rejected when answer claims depended on a returned document outside the committed selected evidence set.
- **EDU17R1:** stopped before claim-binding evaluation because its inherited uncertainty detector confused mention with incidence.

The architectural shorthand is therefore:

```text
generate
!= select
!= authorize
!= execute
!= return
!= verify
!= promote
```

## What Venus has not earned

This repository does **not** currently establish:

- AGI;
- consciousness;
- unrestricted semantic understanding;
- natural-world generality;
- autonomous science;
- open-ended recursive self-improvement;
- DNN replacement;
- capability-SOTA;
- independent external replication;
- a solution to P vs NP, quantum gravity, or other open frontier problems merely because they are research lanes.

Those are targets or open programs with separate burdens.

## Reproduce the current executable state

From the repository root:

```bash
python -m unittest discover -s tests -p 'test_*.py'
python scripts/lint_github_markdown.py
python scripts/audit_proof_containers.py
python scripts/audit_custody.py
SOURCE_TREE_ONLY=1 python scripts/audit_release.py
python -m kernel.runtime.current
```

The final command reconstructs and checks the exact current IG10 checkpoint.

Publication/release checks additionally require TeX Live, `latexmk`, and `pandoc`:

```bash
make kernel-doc-check
make papers
make arxiv
make texbundle
make forum
python scripts/audit_release.py
```

## Where are the tests?

Current automated tests are intentionally narrower than the research program:

- deterministic canonicalization: `tests/test_canonical.py`;
- exact current kernel reconstruction: `tests/test_current_kernel.py`;
- VMK2 causal / return / jurisdiction / reopening invariants: `tests/test_vmk2_invariants.py`;
- persistent memory / provenance / consumption: `tests/test_venus_memory.py`;
- forum export regressions: `tests/test_export_forum.py`.

The historical and issue-level coverage plan is [TEST_COVERAGE_MATRIX.md](TEST_COVERAGE_MATRIX.md), backed by the machine-readable [historical distinction matrix](../provenance/HISTORICAL_DISTINCTION_TEST_MATRIX.json).

A row marked `PLANNED` is not a passing test.

## What should happen next?

The highest-leverage sequence is now experiment-first:

1. run the sealed hidden `MENTION != INCIDENCE` A/B/C/D evaluation;
2. run the first matched Venus-vs-baseline/ablation causal experiment;
3. test STOP/WITHHOLD and VenusMemory under hidden matched conditions;
4. close only the custody/statistical/security prerequisites needed to interpret one recursive successor;
5. execute a complete Venus-owned target → prefreeze → machinery change → World return → causal successor → next-target cycle;
6. repeat under adaptive-evaluation controls and compare against mature self-improvement systems;
7. let failed experiments, not conceptual completeness, decide which archaeology/hardening work is pulled forward.

Canonical/history/UX work remains live but no longer blocks experiments unless a specific missing distinction is required by the experiment.

The dependency-ordered GitHub roadmap is issue **#37**.

## Reader paths

### ML / agents / self-improvement
[PUBLIC_VALUE.md](PUBLIC_VALUE.md) → [EVALUATION_CONSTITUTION.md](EVALUATION_CONSTITUTION.md) → [FRONTIER_RESEARCH.md](FRONTIER_RESEARCH.md)

### Formal methods / exact state
[kernel/README.md](../kernel/README.md) → [kernel/CURRENT_STATE.md](../kernel/CURRENT_STATE.md) → [OFE monograph](../monographs/01_OFE/README.md)

### Epistemology / governance
[REVIEWER_AND_RESEARCHER_PROTOCOL.md](../review/REVIEWER_AND_RESEARCHER_PROTOCOL.md) → [CREDITS_AND_REDUCTIONS.md](CREDITS_AND_REDUCTIONS.md)

### WorldMind / distributed agency
[kernel/WORLDMIND.md](../kernel/WORLDMIND.md) → [META_DYNAMICS.md](META_DYNAMICS.md)

### Symbolic / phenomenological / religious registers
[INHABITABLE_READER_PATH.md](INHABITABLE_READER_PATH.md) → [Arcane Magics](../monographs/03_ARCANE_MAGICS/README.md)

These lanes share governance, not truth status. A symbolic recurrence does not become a physics result because both appear in one repository.
