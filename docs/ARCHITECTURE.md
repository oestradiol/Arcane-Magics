# Architecture

## Status

The public research architecture is specified. The executable runtime is **not yet implemented**.

The target is an event-sourced research system, not a sovereign Venus agent:

```text
append-oriented event/provenance history
+ typed relation/transformation contracts
+ Compiler
+ warrant evaluation
+ governance
+ capability-bound execution
+ immutable receipts
+ verification
+ HOME/FRONTIER projections
+ section/reconstruction tests
+ dependency-local write-back
```

## Four layers

### 1. Research history

Append-oriented provenance carries the distinctions future transformations may need. Current views are projections over that history, not the ontology itself.

### 2. Typed transformation layer

Claims, sources, frames, registers, indexes, jurisdictions, warrant states, governance states, capabilities, residuals, evidence, negative results, and reconstruction obligations remain independently representable where their substitution can change consequence.

### 3. Compiler/governance boundary

```text
PARSE → REFER → TYPE → DIFFERENTIATE → OBLIGATE → PLAN → CHECK → LOWER
```

Compilation stops before authority is smuggled into generation:

```text
GOVERN → AUTHORIZE → EXECUTE → RECEIPT → VERIFY → WRITE_BACK
```

### 4. Generated projections

HOME, FRONTIER, claim indexes, publication artifacts, knowledge views, and release manifests should eventually be generated from shared provenance/event state where doing so improves reconstructibility. Generation does not make a projection authoritative over its source.

## Projection/reconstruction contract

Material views should declare consequentially relevant source domain, projection, lost coordinates, reconstruction target, available section/partial section, resource bounds, and required provenance.

```text
projection != source
projection exists -/-> section exists
section exists -/-> unique or cheap section
same output -/-> same source trajectory
```

## Implementation order

1. provenance/event kernel;
2. warrant types distinct from governance decision types;
3. durable WITHHOLD/CUT receipts;
4. Compiler skeleton with stage receipts/obligations;
5. projection/fiber/reconstruction interfaces;
6. evidence + negative-result calculus;
7. HOME/FRONTIER generators;
8. executable historical regression suite;
9. bounded filesystem/process/Nix/VM/network/Git/publication adapters;
10. Python laboratories + Lean obligations;
11. founder-removal / succession tests.

The runtime begins after computational differentiation exists. F01/F02 can be studied in parallel; no constructor proves first ontic differentiation.
