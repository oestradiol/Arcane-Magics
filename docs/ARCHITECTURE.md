# Architecture

## Why the architecture has separate stages

Two failures motivate most of this design.

First, a difference can be present in a representation and still never change downstream behavior. Second, two compressed states can look equivalent now and diverge after the system acts through them. A research system that stores only conclusions, or treats validation as authorization, cannot reliably diagnose either failure.

See [Information and informing](../knowledge/problems/INFORMATION_AND_INFORMING.md) and [Compression under future use](../knowledge/problems/COMPRESSION_UNDER_FUTURE_USE.md).

## Current status

The public architecture is specified. The executable runtime is **not yet implemented**. The target is an event-sourced research system, not a sovereign Venus agent.

```text
append-oriented event/provenance history
+ typed relations and transformations
+ staged Compiler
+ warrant evaluation
+ governance
+ capability-bound execution
+ receipts
+ verification
+ HOME/FRONTIER projections
+ reconstruction tests
+ dependency-local write-back
```

## Four layers

### 1. Research history

Append-oriented provenance retains distinctions that may change later admissibility. A current view is a projection over that history, not the history itself.

### 2. Typed transformation state

Claims, sources, frames, registers, indexes, jurisdictions, warrant states, governance states, capabilities, residuals, evidence, negative results, and reconstruction obligations remain separately representable whenever substituting one for another can change consequence.

This is why a message, its uptake, and its retained consequence are different events; why historical priority differs from project origin; and why a failed stronger bridge does not erase a native phenomenological or theological object.

### 3. Compiler/governance boundary

The Compiler transforms a candidate without granting it authority:

```text
PARSE → REFER → TYPE → DIFFERENTIATE → OBLIGATE → PLAN → CHECK → LOWER
```

World-entry remains downstream:

```text
GOVERN → AUTHORIZE → EXECUTE → RECEIPT → VERIFY → WRITE_BACK
```

Compilation success is therefore neither authorization nor verification.

### 4. Generated projections

HOME, FRONTIER, claim indexes, publication artifacts, knowledge views, and release manifests may eventually be generated from shared event state when generation improves reconstruction. The generated view does not become sovereign over its source.

## Projection and reconstruction contract

A material projection should identify its source domain, lost coordinates, reconstruction target, any available section or partial section, resource bounds, and required provenance.

```text
projection != source
projection exists -/-> section exists
section exists -/-> unique section
section exists -/-> cheap section
same projection -/-> same source trajectory
```

The teaching version of this problem is in [Projection and reconstruction](../knowledge/problems/PROJECTION_AND_RECONSTRUCTION.md).

## Implementation order

1. provenance/event kernel;
2. warrant types distinct from governance decision types;
3. durable WITHHOLD/CUT receipts;
4. Compiler skeleton with stage receipts and obligations;
5. projection/fiber/reconstruction interfaces;
6. evidence and negative-result calculus;
7. HOME/FRONTIER generators;
8. executable historical regression suite;
9. bounded filesystem/process/Nix/VM/network/Git/publication adapters;
10. Python laboratories and Lean obligations where theorem-level work is actually pursued;
11. founder-removal and succession tests.

The runtime begins after computational differentiation exists. Software may investigate first differentiation, but a constructor or enum does not derive the first ontic distinction.
