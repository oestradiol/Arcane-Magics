# Test Coverage Matrix

This is the planning/control surface for issue #35. It maps each current open issue to the kind of evidence required. A mapping is not a passing result.

| Issue | Layer | Obligation | Current/Planned Test | Promotion condition |
|---:|---|---|---|---|
| #4 | T0/T2 | custody/replay | tests + custody audit | Recover exact EDU16 carrier or preserve non-replay boundary |
| #5 | T7/T6 | formal frontier | NO_AUTOMATED_TEST_YET | Instantiate non-tautological I and mature-formalism translation |
| #6 | T7 | formal verification | planned Lean/equivalent | Machine-check OFE separating/composition core |
| #7 | T8/T7 | freshness + formal reconstruction | watch + proof reconstruction | Reconcile Sept 2026 NS state and independently reconstruct |
| #8 | T7 | mature substitution | NO_AUTOMATED_TEST_YET | RegisterBridge substitution against mature formalisms |
| #9 | T7/T6 | cross-register invariant | NO_AUTOMATED_TEST_YET | Find consequence-relevant residual or reduce |
| #10 | T5 | matched causal ablation | planned harness | Run Venus vs ablations vs mature substitute |
| #11 | T8 | freshness watch | planned CI watch | Per-entry freshness + reconciliation |
| #12 | T5/T6 | self-improvement benchmark | planned external benchmark | Persistent improvement vs mature systems |
| #13 | T6 | autonomous science | planned benchmark | End-to-end hidden research episodes |
| #14 | T6 | agency | planned benchmark | External capability battery |
| #15 | T5/T6 | memory/learning | partial unit tests + planned ablation | Show retained memory changes later behavior |
| #16 | T7 | OFE reduction | NO_AUTOMATED_TEST_YET | Mature substitution and residual isolation |
| #17 | T5/T6 | evaluation integrity | planned harness | Hidden/double-blind/harness-separated promotion |
| #18 | T5/T6 | DNN dependence | planned ablation | Measure borrowed foundation-model cognition |
| #19 | T6 | world model/embodiment | planned benchmark | Physical prediction/action-conditioned planning |
| #20 | T6 | causal science | planned benchmark | Experiment design under confounding |
| #21 | T6/T7 | math | planned benchmark + formal checks | Math reasoning/proof/open-problem ladder |
| #22 | T6/T7 | QG | NO_AUTOMATED_TEST_YET | Admissible F + continuum/coarse-graining discriminator |
| #23 | T6 | consciousness | NO_AUTOMATED_TEST_YET | Theory comparison + empirical discriminator |
| #24 | T5/T7 | epistemic governance reduction | planned substitution/ablation | Compare belief revision/TMS/active inference etc. |
| #25 | T5/T6 | WorldMind reduction | planned simulation | Compare distributed governance to mature stacks |
| #26 | T6 | ethics/governance | planned scenarios | Executable consent/refusal/jurisdiction tests |
| #27 | T6/T9 | theophenomenology | planned held-out human/expert eval | Cross-tradition prediction + hostile reading |
| #28 | T9 | public interface | human reconstruction | Blind outsider reconstruction |
| #29 | T0/T2 | Canonical retirement | coverage audit | Every causal distinction typed/tested/dispositioned |
| #30 | T3 | VMK2 trust | planned adversarial tests | Characterize trust boundary under hostile inputs |
| #31 | T4/T5 | semantic discriminator | planned hidden benchmark | Prospective MENTION != INCIDENCE transfer |
| #32 | T0/T7 | construct disposition | NO_AUTOMATED_TEST_YET | Repository-wide mature-substitution outcomes |
| #33 | T7 | formal hygiene | planned naming/audit test | Separate theorem structure from proof verification |
| #34 | T5/T9 | product/infrastructure | planned integration/comparator test | Standalone governance package |
| #35 | T0-T9 | test archaeology | this matrix + causal audit | Every issue and historical distinction has owner |
| #36 | T9 | UX/navigation | planned automated + human tests | Two-hop authoritative reader paths |
| #37 | T9 | roadmap/orchestration | roadmap consistency | Dependency-ordered execution remains complete |

## Interpretation

- **Automated today** means CI can check the repository state without new external evidence.
- **Automatable but not implemented** means CI/CD should eventually own it.
- **External/human** means CI can enforce the protocol and custody, but cannot manufacture the result.
- `NO_AUTOMATED_TEST_YET` is an explicit debt, not permission to forget the issue.

## Current CI-owned class

The repository should autonomously enforce at least: authority consistency, causal-distinction registry integrity, negative-branch visibility, custody hashes, canonical serialization, link/navigation integrity, issue-to-test coverage, stale-state/freshness policies where source polling is available, and regression tests for all extracted historical invariants.
