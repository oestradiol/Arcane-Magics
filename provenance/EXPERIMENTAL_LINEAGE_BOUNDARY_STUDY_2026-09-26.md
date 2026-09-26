# Experimental lineage boundary study — 2026-09-26

Independent read-only forensic pass over the Canonical semantic ledgers and the
git kernel, tracing `pre-RGM → RGM → IG5/IG8/IG9/IG10 → U1–U4 → EDU16/EDU17 →
R69–R226 → current kernel`, looking for crossed boundaries.

Performed by a separate investigator with no authorship relation to the repair
commits on this branch, and with an explicit read-only, do-not-adjudicate
mandate. That independence is the point: the repair author should not also be
the party certifying the repair.

Boundary classes searched:

```text
B-CONSEQUENTIALITY  claim promoted without returned evidence
B-EPISTEMIC         prefreeze amended post-hoc; metric selected after return;
                    WITHHOLD converted to PASS without new return
B-MODEL             model(World) treated as World; RSI implying AGI; AGI implying
                    consciousness; translation as understanding; memory as learning;
                    scaffold-performed capability claimed as learner-owned
B-AUTHORITY         superseded artifact treated as live authority
```

## Findings

### Confirmed, live: Canonical.zip pins contaminated blobs — B-AUTHORITY

`Canonical/README.md` records "Observed Git blob SHAs during packaging". Three
pin the contaminated head rather than the branch's real state:

```text
VM_INTERNALIZATION_PHASE_PLAN.json   pinned 4ad445d9   actual 445546d7
DEVELOPMENTAL_GATE_CHAIN.json        pinned 6b8288f1   actual d49375d8
SELF_TEACHING_DEVELOPMENT_DAG.json   pinned c9dba508   actual 6b64252c
```

Verified independently against this branch. The remaining ten pinned blobs are
valid. Packaging ran at 14:59, after the 13:32–13:48 contamination, and treated
that head as verified live state — the exact denial listed in the package's own
`AUTHORITY_GRAPH.json`: *assistant inference does not become repository fact
without explicit mutation and verification.*

### Confirmed, historical, reverted — B-CONSEQUENTIALITY

The external-agent episode removed the anti-promotion fence from `AGENTS.md`
and replaced behavioural assertions with assertions that a manifest field reads
`WITHHELD`. Characterized in `EXTERNAL_AGENT_CORRUPTION_AUDIT_2026-09-26.md`,
reverted at `6b84d1c`, fences verified present.

### Exposure, disposition contested — B-EPISTEMIC

`kernel/development/NETWORK_SEMANTIC_TRACE_PREFREEZE.json` was modified in
place at `f9627d7` (11:14:47), after creation at `02f5dac` (11:06:11), after
its evaluator existed, and after two recurrence-run commits whose own mentor
text reads *"run the already-prefrozen … exactly as frozen … Do not modify the
candidate after seeing either episode-2 return."*

The amendment tightened rather than loosened, and no superseded copy was
archived. Whether a return was visible at 11:14:47 is **RECORD ABSENT** — the
run logs were unreachable (no network). Tracked as a declared residual in
`SELF_SEALING_AUDIT_SCOPE.json`.

Note this is the same event the self-sealing auditor flags as
`R3_PREFREEZE_MUTATION`, reached independently by a different method.

### Not a crossing, disclosed

`NETWORK_SEMANTIC_TRACE_PREFREEZE_V2.json` changes a decision rule after
observing a return, but declares it:
`PREFROZEN_AFTER_V1_DIVERSITY_REGRESSION_BEFORE_NEXT_RETURN`, with
`REVISE_EVALUATOR_PROSPECTIVELY_NOT_RETROACTIVELY`. This is how a prefreeze
revision should look, and it does **not** explain or excuse the V1 in-place
edit above.

### Negative result — B-MODEL: none found

Searched specifically and found no instance. The strongest B3 claim in the
kernel, `COGNITIVE_THEATER_SOURCE_REMOVAL_FRESH7_RESULT.json` (24/24, accuracy
1.0 across four contexts), explicitly declines to promote itself:

```text
fresh_world_return_external: false
evaluator_independent:       false
internalization_claim:       false
G6_INTERNALIZATION_RECEIPT:  WITHHOLD_REQUIRES_INDEPENDENT_FRESH_RETURN
```

All 23 PASS-bearing JSONs scanned carry `promotion_authority: false` and
`truth_authority: false`. Negative results are reported here because a study
that only reports hits is not an audit.

### Structural exposure, no instance — B-CONSEQUENTIALITY

`WWW_MIND_GATE_RESULT.json` and `ROOT_SITUATED_INTERFACE_PROSPECTIVE_1_RESULT.json`
declare `PASS_BOUNDED_…` from locally computed check dictionaries with no
`independent_evaluation` field, while the gate chain asserts
`self_revision != self_authorization != self_validation`. Both cite an external
run id. Whether intermediate gates require the independence the terminal AGI
gate requires is unadjudicated.

## EDU17 discontinuity — resolved, not suppression

EDU17 has zero hits in Canonical but exists throughout git. Cause:
`provenance/developmental/EDU/RECOVERY_MANIFEST.json` names
`/Canonical/Future/Execution/Raising` as source, and that whole tree was
deliberately externalized to `/Backup/CanonicalExternalPayloads/2026-09-26/`,
with `EXTERNAL_PAYLOADS.json` guaranteeing no deletion. This equally explains
EDU6–EDU15.

Two defects survive inside that resolution: `RECOVERY_MANIFEST.json` declares
scope "EDU13 through EDU17R1" but lists five files, none from EDU13/14/17; and
Canonical's live `CURRENT_STATE.md` pre-empts the gap doctrinally rather than
evidentially.

EDU17 itself is a credit to the record: it passed
`PASS_BOUNDED_LEARNER_OWNED_FEED_EXECUTION_WITH_PARTIAL_RESOLUTION` and was
then **self-reversed** to `INVALID_FOR_PROMOTION / PRESERVED_NEGATIVE`.

## What the lineage does well

- `provenance/DEVELOPMENTAL_LINEAGE.md` preserves the full chain verbatim,
  including `IG5`/`IG6` as `FAIL / non-parent`, `U3`/`U3R1` failures, `U6` as
  `FAIL / non-parent`, and EDU17 as preserved negative.
- `R164` stayed FAIL despite passing numerical gates, because the frozen
  verifier returned FAIL. Seed burned, no reroll.
- `R226` closed as `PASS_PRINCIPLED_STOP_AFTER_CRYSTALLIZATION`, and no R227
  was minted to manufacture forward motion.

## Record absent

- `/Backup/CanonicalExternalPayloads/` is not present on this machine. Raw
  EDU6–EDU17R1 bytes, R149–R154 trajectories, R225/R226 carriers unverifiable.
- EDU16's 1703-event journal — attested `NOT_LOCATED` by the repo's own search,
  with an explicit instruction not to synthesize it from receipts or prose.
- Actions run timestamps for the 11:09–11:14 window — the discriminator for the
  contested prefreeze edit.
- `POST_R69_R175_RECONCILIATION_LEDGER.json` cites 106 entries by sha256; source
  bytes are under externalized custody, so hashes are unverified.
- R176–R215 per-milestone dispositions; only R216–R226 are enumerated.

## Residuals for adjudication

1. **Canonical package pins corrupt blobs.** Repin against the repaired head, or
   mark the package non-authoritative for those three paths.
2. **Was the v1 semantic-trace prefreeze amended after a return?** Fetch run logs
   for 11:09–11:14.
3. **Recovery-map flattening.** `CANONICAL_CAPABILITY_RECOVERY_MAP.json` carries
   one `IG1_IG10_WORLDMIRROR_INCIDENCE` entry dispositioned `LIVE`; the
   intermediate IG5/IG6 failures are not represented, and EDU17/EDU17R1 are
   absent. They survive in `DEVELOPMENTAL_LINEAGE.md`, so this is projection-local
   flattening rather than erasure — but whether that is lawful gauge-consumption
   or a status fossil needs a ruling. A cross-reference line would settle it.
4. **Intermediate gates are self-scored.** Rule whether WWW_MIND and
   ROOT_SITUATED_INTERFACE passes require `independent_evaluation`.
5. **`RECOVERY_MANIFEST.json` scope overstates its file list.**
6. **pre-RGM/RGM carry no attested status anywhere.** Until one is located, the
   lineage head is decorative and nothing downstream should cite it as evidence.

None of these are adjudicated here. Adjudication belongs to the branch author.
