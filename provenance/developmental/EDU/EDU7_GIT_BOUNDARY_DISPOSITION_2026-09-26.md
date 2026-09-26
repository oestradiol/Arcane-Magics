# EDU7 family — git-boundary disposition

**Status: restored 2026-09-26. Negative results, first-class, non-parent.**

## What happened

The EDU7 family produced three results, all WITHHOLD:

```text
EDU7    WITHHOLD_EDU7_POLYHEDRAL_SELF_GEOMETRY   1580 records
EDU7R1  WITHHOLD_EDU7R1_EDGE_GLUE_REPAIR         1577 records
EDU7R2  WITHHOLD_EDU7R2_FACE_LOCALIZED_GLUE      1577 records
```

All three survived in execution custody under
`/Backup/CanonicalExternalPayloads/.../Future/Execution/`, with prefreezes,
result JSON and MD, and runner code. None survived into git-side developmental
provenance. `DEVELOPMENTAL_LINEAGE.md` elided the span as `EDU4 → … → EDU15`.

This is **not** the EDU17 case. EDU17's absence is explained by deliberate
externalization of its source tree. Here the result-bearing sources survive
locally and the projection dropped them anyway. The defect is therefore:

```text
negative-result survival in execution custody
!=
negative-result survival across git/provenance projection
```

Against the project's own rule that negative, invalid and harness-invalid
branches remain first-class provenance, that is a structural loss, and it is
an instance of the pattern this repository keeps finding in itself:

```text
result exists
→ projection/reconciliation compresses it
→ provenance layer loses the actor / negative / test-row distinction
→ current state still references the surviving high-level claim
```

## What was restored

Six files, copied **byte-exact** from external payload custody and verified
against the bundle's SHA256 manifest:

```text
EDU7_POLYHEDRAL_SELF_GEOMETRY_PREFREEZE.md        ae0b5fe95ddf9e09…
EDU7_POLYHEDRAL_SELF_GEOMETRY_RESULT.md           ea856f7c60c4f838…
EDU7R1_POLYHEDRAL_EDGE_GLUE_REPAIR_PREFREEZE.md   5c5d67bf228d5d4a…
EDU7R1_POLYHEDRAL_EDGE_GLUE_REPAIR_RESULT.md      20437ee390111766…
EDU7R2_FACE_LOCALIZED_GLUE_PREFREEZE.md           003659c7b2134690…
EDU7R2_FACE_LOCALIZED_GLUE_RESULT.md              efc886439f27cde9…
```

Nothing was rewritten, summarised, or reformatted.

## What was NOT copied, and where it is

Exact-byte execution payloads remain in external custody. They are recorded
here by hash so the pointer survives even if the payload root moves:

```text
EDU7_POLYHEDRAL_SELF_GEOMETRY_RESULT.json         4b72892697c3a02e…   32K
EDU7R1_POLYHEDRAL_EDGE_GLUE_REPAIR_RESULT.json    90838ca3f1b10025…   10K
EDU7R2_FACE_LOCALIZED_GLUE_RESULT.json            b193e98ad5a8e880…   34K
run_edu7.py                                       87e22ba8c8f210b7…   29K
run_edu7r1.py                                     c346057a6254bdfa…   17K
run_edu7r2.py                                     8c40c0cb96b1035c…   13K
```

`/Backup/CanonicalExternalPayloads/` was **not reachable** from the machine
that performed this restoration. The hashes above come from the forensic
bundle's own manifest, which verified clean. They are therefore
cross-attested, not verified against the payload root. That limitation is
recorded rather than inferred away.

## What the results actually found

Worth stating, because a WITHHOLD that is merely listed becomes invisible.

EDU7 tested a **nameless typed factor/edge representation before** the
Polyhedral vocabulary was admitted. A targeted correction altered only the
`jurisdiction` component; the other learned components stayed byte-identical.
Then, decisively:

> An opaque neutral graph with the same factorization preserves the same
> consequence partition, and label ablation leaves predictions unchanged.
> Therefore **the Polyhedral names/geometry receive no algorithmic privilege at
> this scope**. What survives is the typed factorized operator-self-model
> invariant.

EDU7R1 changed only scope and jurisdiction faces, keeping warrant and
causal-stage byte-identical, and explicitly preserved EDU7 as a negative
sibling. EDU7R2 changed only representational segmentation and gluing, touching
no semantic training bank, and scored 0.500 on both whole-scenario and
face-localized accuracy.

The family's standing conclusion is that the useful object is **persistent
self-indexing by role/boundary/operator with dependency-local learning** — not
self-grounding, not project-name recovery, and not promotion of the
phenomenological, theological or physical registers. Grounding remains external
through non-preauthored return.

This is a good negative result. It ran an ablation against its own preferred
vocabulary and reported that the vocabulary earned nothing.

## Related custody gaps, recorded not repaired

Two findings from the same forensic pass concern validator identity rather than
negative-result survival. They are recorded here because they share the pattern
and are tracked in `provenance/OPEN_RESIDUAL_REGISTER_2026-09-26.md` as `LIN-4`.

**R198.** `R198_INDEPENDENT_AUDIT.json` carries schema
`Canonical.R198.IndependentAudit.v1`, 27 boolean checks, and `passed: true`. It
carries no auditor identity, no execution principal, no custody or environment
identity, no independent-party identifier, and no authorship-separation
attestation. `verify_r198_independent.py` constructs the report, writes it to
`/mnt/data/r198_execution/final/R198_INDEPENDENT_AUDIT.json`, then prints the
same serialized object — the stdout is byte-identical to the JSON. So the
artifact establishes *a verification program ran and all encoded checks
returned true*, and not independent validator identity, custody, or separation
of authorship. The name `IndependentAudit` is stronger than the preserved
evidence supports.

**R206.** The prefreeze requires `I0 → diagnosed limitation → governed ΔI1 →
separate validation V1 → I1 retained → later candidate delta → separate
validation V2`, and generation 2 carries
`V2_selected_repair_independently_validates: true`. No preserved artifact
identifies V1 or V2, their program hash, their custody or execution boundary,
or whether producer and validator share implementation lineage. Preserved:
`validation predicate = true`. Not preserved:
`independent validation provenance established`.

Both are materially weaker than they read. Neither is repaired here, because
supplying a validator identity that was never recorded would be invention. What
is needed is a statement of what "independent" meant in each case — process
separation, code separation, actor separation, or only a separate function
invocation.

```text
validation != independent validation
named audit != demonstrated custody separation
```
