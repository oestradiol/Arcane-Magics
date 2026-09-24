# Evaluation manifests

`MATCHED_EXPERIMENT_TEMPLATE.json` defines the common A/B/C/D/E contract. A valid schema is not automatically a run-ready experiment.

`EVIDENCE_GOVERNANCE_PREFREEZE.json` is the first concrete #10 causal experiment contract. It targets claim-local provenance and retained negative state under matched conditions.

## Readiness states

```text
TEMPLATE / PREFREEZE
-> schema is inspectable
-> missing dependencies are explicit
-> execution is forbidden

RUN_READY
-> model snapshot frozen
-> hidden split hash frozen
-> contamination disposition frozen
-> tools/information/budgets frozen
-> independent evaluator frozen
-> analysis plan frozen
-> execution may begin
```

CI runs both the structural manifest validator and the readiness audit. Neither grants promotion authority.

## First evidence-governance experiment

The planned conditions are:

```text
A ordinary strong scaffold
B full Venus
C Venus minus claim-local provenance
D Venus minus retained negative state
E strongest mature substitute
```

The public benchmark surfaces are development aids only. The claim-bearing task surface must be held out from the evaluated harness before execution.
