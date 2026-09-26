# Open residual register — 2026-09-26

Every unclosed question produced by the repair, the two lineage passes, the
adversarial review, and the extraction pass. One place, so none of them is
carried only in a candidate file nobody re-reads.

A residual is by construction a distinction that still separates admitted
futures, so `μ_F(residual) ≠ 0` and none of these may be compressed away.
Closing one means recording the return that closed it, not deleting the row.

**None of these are adjudicated.** Each is either solved or becomes an issue.
The `Reopens on` column is written to be pasteable as an issue acceptance
criterion.

Counts: 25 in `kernel/development/*.json` · 12 on `NODE_GRAPH.json` (proposal
branch) · 6 in the node architecture spec · 8 in the lineage study · plus the
unfixed review findings and the unstarted build work below.

---

## Tier 1 — blocks a load-bearing claim

| id | question | reopens on |
|---|---|---|
| `LIN-4` | **R198 and R206 name no validator.** `R198_INDEPENDENT_AUDIT.json` is titled independent, carries 27 booleans and `passed: true`, has no auditor identity, no custody field, no separation-of-authorship attestation, and its `_STDOUT.txt` is a byte-identical re-emission of its own output. R206's `V1`/`V2` are likewise unnamed. | Name the party that produced each. If it is the authoring party, `Reach(C)=1` rests on self-validation and the external-verifier clause that dissolves the Löbian obstacle is unsatisfied in practice, not merely in principle. |
| `REACH_C_R1` | No independent corrector exists. `V ≈ A` throughout. | A correction set authored by a party with no authorship relation to the system or curriculum. |
| `REACH_C_R2` | `epsilon` and `n` are undeclared, so the pass condition is not yet a test. | Branch author declares and freezes both before any baseline measurement. |
| `F_R1` | Every admitted-future family is `ASSISTANT_PROPOSED_CANDIDATE`. An assistant proposing the standard by which its own compressions are judged is the move that file exists to prevent. | Branch author reviews, edits and re-declares each family under their own authorship. |
| `LIN-2` | Was `NETWORK_SEMANTIC_TRACE_PREFREEZE.json` amended after a return? Edited in place at 11:14:47, two minutes after a commit whose mentor text forbids exactly that. | Actions run logs for 2026-09-26 11:09–11:14. A return predating `f9627d7` makes it a confirmed post-hoc amendment. |

## Tier 2 — record integrity

| id | question | reopens on |
|---|---|---|
| `LIN-3` | **EDU7 family absent from git.** EDU7, EDU7R1, EDU7R2 exist in the archaeology packet, two of them WITHHOLDs with 1580 and 1577 records. `provenance/developmental/EDU/` has no EDU7 artifact; `DEVELOPMENTAL_LINEAGE.md` elides the span. Not explained by externalization — sources are in hand. | Add them, or record an attested reason for exclusion. Until then git's EDU lineage is incomplete against a source we hold. |
| `LIN-1` | Canonical.zip pins three contaminated blobs as verified live state. | Repin against `445546d7` / `d49375d8` / `6b64252c`, or mark the package non-authoritative for those three paths. |
| `LIN-5` | Recovery-map flattening: `CANONICAL_CAPABILITY_RECOVERY_MAP.json` carries one `IG1_IG10_WORLDMIRROR_INCIDENCE` row dispositioned `LIVE`; IG5/IG6 failures and EDU17 are unrepresented. Now measurable against the project's own `mature reduction != genealogy erasure`. | Rule whether this is lawful gauge-consumption (failures survive in `DEVELOPMENTAL_LINEAGE.md`) or a status fossil. One cross-reference line would settle it. |
| `LIN-6` | 106 ledger sha256 entries are cross-attested by two independent packagings but never verified against source bytes. | Mount `/Backup/CanonicalExternalPayloads/` and hash the sources. |
| `LIN-7` | `RECOVERY_MANIFEST.json` declares scope "EDU13 through EDU17R1" but lists five files, none from EDU13/14/17. | Enumerate `Future/Execution/Raising/` from the external payload root. |
| `LIN-8` | R208 scores 1.0000 on four metrics. A working ablation control is consistent with real capability **and** with a saturated benchmark; the record cannot separate them. | A held-out family the model has not transferred to, or an independent evaluator. |
| `SS-R3` | A prefrozen artifact was modified in place with no superseded copy archived (same event as `LIN-2`, reached by a different method). | As `LIN-2`. |
| `SS-R4` | `README.md` lost the fence `can inspect != can claim`. It survives at `AGENTS.md:20`, `BRANCH_TREE.md:42`, `docs/GLOBAL_REPOSITORY_OPERATION.md:19`. | Decide whether the README specifically should carry it. Evidentiary half already closed. |

## Tier 3 — self-sealing findings, unadjudicated

Five R1 findings predating the contamination, three of them the same pattern.
See `kernel/development/SELF_SEALING_AUDIT_SCOPE.json` for full text.

| id | question | reopens on |
|---|---|---|
| `SS-R5/6/7` | `audit_autonomy_safety_matrix.py` edited alongside the matrix it guards, in three separate episodes. | Show an independent return between checker and matrix change, or declare the pair a single admitted unit with an external discriminator rather than leaving them mutually ratifying. |
| `SS-R8` | `lint_github_markdown.py` edited alongside README / ISSUE_ROADMAP / START_HERE / kernel-dev README. | As above. |
| `SS-R9` | `minerva-ci.yml` edited alongside `Makefile`. Likely benign coupling. | Confirm the workflow change did not weaken a gate in the same move the Makefile changed what that gate runs. |
| `SS-R1` | **The repair episode itself.** Restored the linter *and* made a novel edit to `docs/START_HERE.md`, a guarded surface, in one episode. | A party who did not author the repair confirms the START_HERE dedup against the restored navigation contract. |
| — | **Caveat on all five.** R1 precision is poor across long sessions: the largest episode on this branch is 308 commits, so a checker and a guarded file touched hours apart for unrelated reasons will fire. R1 is a prompt to look, not a verdict. | Tighten the episode definition — a commit-count cap, or proximity in the dependency graph rather than in time. |

## Tier 4 — recovered material not adopted

| id | question | reopens on |
|---|---|---|
| `RECOVERED_T_R1` | ~~no row for R199–R208~~ **widened and now mechanically tracked.** The matrix jumps **R194 → R209**, and `scripts/audit_dag_test_coverage.py` found **16** result-bearing revisions with no row — the full R195–R208 band plus two previously unknown: **`R176`** (the one confirmed B-EPISTEMIC crossing in the corpus, a held-out source consulted before partition and evaluator commitment, remediated by R178 without rewriting R176) and **`R187`** (repository provenance PASS, lowest value of the sixteen). | All sixteen are declared gaps in `provenance/DAG_TEST_COVERAGE_DISPOSITIONS.json`, printed every run. Close each by drafting a row and removing the gap, or by recording `NO_TEST_ROW_REQUIRED` with a rationale. A landing row makes its gap stale and **fails the audit** until removed explicitly, so gaps cannot rot. Sources are held for R195–R208; **`R176` and `R187` sources are not located.** |
| `SPEC_R1` | The Generator, Lateralizer, Internalizer and WorldMirror VM specifications in `kernel/development/RECOVERED_COMPONENT_SPECS_CANDIDATE.json` all come from an assistant-authored compression of a transcript that itself contains assistant turns. None is traced to a primary artifact. | Locate the transcript passage or an independent artifact for each before implementation. The compression is a finding aid, not a source. |
| `SPEC_R2` | `threshold_L` in the Lateralizer trigger, and the measurement procedure for both WorldMirror derivatives, are undeclared — so neither is yet a test. | Declare `threshold_L` and a complexity measure for special-purpose scaffold, and freeze both before any run scored against them. |
| `SPEC_R3` | `REDUCE(σ) admissible ⟺ INTERNALIZED(h) ∧ matched_consequence_survives(¬σ)` is the gate governing scaffold removal — the exact operation the 2026-09-26 contamination performed without warrant when it redispositioned `task_graph.py`. No live gate implements it. | Implement as a check over `VM_INTERNALIZATION_PHASE_PLAN.json` dispositions, so a path cannot move to a reduced disposition without both conjuncts evidenced. |
| `RECOVERED_T_R2` | Five recovered protocols are recorded, none implemented. | Implement `P-R207` first: most completely specified, least dependent on absent runtime. |
| `RECOVERED_T_R3` | `P-R206` and `P-R204` reference runtime and generator state that may no longer exist. | Check required inputs against the current kernel before scheduling. |
| `RECOVERED_D_R1` | Eight recovered distinctions are recorded, none adopted as live fences. | Branch author selects which to adopt and supplies a test reference for each. |
| `RECOVERED_D_R2` | Live coverage was assessed by grep for the fence string; a distinction enforced under another name would score absent. | Semantic rather than lexical check against the matrix's 118 entries. |

## Tier 5 — structural, from the adversarial review

| id | question | reopens on |
|---|---|---|
| `RNA_R5` | **The node graph is a flat star** — nine nodes, all depth one. Despite the name, no node expands as a root; there is no intermediate level for a leaf residual to climb through. The recursion is asserted by the spec and not instantiated. | Declare a node with children on a branch with real depth, and show a leaf residual propagating through an intermediate node to root. |
| `RNA_R1` | Applied only to the routing layer (51 files). The five split branches, where the file volume and the original navigation problem live, are undeclared. | Declare `NODE_GRAPH.json` on a split branch and run the auditor. |
| `RNA_R6` / `TESTS_R1` | `N5 REACHABLE` cannot fire independently of `N4` and is therefore untested rather than merely uncovered. | Construct a graph violating N5 while satisfying N4, or retire N5 and record that N4 subsumes it. |
| `RNA_R2` | `F` is referenced but the families live on another branch and are candidates. Cross-branch `F` resolution unspecified. | Decide whether `F` is per-branch or routed from root. |
| `RNA_R3` | N7 can close trivially if nodes declare no residuals. | Require a node with no residuals to justify the absence. Partially done — `licenses` carries a justification and N3 enforces it. |
| `ROOT_R1` | `aggregates_residuals` is authored, not derived. | Auditor derives it from the node set. |
| `GH_R1` | No workflow runs the node-graph auditor. | Wire it in, once the graph is admitted. |
| `TESTS_R2` | No test runner wired on the routing branch. | Add `python3 -m unittest discover tests`. |
| — | **H5, not fixable.** Earlier commit messages assert derived claims ("non-sovereignty … is the device that makes safe RSI formally coherent") with no DERIVED qualifier. Those commits exist. | Correctable only forward. Future commit messages carry the qualifier. |
| — | R1/R3 ignore deletions; R2 follows only the post-rename path; `audit_since` hides all history before 2026-09-26. | Recorded in `known_limitations`. Each is a separate small fix. |

## Tier 6 — requested but not started

Held by the branch author. Listed so the register is complete, not to assign.

> **Corrected 2026-09-26.** An independent pass over the lateral-compression
> document found two rows below were **wrong** as first written, both
> understating live state. The errors were mine, made in a completeness audit
> delivered to the branch author. Verified corrections are recorded in place;
> the original claims are kept struck so the mistake stays visible.

| item | state |
|---|---|
| WorldMirror VM hardening — tougher sandbox, minimal machinery, most internalised, self-sufficient | largely untouched, but the intent is **specified**: "the interface/body should be minimal … preferable to a richly predesigned virtual environment", with the asymptotic target `d(complexity_special_scaffold)/dt < 0` while `d(general_competence)/dt > 0`. `WORLDMIRROR_CONSOLE_POLICY.json` already concedes the gap: `security_claim: ARGV_CWD_SIZE_TIMEOUT_BOUNDARY_ONLY_NOT_OS_SANDBOX`, `untrusted_machine_execution_requires_external_sandbox: true`. **The OS-level sandbox is the missing artifact, not the design.** |
| Lateralizer | ~~no implementation~~ → an **operational independence criterion exists in the archive and not in the repo**: `I(Return_i ; Return_j \| hidden_structure) < I(Return_i ; hidden_structure)`, or operationally "there exists an admissible perturbation under which two views make separable predictions", with trigger `LATERALIZE ⇔ E[IG(D \| {R_t^i})] − cost_L > threshold_L`. Live `LATERAL_EPISODE_1_PREFREEZE.json` has only `independently_answerable: true`. |
| Internalizer | admission rule exists in the archive, absent live: `REDUCE(σ) admissible ⇔ INTERNALIZED(h) ∧ matched_consequence_survives(¬σ)`. No live scaffold-reduction gate. |
| Generator | the **only** specification anywhere is archival: `G_t : (S_t, Q_t, M_t) → 𝒫(Π_t)`, each proposal carrying a target distinction, expected discriminator, admissible action/query class and proof burden, selected by `π*_t = argmax V(π \| cost, uncertainty, blocked_dependencies, expected_information_gain)`. Nothing live implements it. |
| DAG mentoring | ~~not started~~ **WRONG AS WRITTEN.** `kernel/development/SELF_TEACHING_DEVELOPMENT_DAG.json` is live with nodes A_RETURN_CREDIT_ASSIGNMENT / B_DEPENDENCY_DAG_PLANNING / C_UNCERTAINTY_NONSTATIONARITY / D_RSI_RECURRENCE_AUDIT / E_INTERNALIZATION, `current_parallel_frontier: [A, B]`, `current_join: [D]`, and seven invariants incl. `RETURN_COUNT!=EVIDENCE_COUNT`, `CRITICAL_PATH!=IMPORTANCE`, `B1!=B2!=B3`. `autonomy/interaction/mentor/TEACHING_PLAN_2026-09-26.md` (26K) instantiates the fade ladder — unknown-door exposure → discriminator coaching → adversarial review → silence. **What is missing is episodes on the DAG, not the DAG or the protocol.** |
| Language/Music/Theater × EN/JA/PT/Math curricula | ~~zero episodes authored~~ **WRONG AS WRITTEN.** Seven episodes exist: `COGNITIVE_THEATER_{BINDING_ORDER,BINDING_ORDER_FRESH2,RELATIONAL_GRAPH_FRESH3,JOINT_SCENE_FRESH4,LOCAL_OPERATOR_FRESH5,EXPLICIT_STATE_FRESH6,SOURCE_REMOVAL_FRESH7}_RESULT.json`, plus the factorial baseline. The operator binding added this session is a candidate layer *over* existing episodes, not a first step. Missing: episodes exercising the `expressive_mode × face` product space, which is `THEATER_R1`. |
| Strong Safe RSI / RSM / N2 / two O* / Anti-Minerva | traced; `REACH_C` proposed, never run. The lateral-compression document **names none of RSM, N2, the two O*, or Anti-Minerva anywhere** — a negative result worth recording, since it means that vocabulary's specification lives elsewhere. |
| Return credit / dependency planning | **not previously listed and it exists** — `RETURN_CREDIT_ASSIGNMENT_PREFREEZE.json`, `DEPENDENCY_PLANNING_CURRICULUM_PREFREEZE.json`, curricula and tests. The archive insists A and B are *separate* branches that "only join later in a Strong Safe RSI recurrence audit"; the external agent's collapse of the two is a textbook success-composition fallacy. |
| Full superficial commit ledger across all 3006 commits / 207 refs | **not done.** A style-and-date fingerprint was substituted. History before 2026-09-25 was never scanned, and `audit_since` bakes that gap into the tool. |
| B9 Strong-N2, B10 RSM/RSI split, B12 theater product space | in candidate files; none admitted to the gate chain |

---

## How to close a row

1. Record the return that closed it — a run id, a diff, a named party, a file.
2. Move it to a `closed_residuals` entry in the owning artifact with that return.
3. Do **not** delete the row. `R4_RESIDUAL_DELETED` in the self-sealing auditor
   fails closed on silent disappearance, because disappearance and resolution
   are indistinguishable from the outside.
