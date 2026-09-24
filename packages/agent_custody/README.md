# Agent Custody

`packages/agent_custody/` is an ordinary-language facade over the repository's existing governance/custody kernel. It is the first bounded extraction for issue #34.

It deliberately avoids requiring the wider Venus ontology.

## Current API surface

- record evidence with source/assessor/provenance metadata;
- bind an external return to registered evidence;
- register **internal** authorization and transition policy;
- bind a claim to returned, selected, and required evidence;
- fail closed when required evidence exists somewhere in the return bundle but was not selected for the claim.

Example:

```python
from packages.agent_custody import AgentCustody

custody = AgentCustody()
e = custody.record_evidence(source_id='world', assessor_id='reviewer', payload={'x': 1}, epoch=1)
claim = custody.bind_claim(
    claim_id='c1',
    returned_evidence_ids=[e.evidence_id],
    selected_evidence_ids=[],
    required_evidence_ids=[e.evidence_id],
)
assert not claim.supported
```

## Trust boundary

Current authority registration is **internally registered**, not cryptographically authenticated. The facade exposes that fact as `authority_level == INTERNALLY_REGISTERED` and does not relabel it.

```text
internal receipt registry
!= authenticated issuer
!= trust root
!= external immutable custody proof
```

## Product test

The next question is whether this API provides useful audit/reliability consequence for an external agent integration relative to ordinary structured logs/event sourcing/provenance tooling. If mature infrastructure preserves every declared consequence, the project-specific product claim should reduce accordingly.

## Claim fence

This package boundary is an engineering extraction. It is not evidence of AGI, autonomous science, or a secure authenticated trust boundary.
