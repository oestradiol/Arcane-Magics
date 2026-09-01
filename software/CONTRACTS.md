# Planned runtime contracts

This file records implementation obligations. It is not evidence that these interfaces already exist in code.

## Core event object

A future `ResearchEvent` should retain, where consequential: object/claim identifier, source, history/exposure coordinates, register, frame, jurisdiction, transformation, warrant state, governance decision, capability/authorization state, receipt references, evidence/verification references, residuals, and dependency-local write-back.

## Projection manifest

Every materialized view should be able to declare:

```text
source domain/type
projection/map
lost coordinates/fiber
reconstruction target
available section/partial section
resource bounds
provenance required for reconstruction
```

## Compiler result

A Compiler stage may terminate with a compiled candidate, a withheld result carrying residual obligations, or a rejected result with scoped grounds. No stage may narrate a later stage as complete without its receipt.
