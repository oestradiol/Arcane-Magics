# EDU15R1 — Self-Preregistration Verifier Repair

**Date:** 2026-09-24
**Class:** verification/reconciliation repair only; no new curriculum attempt and no new evaluator return
**Parent:** EDU15 verifier-defect branch

EDU15's proposal and independent evaluator return are immutable inputs. The only repair is replacing the faulty bare-word leakage check with a structural check: the proposal may contain a commitment hash and independently reconstructed gate concepts, but must not contain the hidden evaluator object, evaluator coverage fields, or copied rubric arrays. No new RETURN, changed threshold, or rerun is permitted.
