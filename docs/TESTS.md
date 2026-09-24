# Tests and evidence

This page answers a simple question:

> For a given Venus-Minerva claim, what kind of evidence could actually support or refute it?

Repository tests, formal proofs, hidden benchmarks, external experiments, and independent replication are different evidence types. Passing one does not silently promote a claim into another.

## Run the automated integrity suite

~~~bash
make audit
~~~

This currently checks:

- live Python/runtime invariants;
- current authority and custody consistency;
- Markdown/navigation integrity;
- theorem/proof-container structure;
- historical causal-distinction registry integrity;
- open-issue → test/evaluation ownership;
- experiment-manifest constraints;
- source-tree release boundaries.

For the admitted Lean subset:

~~~bash
make formal-check
~~~

## Test layers

| Layer | Question |
|---|---|
| **T0** | Is repository/current authority internally consistent? |
| **T1** | Do deterministic kernel invariants hold? |
| **T2** | Have historically learned causal distinctions regressed? |
| **T3** | Does the trust/custody boundary survive hostile inputs? |
| **T4** | Do semantic discriminators bind the right referents? |
| **T5** | Does a Venus mechanism causally change behavior under matched ablation? |
| **T6** | Does Venus produce externally scored capability/science consequences? |
| **T7** | Are formal claims machine-checked and reduced against mature alternatives where relevant? |
| **T8** | Does changing external state reopen stale repository state? |
| **T9** | Can an unfamiliar reader reconstruct and navigate the system? |

The most important current gap is between T0–T4/T7 infrastructure and actual T5/T6 external results.

## Current high-value experimental surfaces

### EDU17R1 semantic discriminator

`benchmarks/edu17r1_mention_incidence/` contains:

- public development cases;
- the deliberately weak lexical mention baseline;
- A/B/C/D experiment conditions;
- a hidden-split sealing helper;
- deterministic scoring;
- regression tests for evaluator separation and hash binding.

The missing evidence is the sealed hidden matched run.

### Causal memory

`benchmarks/memory_causal/` tests whether retained dispositions, provenance, negative branches, and replacement relations change later admissible action.

The public split is development infrastructure. Promotion requires hidden matched ablations against raw history, equal-size context, summaries, retrieval/RAG, and no-memory controls.

### First matched Venus causal ablation

Issue #10 asks for:

~~~text
same model
same tools
same information
same budget

ordinary strong scaffold
vs
full Venus
vs
claimed mechanism ablated
vs
strong mature substitute
~~~

This is the central experiment for separating architectural consequence from additional scaffolding.

### STOP/WITHHOLD and adversarial World input

Issues #42 and #43 test two distinct boundaries:

~~~text
good abstention
!=
doing nothing

returned content
!=
instruction
!=
evidence
!=
authority
!=
persistent policy/memory
~~~

Both must be evaluated against mature substitutes and utility loss.

## Historical regression law

A historical distinction becomes a regression obligation when an experiment, failure, repair, boundary, or mature reduction changed what later states were allowed to do, infer, promote, or preserve.

The intended compression is:

~~~text
large developmental history
-> extracted causal distinctions
-> compact falsifier/regression suite
-> simpler live implementation
-> provenance and reopening routes preserved
~~~

Historical artifacts do not become current authority merely because they are tested.

## Machine-checked formal subset

`formal/lean/` machine-checks a bounded OFE core including:

- future-equivalence as a setoid;
- test-family monotonicity;
- sufficient-representation refinement;
- quotient transport;
- pullback closure as a sufficient preservation condition;
- common-refinement factorization implying future-equivalence;
- separating-family equality;
- reopening by adjoining an explicit pulled-back separator.

Theorem-container lint is separately tested as structural hygiene. Machine-checked correctness does not establish OFE novelty, physical correctness, or residual value after mature substitution.

## What CI can and cannot establish

CI can enforce:

- preregistration shape;
- custody/hash integrity;
- model/harness metadata requirements;
- no-reroll conditions;
- ablation configuration;
- negative-result retention;
- formal checker success;
- promotion-gate structure.

CI cannot honestly manufacture:

- independent replication;
- expert consensus;
- new physical evidence;
- mathematical novelty;
- capability superiority;
- a Venus-owned developmental episode.

Those require external return.

## Control surfaces

- [Current authority](../kernel/CURRENT_STATE.md)
- [Evaluation Constitution](EVALUATION_CONSTITUTION.md)
- [Test Coverage Matrix](TEST_COVERAGE_MATRIX.md)
- [Historical distinction registry](../provenance/HISTORICAL_DISTINCTION_TEST_MATRIX.json)
- [Issue Roadmap](ISSUE_ROADMAP.md)
- [Earned Milestones](EARNED_MILESTONES.md)
- [Reviewer methodology](../review/REVIEWER_AND_RESEARCHER_PROTOCOL.md)
