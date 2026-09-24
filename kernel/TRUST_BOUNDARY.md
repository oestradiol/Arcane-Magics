# VMK2 Trust Boundary

VMK2 is currently a **reference governance/custody kernel**. It enforces relations among registered objects. It does not yet authenticate the external principals who supplied those objects.

## Current distinction

```text
registered jurisdiction/legitimacy receipt
!= externally authenticated authority

registered evidence digest + source/assessor identifiers
!= independently authenticated evidence custody
```

The reference kernel can correctly reject a transition that violates a registered jurisdiction while still relying on the caller/runtime to decide which jurisdiction receipts are trustworthy enough to register.

## What VMK2 currently enforces

- immutable identifier binding within registries;
- actor/target/mode jurisdiction checks;
- validity windows;
- withdrawn/failed legitimacy rejection;
- turn ownership and contamination checks;
- evidence/return source binding;
- action-return execution-receipt requirement;
- replay/nonce rejection;
- payload-to-return evidence binding;
- WORD vs PORTAL separation;
- dependency closure;
- projection reopening only under strict future-family expansion with bound separator;
- state-root consistency at transition time;
- defensive isolation of backend input from prior state values.

## What remains outside the current authenticated boundary

- cryptographic issuer identity;
- trust-root/capability-chain verification;
- source/assessor signature verification;
- independent timestamping;
- external immutable storage/custody proof;
- revocation distribution across independent processes;
- cross-machine principal authentication.

Those belong to issue #30 and any future deployment adapter.

## Reference VMK2 canonicalization

The live reference VMK2 canonicalizer now:
- sorts normalized unordered containers before hashing;
- rejects NaN and positive/negative infinity;
- requires string mapping keys for cross-language authority-bearing JSON;
- carries an exact byte/digest fixture in the test suite.

These changes are required to leave the admitted IG10 JSON-state roots unchanged; `tests/test_current_kernel.py` remains the regression oracle. This does not rewrite historical non-JSON objects or migrate old custody roots.

## Historical hash contract

The exact IG10 checkpoint depends on the historical VMK2 serialization/hash contract. New repository objects use `kernel/runtime/canonical.py`, whose unordered-container canonicalization is stricter.

Do not silently rewrite historical VMK2 hashing and then call the resulting roots IG10.

A future migration may:
1. retain historical hash verification for admitted checkpoints;
2. create a new versioned canonical contract;
3. prove/record migration correspondence;
4. mint new roots under the new contract without rewriting old custody.

## Claim fence

A hardened internal custody kernel is not automatically an externally authenticated trust system. External authentication must be represented and tested explicitly.
