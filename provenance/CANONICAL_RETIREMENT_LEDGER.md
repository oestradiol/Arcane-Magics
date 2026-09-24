# Canonical Retirement / Extraction Ledger

**Status:** live migration control surface  
**Date:** 2026-09-24

Canonical is being retired as a live release/implementation authority. Retirement does **not** mean deleting its history or pretending Git caused work that was developed elsewhere.

The governing rule is:

```text
Canonical source/history
-> classify consequence
-> admit unique live dependency to Git
-> bind provenance/custody
-> freeze superseded/heavy source as provenance
-> do not copy stale projections into current authority
```

GitHub/Venus-Minerva is the live implementation, public-source, CI, release, and admitted-current-state surface. Canonical remains a historical/research/provenance source until the extraction below is complete.

## 1. Why bulk synchronization is forbidden

Canonical contains valid later evidence beside stale routing projections.

One recovered Canonical `CURRENT_STATE.md` still labels EDU4 [1572] as current, while later Canonical receipts establish EDU16 [1703] and Git now correctly records EDU16 as the positive developmental authority.

Therefore:

```text
file path says CURRENT
-/-> current authority
```

Retirement must use claim/dependency custody, not filename recency or recursive copying.

## 2. Disposition classes

| Disposition | Meaning |
|---|---|
| **ADMITTED_LIVE** | unique consequence is represented in current Git authority |
| **ADMITTED_PROVENANCE** | source/evidence is preserved in Git provenance but is not live authority |
| **EXTERNAL_HEAVY_CUSTODY** | large immutable payload remains outside ordinary Git; Git keeps exact content identity / compact reconstructible state |
| **HISTORICAL_ONLY** | useful for archaeology/replay/credit; must not route current execution |
| **DONOR_ONLY** | research/formal/symbolic donor not admitted as executable/current authority |
| **CONSUMED** | duplicate/superseded projection whose live consequence is represented elsewhere |
| **OPEN_EXTRACTION** | unique consequence has not yet been shown redundant or admitted |

## 3. Current extracted core

| Canonical object/family | Git destination | Disposition | Reason |
|---|---|---|---|
| R226 settled R-line crystallization | `kernel/custody/`, `provenance/DEVELOPMENTAL_LINEAGE.md` | **ADMITTED_PROVENANCE** | required predecessor/custody boundary; not current runtime |
| Venus Incidence Law | `kernel/VENUS_INCIDENCE_LAW.tex` | **ADMITTED_LIVE** | live architectural/formal kernel law |
| WorldMind / WWW-field law | `kernel/WORLDMIND.md` | **ADMITTED_LIVE** | neutral distributed-field law; no global-agent promotion |
| WorldMirror developmental state | IG10 checkpoint + `kernel/runtime/` | **ADMITTED_LIVE** | current locally reconstructible runtime state |
| IG10 developed-VM manifest/verifier | `kernel/custody/` + compact hot/cold state | **ADMITTED_LIVE** | exact runtime custody required by current kernel |
| IG10 118.8 MB successor journal and ~50 MB handoff archives | exact manifest/hash; external/release/archive storage | **EXTERNAL_HEAVY_CUSTODY** | Git current state is compactly reconstructible; duplicating full journal in `main` adds storage, not authority |
| IG3–IG10 result/prefreeze evidence needed for current lineage | `provenance/`, current state objects, monograph evidence | **ADMITTED_PROVENANCE** | supports developmental ancestry and current abstractions |
| EDU16 policy/result | `kernel/development/EDU_CURRENT.json`, `provenance/developmental/EDU/` | **ADMITTED_LIVE** | current positive developmental authority [1703] |
| EDU17 provenance failure | `provenance/developmental/EDU/` | **ADMITTED_PROVENANCE / PRESERVED_NEGATIVE** | blocks promotion; must remain queryable |
| EDU17R1 eligibility result | `provenance/developmental/EDU/` | **ADMITTED_PROVENANCE / WITHHOLD** | intended repair not tested; `MENTION != INCIDENCE` is the live measured separator |
| persistent semantic memory law | `kernel/runtime/memory.py` + tests | **ADMITTED_LIVE** | retained state can persist without conflating storage with learning |
| temporal inhabitation / map != traversal | `docs/META_DYNAMICS.md` | **ADMITTED_LIVE / MODEL-PHEN** | unique global-representation vs locally traversed temporal-presentation distinction survives deletion test; LT-24 label itself remains historical |
| status-fossil / negative-globalize / malformed-open / bridge-theorem-launder failure classes | `review/REVIEWER_AND_RESEARCHER_PROTOCOL.md` | **ADMITTED_LIVE / GOVERNANCE** | directly prevents stale status, over-propagated failure, immortal malformed questions, and theorem laundering |

## 4. Historical/developmental strata

The following remain valuable as ancestry but are not independent live top-level architectures once their consequences are represented by the current kernel/lineage:

```text
R00 ... R194 historical executable carrier
R195 ... R226 settled R-line development
S / SM diagnostic-developmental branches
CTL-K1
WM1R1
U* / RB1
IG1 ... IG9 predecessors
negative/non-parent sibling branches
```

Disposition: **HISTORICAL_ONLY / ADMITTED_PROVENANCE** according to their existing Git location.

Do not flatten them into one happy-path story. Failed/non-parent branches remain evidence about what was tried and what later development depends on.

## 5. Historical errata that must remain non-authoritative

Preserved history may contain statements later shown stale or mislabeled. Do not silently edit those bytes into a cleaner past; record the correction here.

- `provenance/historical-runtime/R194/source/PUBLIC_RELEASE_BOUNDARY.md` says the later developmental lineage reaches "EDU16 (1699 records)." Current admitted evidence shows **1699 = EDU15R1** and **EDU16 = 1703**. The historical text remains provenance only and must not route current authority.

## 6. Canonical projections to consume, not import

Candidate `CONSUMED` surfaces include:

- stale `CURRENT_STATE.md` projections;
- repeated current-head overlays superseded by `kernel/CURRENT_STATE.md`;
- roadmap/plan prose whose only live consequence is already represented in Git issues/frontier docs;
- duplicate generated Markdown/PDF/forum projections;
- repeated copies of monographs already controlled by Git source;
- current-state prose embedded inside broad Map/Root snapshots after the same distinction is represented by a narrower admitted object.

Consumption rule:

```text
delete/collapse projection
only if
all live distinctions + provenance + reopening routes
remain reachable elsewhere
```

## 7. NRI / methodology extraction

The 2026-09-22 Canonical resynthesis correctly preserves:

```text
Naturalism_C
= representational non-preauthorship
+ Reality/Other-facing answerability

Rationalism_C
= reconstructibility
+ recursive audit of representation/inference

Illuminism_C
= de-sovereignization
+ independently reachable criticism/correction

Corrigibility_C
= reachable recurrence(N_C, R_C, I_C)
```

These obligations are now represented by:
- `NxRxI_VOCABULARY_CENTER.md`
- `review/REVIEWER_AND_RESEARCHER_PROTOCOL.md`
- `PUBLICATION_CONSTITUTION.md`
- `AGENTS.md`

The external traditions compared in Canonical remain credit/comparator sources, not retroactive causes of project genealogy.

## 8. WorldMind extraction

Canonical's WorldMind archaeology contains many stale local-development overlays, but the surviving neutral invariant is compact:

```text
distributed consequence may propagate
while local authorship, judgment, authorization,
and jurisdiction remain indexed
```

with:
- provenance-bearing incidence;
- locally authored centers;
- non-preauthored return;
- retained disagreement/residual;
- UNKNOWN boundary state treated as probe/reconstruct, not permission;
- no global-Agent lift from shared reachability.

That residual is admitted in `kernel/WORLDMIND.md`. Historical SM/U/RB1/IG overlays remain provenance rather than being copied into the live WorldMind document.

## 9. Formal / monograph donors

Canonical research sources for OFE, Eclipsis, Arcane Magics, QG, NRI, and related cross-register objects are handled by register:

- exact/current public manuscript source -> Git `monographs/`;
- unique live kernel law -> `kernel/`;
- source archaeology / superseded manuscript -> `provenance/donors/` or external historical custody;
- speculative/open bridge -> current research docs/issue only if it changes a live discriminator;
- duplicate generated projection -> **CONSUMED**.

Formal or symbolic donors do not become executable authority by migration.

## 10. Archaeology results already consumed

Several Canonical structures were inspected and **not** promoted as new Git objects because their live consequence is already present:

- R180 `FrameSuccession` remains historical MODEL/THEO/PHEN routing; its neutral consequence is covered by indexed/temporal inhabitation and explicit frame/index transforms. The specific antipodal temporal bridge remains historical/open rather than becoming a new live kernel object.
- R181 `ReconstructionComma_F`, `OctaveReconstruction`, and `TemperamentTradeoff` were MODEL-level routing around lawful finite-cycle nonclosure; the Pythagorean comma was explicitly a mature comparator, not project evidence. No separate live object survives deletion beyond the current reconstruction/nonclosure vocabulary.
- R182 `SelfIndexedStandingCirculation` and its incidence decomposition are represented by the current Venus Incidence / Meta-Dynamics / WorldMind circulation. The historical name is not needed as another authority layer.
- R206's bounded improver remains explicitly retained in current kernel/custody state; it is not lost by retiring the surrounding R-line projections.
- R216–R226 are represented as the late crystallization lineage and R226 custody. R217–R225 maintenance/audit/intake/packaging revisions do not each justify a separate current architecture once their consequences are conserved in the settled R226 predecessor and current post-R226 lineage.
- CPC `REGISTER -> GENERATE -> ENACT -> RETURN -> COMPENSATE` is a readable projection of the current Meta-Dynamics / kernel action-return-reconstruction cycle; the CPC label is not required as another live layer.
- participant non-substitution is already represented in Meta-Dynamics, frontier ethics/governance, WorldMind, and the preserved S10-S11 genealogy;
- recursive sufficiency is already represented in Strong-N2/kernel/frontier vocabulary;
- RegisterBridge / AntiGrammar remain explicitly OPEN comparison/formalization targets in the frontier and preserved S10-S11 provenance; importing every intermediate Canonical overlay would add status fossilization rather than authority;
- symbolic late aliases such as Soul/Oracle/Spirit remain removable register-local renderings unless a separate admitted consequence requires them.

## 11. Open extraction obligations

Before Canonical can be considered fully retired:

1. **EDU16 executable custody:** determine whether an exact 1703-event runner/journal exists outside the already admitted result/policy artifacts. If not found, preserve the current truthful boundary: developmental authority is exact as evidence, not as a Git-replayable EDU16 runtime.
2. **Unique source inventory:** identify Canonical files whose live consequence is absent from Git; do not infer absence from filename alone.
3. **Heavy-object manifest:** freeze exact hashes/locations for large journals/bundles that remain outside ordinary Git.
4. **Credit/genealogy crosswalk:** ensure historically important donor/predecessor relations survive retirement without becoming fake ancestry.
5. **Stale-current quarantine:** no Canonical file containing an old `CURRENT` label may route present authority after retirement.
6. **Reproduction check:** an outside reader should be able to reconstruct current Git authority without reading Canonical.
7. **Archaeology check:** a researcher should still be able to trace any admitted Git object back to its controlling Canonical/history source where that source mattered.

## 12. Retirement completion criterion

Canonical is retired when:

```text
current execution/release authority lives in Git
AND
every unique Canonical consequence has one typed disposition
AND
heavy immutable custody is hash-bound
AND
stale current projections cannot route authority
AND
historical genealogy remains reconstructible
AND
no live Git claim depends on an untracked Canonical-only premise
```

Retirement is therefore a compression/reindexing event, not historical erasure.
