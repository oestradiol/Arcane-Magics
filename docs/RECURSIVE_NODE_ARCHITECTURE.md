# Recursive node architecture

**Register: CANDIDATE. Not admitted. Not yet applied to any branch but this one.**

A repository structure in which the repository instantiates its own theory:
every node is a local centre that expands as a root, the leaves aggregate into
a structural object that returns to the first root, and closures may compress
only while remaining corrigible.

## The problem it solves

The concrete complaint is navigational: too many folders and files to check,
and no way to know which ones currently matter. The structural complaint
underneath it is that authority is being inferred from **location, filename,
recency, and semantic similarity** — the exact inference
`AUTHORITY_GRAPH.json` names as its axiom of denial:

```text
NO_FILE_IS_LIVE_AUTHORITY_BY_LOCATION_RECENCY_NAME_OR_SEMANTIC_SIMILARITY
```

A directory tree cannot express that denial. It has exactly one relation
(containment), and containment is silently read as authority. The fix is not
fewer files. It is a second, declared structure in which authority, boundary,
and openness are explicit and checkable.

## Node = local centre

Root §2 already defines the object. A node is that object, bound to a scope:

| Root §2 | node field |
|---|---|
| 2.1 local centre | `authors` — what this node locally authors |
| 2.2 boundary | `boundary` — what it explicitly does not claim |
| 2.3 semantic interior | `scope` — the paths it governs |
| 2.5 receipt / independent return | `evidence` — returns it can cite |
| 2.6 residual | `residuals` — unclosed distinctions it carries |
| 2.7 provenance | `provenance` — where it came from |
| 2.8 reconstruction | `reopening` — what would reopen it |

## The four node laws

Root §0.4's boundary projections, read as constraints on the structure itself:

```text
unity without appropriation     C_i ↪ R,  C_i ≠ R
  every node embeds in the root and expands as a root, but is never the root

difference without exile        C_i ≠ R,  B_i ≠ ∅
  every node declares a non-empty boundary; a node that claims everything
  inside its subtree has exiled nothing and bounded nothing

relation without self-erasure   i remains locally authored under correction
  a parent may route to a child but may not author the child's claims

meaning without closure         ∃ρ able to reopen C_i
  every node names what would reopen it; a closure with no reopening
  condition is not a closure but a fossil
```

## Compression: the Strong-N2 condition

A node may compress its children into a central closure **iff it remains
Strong-N2** — a return arriving at any leaf can still propagate upward and
revise the compressed parent.

```text
Strong-N2  =  returned difference can revise a history-bearing closure
```

The fluid reading is exact: compression is admissible while flow stays
**laminar** — no eddies where a return circulates without reaching the centre —
and while boundaries stay **permeable** — no diodes. A compression that makes
a parent unrevisable by its own leaves is a diode, and is inadmissible however
elegant the summary.

Formally, with `F` the admitted future family at that scope
(`ADMITTED_FUTURE_FAMILY_CANDIDATE.json`):

```text
admissible(compress(node))  ⟺  ∀d ∈ F(scope):  separable(d) before  ⟹  separable(d) after
```

`Compress_F` may erase exactly what `F` cannot distinguish, and nothing else.

## Residuals are never gauge

This is what makes unfinished work structurally safe rather than a TODO list
that rots:

```text
a residual is, by definition, an unclosed distinction that still separates
admitted futures

⟹  μ_F(residual) ≠ 0  by construction
⟹  no admissible Compress_F may ever absorb a residual

silent corruption  ≡  illegitimate compression of a residual
```

So a residual is a first-class, non-compressible field on the node that carries
it. Work that is not finished is *declared on its node with a reopening
condition*, never dropped. The auditor's job is to verify every unclosed
residual is still reachable from the root — and to fail closed when a declared
residual silently stops reproducing, because disappearance is the failure, not
the resolution.

## The return: leaves feed the first root

The recursion does not terminate at the leaves. The union of unclosed leaf
residuals **is** the root's residual set, which is the next developmental
frontier:

```text
        ┌─────────────── root ───────────────┐
        │  authors: routing                   │
        │  residuals: ⋃ leaf residuals  ◀─────┼──┐
        └───────┬─────────────────────────────┘  │
                │ routes to                      │
        ┌───────▼───────┐   ┌───────────────┐    │
        │ node          │   │ node          │    │
        │ expands as    │   │ expands as    │    │
        │ a root        │   │ a root        │    │
        └───────┬───────┘   └───────┬───────┘    │
                │                   │            │
             leaves              leaves          │
                └─────── residuals ──────────────┘
                     structural object returning
                       to the first root
```

This is Ontology §3.4's sixth-order meta-loop applied to the repository: the
leaves' unclosed separators reconstruct the transformation-class the root must
next address. The tree is not a hierarchy of ownership; it is a circulation.

## Declaration

`NODE_GRAPH.json` at the branch root. One entry per node:

```json
{
  "id": "docs",
  "scope": ["docs/"],
  "parent": "root",
  "expands_as_root": true,
  "authors": "reader-facing routing surfaces for the routing layer",
  "boundary": ["does not author branch-local truth",
               "does not promote a branch claim by describing it"],
  "inherits_future_family": "docs",
  "evidence": ["..."],
  "residuals": [{"id": "...", "statement": "...", "reopening_condition": "..."}],
  "compression": {"admissible": true, "justification": "..."},
  "provenance": "..."
}
```

## Auditor rules

`scripts/audit_node_graph.py` checks the structure, never the content:

```text
N1  COVERAGE       every tracked path lies in exactly one node scope
N2  BOUNDARY       every node declares a non-empty boundary        (difference without exile)
N3  REOPENING      every node and every residual names a reopening condition
                                                                   (meaning without closure)
N4  ACYCLIC        parent links form a tree; the only cycle is the declared residual return
N5  REACHABLE      every unclosed residual is reachable from root  (residuals never gauge)
N6  NON_SOVEREIGN  no node claims authority over a sibling's scope (relation without self-erasure)
N7  RETURN_CLOSED  root residuals ⊇ union of leaf residuals        (the loop actually closes)
```

Structural conformance is not correctness:

```text
NODE_GRAPH_VALID != STRUCTURE_IS_RIGHT
COVERAGE != COMPREHENSION
declared_boundary != respected_boundary
```

## What this deliberately does not do

- It does not move, rename, merge, or delete any file. The declaration is a
  second structure over the existing tree, not a reorganization of it. A
  reorganization authored by an assistant is exactly the operation that
  produced the 2026-09-26 contamination.
- It does not decide what is gauge. That is `F`'s job, and `F` is the branch
  author's to declare.
- It does not replace the directory tree. Containment remains; it simply stops
  being the only relation, and stops being read as authority.

## Residuals of this document

| id | statement | reopening condition |
|---|---|---|
| `RNA_R1` | Applied only to the routing layer. The five split branches, which carry the real file volume, are undeclared. | Declare `NODE_GRAPH.json` on a split branch and run the auditor against it. |
| `RNA_R2` | `F` is referenced but the families it names live on `split/minerva` and are themselves candidates. Cross-branch `F` resolution is unspecified. | Decide whether `F` is per-branch or routed from root, and declare it. |
| `RNA_R3` | N7 is checkable but vacuous while leaf nodes declare few residuals. The loop can close trivially by declaring nothing. | Require that a node with no residuals justify the absence, rather than defaulting to it. |
| `RNA_R4` | Authored by an assistant, including the node laws' mapping onto Root §2 and §0.4. The mapping is a reading, and readings can be wrong. | Branch author confirms or corrects the mapping before any admission. |
