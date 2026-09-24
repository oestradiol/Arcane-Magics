# Tests and evidence

This is the shortest map from a Venus-Minerva claim to the kind of test that can support it.

## Run the current automated suite

```bash
make audit
```

That currently covers:
- live Python/unit invariants;
- reader-surface Markdown/link integrity;
- theorem/proof-container structure lint;
- custody/current-state checks;
- generic-search scaffold-removal/equivalence audit;
- Internalizer O*/Anti-Minerva correction-boundary regressions;
- historical causal-distinction registry integrity;
- source-tree release boundaries.

CI additionally checks the live GitHub issue set and fails when an open issue has no row in the test-coverage matrix.

## Test layers

| Layer | Question |
|---|---|
| T0 | Is repository/current authority internally consistent? |
| T1 | Do deterministic kernel invariants hold? |
| T2 | Have historically learned causal distinctions regressed? |
| T3 | Does the trust/custody boundary survive hostile inputs? |
| T4 | Do semantic discriminators distinguish the right referents? |
| T5 | Does a Venus mechanism causally matter under matched ablation? |
| T6 | Does Venus produce externally scored capability/science consequences? |
| T7 | Are formal claims verified/reduced against mature alternatives? |
| T8 | Does live external state reopen stale repository state? |
| T9 | Can an unfamiliar reader reconstruct and navigate the system? |

Passing one layer never promotes a claim into another.

## Control surfaces

- [Historical distinction registry](../provenance/HISTORICAL_DISTINCTION_TEST_MATRIX.json)
- [Open-issue test coverage](TEST_COVERAGE_MATRIX.md)
- [Current authority](../kernel/CURRENT_STATE.md)
- [Developmental lineage](../provenance/DEVELOPMENTAL_LINEAGE.md)
- [Evaluation constitution](EVALUATION_CONSTITUTION.md)
- [Earned milestones](EARNED_MILESTONES.md)
- [Reviewer methodology](../review/REVIEWER_AND_RESEARCHER_PROTOCOL.md)

## Historical regression law

A historical distinction becomes a regression obligation when an experiment, failure, repair, boundary, or mature reduction changed what later states were allowed to do, infer, promote, or preserve.

The intended compression is:

```text
large developmental history
-> extracted causal distinctions
-> compact falsifier/regression suite
-> simpler live implementation
-> provenance and reopening routes preserved
```

Historical artifacts do not become current authority merely because they are tested.

## External evidence

CI can enforce:
- preregistration shape;
- budget/harness metadata;
- test-set custody;
- no-reroll rules;
- ablation configuration;
- result retention;
- promotion gates.

CI cannot honestly manufacture:
- independent replication;
- expert judgment;
- new physical evidence;
- mathematical novelty;
- benchmark superiority;
- institutional/prize credit.

Those require World-side return and remain separate from automated integrity.

## Memory causal learning benchmark

`benchmarks/memory_causal/` is a public development benchmark for issue #15. It tests whether retained dispositions, provenance, negative branches, and replacement relations change later admissible action. Public dev accuracy is not promotion evidence; the protocol requires hidden matched ablations.

## Machine-checked formal subset

`formal/lean/` machine-checks a bounded OFE core: future-equivalence as a setoid, test-family monotonicity, sufficient-representation refinement, quotient transport under equivalence preservation, pullback closure as a sufficient condition, common-refinement factorization implying future-equivalence, separating-family equality, and reopening by adjoining an explicit pulled-back separator. `tests/test_proof_container_semantics.py` separately locks the fact that theorem-container lint is only structural. These checks do not establish OFE novelty, physical correctness, or mature-substitution residual.

## Reliability public development surfaces

The repository now contains three non-promotional public reliability surfaces:

- `benchmarks/adaptive_promotion/` — synthetic repeated-null-proposal pressure for false successor commits (#41);
- `benchmarks/abstention/` — paired ACT / GATHER / WITHHOLD / STOP decision cases (#42);
- `benchmarks/world_input_security/` — returned-content / instruction / authority / memory disposition cases (#43).

They define executable failure surfaces and baseline floors. Claim-bearing results still require hidden/matched or dynamic external evaluation against mature substitutes.

## Developmental infrastructure checks

Two current T3/T5-adjacent checks are easy to misread as developmental promotion:

- `scripts/audit_generic_search_internalization.py` checks that the inherited generic residual-search function survives scaffold removal as state-owned capability while keeping World/evaluator/authority roles external.
- `tests/test_internalizer.py` checks O* noncollapse and Anti-Minerva carrier permeability.
- `tests/test_edu17r1_semantic_ingress.py` plus `scripts/audit_edu17r1_semantic_ingress.py` bind the public-development method selection, frozen candidate, ownership receipt, hidden-unexposed state, and condition-B executor.
- `benchmarks/edu17r1_mention_incidence/CONDITION_IMPLEMENTATIONS.json`, `scripts/audit_edu17r1_condition_freeze.py`, and `scripts/audit_hidden_run_readiness.py` bind the complete prefrozen A/B/C/D executor set while requiring the actual hidden split/return to remain external.

Passing the first two establishes infrastructure/governance consequences at their tested scope. The semantic-ingress freeze audit additionally establishes bounded learner-side repair authorship before hidden exposure. The harness may therefore be **ready** while efficacy remains entirely unknown. None of these establishes hidden #31 efficacy, developmental promotion, or Safe Strong RSI.
