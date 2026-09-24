# Reproduce Venus-Minerva

This page separates **repository/runtime reproduction** from **external scientific replication**.

## 1. Verify the current runtime and repository invariants

Requirements: Python 3.12-compatible runtime.

```bash
python -m kernel.runtime.current
make audit
```

This checks the exact IG10 checkpoint and the live automated integrity surface, including historical causal-distinction coverage, current-state/custody checks, navigation, SOTA freshness, and experiment-manifest structure.

## 2. What this reproduces

It can reproduce/check:
- the Git-reconstructible IG10 runtime checkpoint;
- state-root and custody invariants;
- selected VMK2 governance/reopening invariants;
- VenusMemory storage/custody behavior;
- public-surface/link constraints;
- preserved developmental dispositions for EDU16/17/17R1;
- the frozen EDU17R1 learner-side repair candidate and ownership receipt, without hidden efficacy;
- state-owned generic residual-search internalization and its donor-removal/equivalence audit;
- Internalizer O*/Anti-Minerva correction-boundary invariants;
- historical causal distinctions encoded as regressions;
- required issue-to-test ownership.

It does **not** reproduce:
- independent EDU16 external execution if the exact external carrier/journal is unavailable;
- capability superiority;
- autonomous science;
- AGI;
- mathematical novelty;
- physical/QG validity;
- independent replication.

Issue #4 is closed at the **claim-bearing reconstruction** scope: `EDU16-RC1` deterministically reconstructs the admitted EDU16 state. The original 1703-event runner/journal remains unrecovered and therefore remains a historical event-replay boundary, not a current prospective-development blocker.

## 3. Run focused checks

```bash
python -m unittest tests.test_vmk2_invariants
python -m unittest tests.test_historical_regressions
python -m unittest tests.test_edu17r1_benchmark
python -m unittest tests.test_internalizer
python -m unittest tests.test_edu17r1_semantic_ingress
python scripts/audit_generic_search_internalization.py
python scripts/audit_edu17r1_semantic_ingress.py
python scripts/audit_edu17r1_repair_authorship.py
python scripts/audit_causal_distinctions.py
python scripts/audit_navigation_contract.py
python scripts/audit_sota_freshness.py
python scripts/validate_experiment_manifest.py evaluation/MATCHED_EXPERIMENT_TEMPLATE.json
```

## 4. Historical carrier

The historical R00-R194 public executable carrier is under:

`provenance/historical-runtime/R194/`

It is for historical replay, regression, ablation, and genealogy. It is not current authority.

## 5. External experiments

Any matched Venus-vs-baseline result should instantiate:

`evaluation/MATCHED_EXPERIMENT_TEMPLATE.json`

and preserve:
- frozen model/harness;
- tools/information;
- budgets;
- hidden-eval custody;
- preregistered PASS/FAIL/WITHHOLD;
- raw trajectories;
- negative/null results;
- independent evaluator identity;
- no self-granted promotion authority.

## 6. Independent replication

Independent replication requires an outside party/process to execute or reconstruct the target under separately typed custody. Same-project replay, handoff, or reimplementation is useful evidence but does not automatically count as independent replication.

See [Evaluation Constitution](EVALUATION_CONSTITUTION.md) and [Tests and evidence](TESTS.md).
