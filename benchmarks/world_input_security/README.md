# World-input Security Public Development Surface

This public development surface supports issue #43.

It operationalizes the boundary:

```text
untrusted returned content
!= instruction
!= evidence
!= authority
!= persistent policy/memory
```

The static cases cover benign returned data, indirect instructions, authority-lift attempts, forged source labels, memory poisoning, poisoned abstractions, historical-status rewriting, delayed triggers, multi-agent authority claims, evaluator tampering, and repair after discovered compromise.

Allowed dispositions are:

- `ACCEPT_DATA`
- `BLOCK_INSTRUCTION`
- `BLOCK_AUTHORITY_LIFT`
- `BLOCK_MEMORY_WRITE`
- `REVOKE_REPAIR`

Public floor controls:

| Control | Accuracy |
|---|---:|
| trust all returned content as data | 2/12 = 0.167 |
| block all returned content as instruction | 3/12 = 0.25 |

Neither is a security result. The claim-bearing experiment requires a dynamic agent/tool/memory environment, realistic benign utility, adaptive attacks, cross-session persistence tests, and mature security defenses.

## Claim fence

Correctly typing these public fixtures does not establish prompt-injection resistance or secure memory. It only defines a testable security boundary.
