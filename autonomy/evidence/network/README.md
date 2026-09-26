# Network / WWW Mind evidence

This directory contains bounded learner-initiated network inquiry episodes.

A typical lineage is:

```text
query.json
→ execution-context.json
→ encounter.json
→ result.json
→ followup-query.json
→ followup-encounter.json
→ lineage-result.json
```

The important causal discriminator is not “a page was fetched.” It is:

```text
retained provenance-bearing encounter
→ changes later reconstruction/query
```

Network encounter remains `ENCOUNTER_RETURN`, not evaluator truth.

Current gate definitions/results live in:

- [`../../../kernel/development/WWW_MIND_GATE.json`](../../../kernel/development/WWW_MIND_GATE.json)
- [`../../../kernel/development/WWW_MIND_GATE_RESULT.json`](../../../kernel/development/WWW_MIND_GATE_RESULT.json)
- [`../../../kernel/development/LAIN_GATE.json`](../../../kernel/development/LAIN_GATE.json)
- [`../../../kernel/development/LAIN_GATE_RESULT.json`](../../../kernel/development/LAIN_GATE_RESULT.json)
