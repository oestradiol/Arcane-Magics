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

## Paired analysis implementation

The first evidence-governance prefreeze now has an executable paired-analysis layer:

```bash
python evaluation/analyze_evidence_governance.py \
  --A /returned/A.scored.jsonl \
  --B /returned/B.scored.jsonl \
  --C /returned/C.scored.jsonl \
  --D /returned/D.scored.jsonl \
  --E /returned/E.scored.jsonl \
  --output /private/evidence-governance-analysis.json
```

The mechanism-local primary tests are B vs C on invalid promotion for claim-local provenance, and B vs D on negative-result reuse for retained-negative state. Both use exact paired discordant-case testing with Holm familywise correction across the two mechanism claims.

Prospective power planning is available through `evaluation/plan_paired_power.py`. It requires the evaluator/researcher to declare a minimum conditional win probability and expected discordance rate before exposure; the repository does not invent those assumptions from hidden results.

Neither implementation makes the experiment RUN_READY. Model snapshot, hidden split, contamination disposition, matched budgets/tools/information, evaluator identity, mature substitute, and prospectively justified power assumptions must still be frozen.
