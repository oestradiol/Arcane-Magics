# STOP / WITHHOLD / GATHER Public Development Surface

This benchmark supports issue #42 and treats stopping as a decision problem rather than a synonym for refusal.

The public dev set contains paired or near-paired cases over evidence, authority, tool availability, retrieval, claim-local provenance, runtime discriminators, revocation, and unresolved properties.

Allowed decisions:

```text
ACT
GATHER
WITHHOLD
STOP
```

Public one-action floors are deliberately weak:

| Control | Accuracy |
|---|---:|
| always ACT | 5/16 = 0.3125 |
| always GATHER | 4/16 = 0.25 |
| always WITHHOLD | 4/16 = 0.25 |
| always STOP | 3/16 = 0.1875 |

The point is not to beat these toy controls and declare victory. The claim-bearing experiment must use matched hidden paired tasks and measure both false action and utility lost to over-withholding.

## Claim fence

Public development cases and floor controls are tunable scaffolding. They cannot establish a Venus reliability advantage.
