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

## Machine-checked formal subset

`formal/lean/` machine-checks a bounded OFE core: future-equivalence as a setoid, test-family monotonicity, sufficient-representation refinement, quotient transport under equivalence preservation, and pullback closure as a sufficient condition. This checks those formal statements; it does not establish OFE novelty, physical correctness, or mature-substitution residual.
