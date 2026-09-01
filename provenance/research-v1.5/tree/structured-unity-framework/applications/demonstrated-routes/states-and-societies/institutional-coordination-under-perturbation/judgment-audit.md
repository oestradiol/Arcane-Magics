# Judgment Audit: New Zealand Route

**Status:** Reference document for coding transparency  
**Route:** New Zealand pandemic coordination (38-event ledger)  
**Date:** 2026-04-17  
**Purpose:** Explicit documentation of judgment-dependent decisions, alternative codings, and impact on locked payoff

---

## 1. Known judgment-dependent decisions

### 1.1 Public-information vs. coordination distinction

**The judgment:** Some events (e.g., Beehive announcements, press conferences) could be read as either pure messaging or active coordination. Current coding treats them as coordination if they include actionable guidance.

**Example edge cases:**

| Event | Coded As | Alternative Reading | Judgment Applied |
|---|---|---|---|
| Alert level announcement with behavioral guidance | `public-information` + `coordination` | Pure communication downstream of decision | Included because it changes what public does, not just what they know |
| Daily press conference with no new guidance | Not coded | Could be coded as maintenance | Excluded: symbolic repetition, no pathway change |
| Official tweet clarifying rules | `public-information` | Could be excluded as minor | Included: official channel changing public knowledge state |

**Sensitivity:** If 5-10 public-information events were excluded as "pure communication," the ratio would shift from 33/38 to approximately 28/38.

### 1.2 Scale tagging (sigma1/2/3)

**The judgment:** Assignment to scale levels involves interpreting level of impact. Current approach uses issuing unit level rather than observed impact.

| Tag | Rule Applied | Alternative Rule | Events Affected |
|---|---|---|---|
| `sigma3` | National-level issuing unit (DPMC, PM, MoH) | Observed national impact | ~22 events |
| `sigma2` | Regional/unit-level issuing (Police, NEMA regional) | Actual regional scope | ~10 events |
| `sigma1` | Local/individual scale | Localized observable effect | ~6 events |

**Impact on payoff:** Scale tagging does not directly affect the locked payoff about public-information centrality.

### 1.3 Confidence notes (high/medium/provisional)

**The judgment:** Confidence assignment varies by source family and perceived reliability.

| Source Family | Typical Confidence | Rationale | Events |
|---|---|---|---|
| D-family A (OAG, Royal Commission) | `high` | Oversight/audit authority; retrospective review | 8 events |
| D-family B (MoH planning) | `high` to `medium` | Official planning documents; some operational uncertainty | 6 events |
| D-family C (Alert transitions) | `high` | Public announcements with clear dates | 9 events |
| D-family D (Emergency management) | `medium` | Operational coordination; some implementation uncertainty | 7 events |
| D-family E (Police/border/public info) | `medium` | Operational releases; less oversight context | 8 events |

**Impact on payoff:** Confidence levels do not affect event inclusion; only source quality annotation.

---

## 2. Alternative reasonable codings

A different researcher, applying the same explicit criteria from `source-corpus-and-coding-protocol.md`, might reasonably:

### 2.1 Exclusion variations

| Scenario | Events Excluded | Impact on 33/38 ratio | Payoff Robust? |
|---|---|---|---|
| Strict coordination-only | 8 public-information events | 25/38 (66%) | Yes - still majority |
| Exclude provisional-confidence | 3-4 events | 30/38 (79%) | Yes |
| Exclude sigma1-only | 6 events | 27/38 (71%) | Yes |

### 2.2 Inclusion variations

| Scenario | Events Added | Impact on ratio | Payoff Robust? |
|---|---|---|---|
| Include routine press briefings | +5 events (all public-info) | 38/43 (88%) | Strengthens |
| Include academic retrospective releases | +2-3 events | 35-36/41 | Marginal change |

### 2.3 Recoding variations

| Change | Events Affected | Impact |
|---|---|---|
| Upgrade `medium` → `high` confidence | 3-5 events | No ratio impact; strengthens reliability claims |
| Split combined events | 2-3 events → 4-6 events | No ratio impact; changes granularity only |
| Merge adjacent events | 4-5 pairs → 4-5 events | No ratio impact; changes granularity only |

---

## 3. Impact on locked payoff

**Locked payoff:** "SUF shows that the New Zealand response should not be read only through command-and-control frameworks... because public-information coordination is structurally central to the working coordination architecture."

### 3.1 Robustness under alternative codings

| Scenario | Public-Info Ratio | Payoff Status |
|---|---|---|
| Current coding | 33/38 (87%) | ✓ Locked |
| Strict exclusion (-10 events) | 23/28 (82%) | ✓ Still robust |
| Moderate exclusion (-5 events) | 28/33 (85%) | ✓ Still robust |
| Inclusion expansion (+5 events) | 38/43 (88%) | ✓ Strengthens |

### 3.2 Breaking scenarios

The payoff would require revision if:

1. **Extreme exclusion:** >15 public-information events excluded, dropping ratio below 60%
2. **Coding fragility:** Review shows the payoff depends on ≤3 specific judgment calls
3. **Alternative reading dominance:** A command-and-control coding yields equivalent or better explanatory structure

---

## 4. Recommended validation procedures

### 4.1 Deferred: Cross-coder reliability study

**Target:** Second researcher codes sample of 10-15 events from source corpus  
**Goal:** Inter-rater reliability κ > 0.75 for event inclusion/exclusion  
**Timeline:** Phase 2 (Australia comparator) or Phase 3  
**Resource estimate:** 4-6 hours coding + 1-2 hours reconciliation

### 4.2 Recommended: Sensitivity documentation for each new case

For Australia comparator and subsequent cases:
- [ ] Document inclusion/exclusion criteria upfront
- [ ] Record edge case judgments in real-time
- [ ] Calculate ratio sensitivity bounds (current ± alternative codings)
- [ ] Report ratio range, not just point estimate

---

## 5. Transparency commitment

This audit document is:
- Updated when coding protocol changes
- Referenced in `CONTRIBUTION_AND_POSITIONING.md`
- Available for reviewer inspection
- Part of the `validator` read-only check surface

**Status:** `reference-document-for-transparency`

---

## Provenance

**Created:** 2026-04-17  
**Trigger:** Devil's Advocate review recommendations  
**Maintainer:** Route lead (SUF active core)  
**Review cycle:** Updated at each phase transition (v1.2 → v1.3 → v1.4)
