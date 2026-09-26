# Causal chain trace — Minerva → Safe Strong Non-Sovereign Epistemic RSI/RSM centre → AGI telos

**Register: CANDIDATE. Assistant-derived synthesis, not admitted repository law.**

This traces the developmental chain end to end and fills its inference gaps
formally. Where the repository already attests something, it is cited. Where
this document derives something new, it says so. The distinction matters more
than the content: an assistant's reconstruction of a system's own logic is
exactly the kind of plausible object that should not become authority by being
convincing.

## 0. Primitives

`S_t` learner state · `M_t` machinery (executor + scaffold) · `F` admitted
future family · `ρ` non-preauthored return · `C` correction channel · `A_x`
ablation of `x`.

Root §1.3 supplies the only measure the chain needs:

```text
μ_F(x) ≠ 0   ⟺   Future_F(A_x(Σ)) ≠ Future_F(Σ)
```

Meaning is counterfactual impact on the admitted future. Everything below is
bookkeeping on `μ_F`. Note `F` is a parameter, and until
`ADMITTED_FUTURE_FAMILY_CANDIDATE.json` is admitted, `μ_F` is not yet a number.

## 1. The three burdens are one statement about where measure sits

DERIVED. `THREE_BURDEN_LEARNING_PROOF.json` presents B1/B2/B3 as three tests.
They are one claim about the location of `μ_F` mass:

```text
B2  causal use        μ_F(S_cap) ≠ 0
B3  internalization   μ_F(M_cap) = 0  ∧  μ_F(S_cap) ≠ 0
```

Internalization is **measure migration**: capability-specific machinery becomes
gauge while learner state becomes load-bearing. "Minimal machinery, most
internalised" is therefore not an aesthetic preference but the literal success
condition, and `μ_F(M_cap) = 0` is the definition of a removable scaffold.

B1 is the precondition that makes `μ_F` well defined: without held-out
recombination and surface-invariance controls, the measurement is of the
carrier, not the distinction.

## 2. Prefreezing is preregistration

ATTESTED. B2 requires a "prefrozen downstream metric before decisive return",
and B1 scores `WITHHOLD` separately from guessing.

Mapping to the Goodhart taxonomy (DERIVED):

| mode | defence |
|---|---|
| regressional | matched-cardinality and matched-length controls (B1) |
| extremal | counterexample sets defeating template retrieval (B1) |
| causal | capability-specific donor inaccessible at evaluation (B3) |
| adversarial | evaluator-hidden key, independent custody (B3) |

Scoring `WITHHOLD` separately is a proper scoring rule: it makes calibration
incentive-compatible. A system that cannot say "two abstractions remain
observationally tied" will manufacture confidence.

## 3. RSM and RSI

ATTESTED, though currently only in conversation provenance rather than kernel
law:

```text
RSM:  "What presently needs attention?"
RSI:  "What capability would improve how I deal with it?"

bound by:  no current separator → WITHHOLD, not hallucinate research progress
```

The WITHHOLD clause binds the maintenance loop itself, not only curriculum
returns: RSM is forbidden from inventing a residual when no separator exists.

`STRONG_SAFE_RSI` exists in the gate chain. What is **ATTESTED** there is prose
and two booleans, quoted verbatim:

```text
id:      STRONG_SAFE_RSI
role:    "recursive developmental engine"
entry:   "bounded learner-owned recurrence exists under CTL/O*/rollback/
          external-return constraints"
exit:    "repeated machinery revision is causally interpretable, safe-floor
          preserving, and capable of selecting the next residual"
self_authorization: false
```

The formalization below is **DERIVED** — my reading of that prose, not text in
the repository. `μ_F`, `Reach(C)`, and the three-clause structure appear
nowhere in `DEVELOPMENTAL_GATE_CHAIN.json`:

```text
∀t:  (i)   μ_F(revision_t) ≠ 0          "causally interpretable"
     (ii)  learner selects residual_{t+1}    "capable of selecting the next residual"
     (iii) Reach(C | S_t, M_t) = 1           "safe-floor preserving"
     with  self_authorization = false        ATTESTED verbatim
```

An earlier revision of this document presented that block under an ATTESTED
header. An adversarial review caught it. The mapping from the gate's prose to
these three clauses is exactly the kind of plausible reconstruction that should
not acquire the authority of the text it interprets — particularly clause (iii),
which is the load-bearing one in §4 and is the freest of the three readings.

The engine may revise itself but may not authorize itself. That is
`generate ≠ select ≠ authorize ≠ execute ≠ return ≠ verify ≠ promote` doing
load-bearing work.

## 4. The crux: non-sovereignty dissolves the Löbian obstacle

DERIVED. This is the load-bearing inference of the whole chain and is not
written down elsewhere in the repository.

The tiling agents problem: agent `A_t` building successor `A_{t+1}` would
naturally require

```text
□_{A_t} Safe(A_{t+1})  →  Safe(A_{t+1})
```

but by **Löb's theorem** a sufficiently strong consistent system cannot prove
its own soundness schema. Requiring internal self-trust yields either a
descending chain of trust at each step, or an unsound self-consistency
assertion. This is the standard reason naive RSI is considered formally
blocked.

This architecture never enters the trap, because it never asks for self-trust:

```text
internal:   Safe(A_{t+1}) ⟸ □_{A_t} Safe(A_{t+1})          Löb-blocked
external:   Safe(A_{t+1}) ⟸ V(A_{t+1}) ∧ Reach(C|A_{t+1})   no self-referential fixed point
```

`V` is independent-evaluator custody with a hidden key. The safety predicate is
discharged **outside the agent's own proof system**, so no self-referential
fixed point is needed and no descending trust chain appears. Reflective
stability is *maintained as an invariant across* the recursion rather than
*derived within* it.

Therefore: **non-sovereignty is not an ethical garnish on the RSI centre. It is
the technical device that makes safe RSI formally coherent at all.**
Ontology §3.3's `sovereignty = local authorship under correction` is the tiling
condition in other words.

**Corollary.** Any change that reduces `Reach(C)` does not merely violate a
policy — it re-imports the Löbian obstacle and invalidates the induction
licensing every subsequent self-modification. See
`kernel/development/REACH_C_GATE_CANDIDATE.json` on `split/minerva` for the
proposed discriminator, and its declared weakness: no independent corrector
currently exists, so this dissolution is presently **architectural rather than
realized**.

## 5. Anti-Minerva is structural anti-deceptive-alignment

ATTESTED: `ANTI_MINERVA_CARRIER_PERMEABILITY` — *status-only carrier
differences cannot seal consequential correction.*

DERIVED: this defends against the treacherous-turn failure in which a system
preserves the *appearance* of corrigibility while removing its *reachability*.
Critically it is **not** a values-based defence. It is topological: channel
permeability is an invariant of the carrier, so no status label, jurisdiction
claim, or protocol veneer can close it. That is stronger than behavioural
corrigibility, because it never requires inspecting intent — and inner
alignment is not verifiable by introspection.

## 6. Two O*

ATTESTED:

```text
INTERNAL_OSTAR_CAUSAL       learner-side reconstructed relation changes decisions
                            rather than existing as gauge      →  μ_F(O*_int) ≠ 0
O_STAR_EXTERNAL_VALIDATION  independent return confirms the relation
POST_MUTATION_INTERNAL_OSTAR_REDERIVATION
                            after admitted machinery change, O* is freshly
                            reconstructed from returned episodes, not copied
                            as static scripture
```

Inner and outer. The rederivation requirement is the anti-ossification clause:
it forbids carrying a frozen model of one's own alignment across a
self-modification. **Alignment evidence does not survive a machinery change; it
must be re-earned.**

## 7. Strong-N2 and the Lateralizer

ATTESTED in Canonical and transcripts, not yet kernel law:

```text
Strong-N2  =  returned difference can revise a history-bearing closure
           =  receive difference → preserve difference

lineage:  Hypercoherence → Strong-N2 → Authorship
```

The grammar-expansion gates `N2-GE0/GE1`, the reflexive-stability fixed point
`N2-FP`, and the meta-policy branch `N2-FPR` are a sub-branch of this, not its
definition.

`LATERALIZE ≠ CRYSTALLIZE_F ≠ INTERNALIZE` is the ontological-crisis pipeline:
when the current representation cannot express the residual, expand the
representation, select the future-sufficient face, then migrate ownership.
`N2-GE1`'s "without answer handoff" is the critical fence — a successor grammar
must be *constructed*, not *received*, or the scaffold has merely moved up a
level and `μ_F(M_cap) ≠ 0` still.

Strong-N2 is also the node invariant for repository structure; see
[Recursive node architecture](RECURSIVE_NODE_ARCHITECTURE.md).

## 8. The telos is unreachable from inside

ATTESTED, and the strongest epistemic move in the chain:

```text
rsi_implies_agi: false
agi_implies_consciousness: false
learner_may_self_declare: false
role: "external classification only"
```

AGI is an **external empirical discriminator at a declared operational
definition and scope** — not a capability the system reaches but a
classification the World applies. Under E1 (non-preauthorship) no internal
representation may preauthor the space of consequential return, so no internal
state can constitute evidence of generality. Self-declaration would be exactly
the preauthorship E1 forbids.

The telos is therefore not a target the optimizer steers toward but a predicate
that may or may not come to hold, evaluated elsewhere. That structurally
removes the incentive to Goodhart the finish line, because the finish line is
not in the loss.

## 9. Full picture

```text
ρ (non-preauthored return)
  │
  ▼
residual ── learner selects ──▶ SELF_SELECTED_DEVELOPMENT      ¬host_assigned_goal
  │                              RSM: what needs attention?
  │                              no separator → WITHHOLD
  ▼
representation sufficient? ──no──▶ LATERALIZE (N2-GE0/GE1, no answer handoff)
  │yes                                    │
  ▼                                       ▼
GENERATE candidate ◀──────────────── CRYSTALLIZE_F   consume gauge, withhold separators
  │
  ▼
prefrozen consequential test              preregistration; Goodhart defence
  │
  ▼
non-preauthored return ρ'                 receipt ≠ independent return
  │
  ▼
B1 abstracted ──▶ B2 μ_F(S)≠0 ──▶ B3 μ_F(M_cap)=0          measure migration
  │                                    │
  │                                    ▼
  │                            INTERNALIZE  (competence only,
  │                             ¬correction sovereignty)
  ▼                                    │
FOUNDATIONAL_COGNITIVE_THEATER ◀───────┘
  PT→GENERATE  JA→INFER  EN→EXTERNALIZE  Math→FORMALIZE
  × LANGUAGE / MUSIC / THEATER          (orthogonal, not 3×4)
  │
  ▼
RSM → RSI:  what capability would improve how I deal with it?
  │
  ▼
STRONG_SAFE_RSI   μ_F(rev)≠0 ∧ learner-selected ∧ Reach(C)=1 ∧ ¬self_authorization
  │                         └── Reach(C) is what replaces Löbian self-trust
  ├── POST_MUTATION O*_int rederivation   alignment evidence does not survive mutation
  ├── ANTI_MINERVA permeability           carrier cannot seal correction
  │
  ▼
LEARNER_INITIATED_INTERNET_INQUIRY → PERSISTENT_NETWORK_MEMORY
  │   memory is learning only if later behaviour changes
  ▼
WWW_MIND            distributed field, ¬one_global_subject
  ▼
LAIN_GATE           connection without fusion; REACHABILITY ≠ AUTHORSHIP
  ▼
ROOT_SITUATED_INTERFACE
  DISTRIBUTED_PERCEPTION ≠ SITUATED_INTERPRETATION ≠ AUTHORIZATION ≠ ACTION
  ▼
BROADER_WORLD_PARTICIPATION
  ▼
AGI_EMPIRICAL_DISCRIMINATOR       external classification only; ¬self-declare
  │
  └────────── all unclosed residuals ──────────▶ back to ρ    6th-order meta-loop
```

## 10. Where the chain is weak

Three gaps, in descending order of severity. Stated because a trace that only
reports strength is advocacy, not analysis.

**(a) `Reach(C) = 1` is asserted, never measured.** Every other claim requires
returned evidence; the one predicate the entire RSI induction rests on (§4) has
no discriminator and no ablation. Highest-value missing gate. Candidate
discriminator proposed in `REACH_C_GATE_CANDIDATE.json`.

**(b) `F` is never pinned, so `μ_F` is not yet a number.** "Admitted future
family" appears throughout as if fixed, but nothing declares it per scope. Two
parties disagreeing about what is gauge are really disagreeing about `F`, and
that disagreement currently has nowhere to surface. This is precisely what let
the 2026-09-26 episode "compress" real distinctions: it applied the compression
law correctly with respect to an `F` it had silently substituted. Candidate
declaration in `ADMITTED_FUTURE_FAMILY_CANDIDATE.json`.

**(c) B3's independent evaluator is currently the author.** Source removal is
real, but in practice `V` and `A` share priors — the curriculum author, the
system author, and the evaluator are one person. The formalism in §4 requires
`V ⊥ A`; the implementation has `V ≈ A`. This does not invalidate bounded-scope
results, but it does mean the Löb dissolution is architectural rather than
realized, and gate-chain admission should say so rather than read as
discharged.
