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

## Bounded authenticated deployment adapter

`kernel/runtime/auth.py` now provides a stronger optional authority-ingress path using HMAC-SHA256 under explicitly configured symmetric trust roots.

It authenticates:
- issuer + key identity within the configured trust store;
- payload digest and type;
- per-root authority-type capability;
- revocation before signing/verification;
- fail-closed registration of jurisdiction and legitimacy receipts;
- preservation of VMK2's existing immutable receipt-ID binding after authentication.

Adversarial tests cover payload tampering, forged issuer/key, signature tampering, revoked roots, capability/type violations, and conflicting authenticated receipt registration.

This earns only:

```text
registered authority
+ configured shared-secret trust root
+ successful cryptographic verification
-> authenticated authority under that bounded deployment trust domain
```

It does **not** establish PKI, independent identity attestation, or cross-organization trust.

## What remains outside the current authenticated boundary

- public-key issuer identity / PKI or equivalent independently distributable trust;
- chained/delegated capability verification beyond a directly configured symmetric root;
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


## Correction permeability is not network permeability

The project-wide phrase **corrigibly permeable boundary** is broader than an authenticated network ingress path.

```text
epistemic/correction permeability
!=
network openness
!=
authorization
!=
trust
```

At kernel scope, authenticated ingress is one implementation condition that may allow a returned consequence to cross a boundary. It never follows that every reachable or semantically relevant return is authorized to mutate state.

The safe composition is:

```text
returned difference
+ source/provenance
+ authentication where required
+ jurisdiction/capability
+ future-separating consequence
-> candidate lawful reopening
```

A security boundary may legitimately reject a carrier even when the underlying distinction remains epistemically relevant; the research obligation then stays OPEN/WITHHOLD rather than being reclassified as false or gauge.


## Symbolic salience is not source independence

A vivid symbol, repeated narrative, synchronistic-feeling coincidence, or high-consensus message can be epistemically important without being independently sourced.

```text
salience != independence != authorization != truth
```

Trust evaluation must therefore preserve provenance/source ancestry separately from phenomenological or social intensity. Recursive citation, algorithmic amplification, or repeated restatement does not create new external evidence.

A symbolic object may still be admitted as a local intervention or research prompt. What it cannot do is cross the trust boundary as `Return` or `Verify` merely because it is meaningful, resonant, or widely repeated.
