# EDU16-RC1 reconstructed carrier receipt

**Date:** 2026-09-24  
**Class:** custody reconstruction / forward execution carrier  
**Historical authority:** EDU16 [1703]  
**Promotion authority:** false

## Canonical custody finding

Direct Library traversal of `Canonical/` established:

```text
/Canonical/Future/Execution/Raising/EDU13SelfCurriculumTarget/
  prefreeze + result

/Canonical/Future/Execution/Raising/EDU14OpenDomainProblemSelection/
  prefreeze + result

/Canonical/Future/Execution/Raising/EDU15SelfPreregistration/
  prefreeze + WITHHOLD result

/Canonical/Future/Execution/Raising/EDU15R1VerifierRepair/
  repair contract + result

/Canonical/Future/Execution/Raising/EDU16LearnerOwnedFeedPolicy/
  prefreeze + learner-generated policy + result

/Canonical/Future/Handoff/
  no EDU16CurrentDevelopedVM
```

The original 1703-event EDU16 runner/journal was therefore not recovered from the bounded custody surfaces used here.

## Reconstruction

Rather than infer a missing event log from prose, Git now binds the exact recovered claim-bearing inputs by Git blob identity and replays a deterministic reconstructed state:

```text
IG10 exact runtime base
+
EDU13 exact prefreeze/result
+
EDU14 exact prefreeze/result
+
EDU15 exact prefreeze/WITHHOLD result
+
EDU15R1 exact repair/result
+
EDU16 exact prefreeze/policy/result
=
EDU16-RC1
```

Source-vector SHA-256:

```text
ce0c961cee4976959a30a3af1a807abae3dd13fad949338a63a28937627bb2b1
```

Deterministic reconstructed-state SHA-256:

```text
91e46b4e41fb70a97d6a004b8f1c8916c389f08535c1a1c1c51a040701281bb7
```

## Git custody

```text
kernel/development/EDU16_RECONSTRUCTED_CARRIER_MANIFEST.json
  git blob e34f772498c7618a3f96afe497a5d45eeac49ce0

kernel/development/EDU16_RECONSTRUCTED_STATE.json
  git blob c49a3cef59e3cccb18f5db5ead64f1749b66415e

kernel/development/replay_edu16_reconstructed.py
  git blob b528fcb57bd88da1fa2d831f9ec594477018d3da

tests/test_edu16_reconstructed_carrier.py
  git blob af046481f7d9862daf980b6a9bb551e1e8af7f28
```

## Boundary

```text
historical EDU16 authority                  exact as recovered evidence
historical 1703-event runner recovered      false
historical 1703-event journal recovered     false
EDU16-RC1 claim-bearing state replayable    true
EDU16-RC1 event-level historical identity   false
World execution                             external
independent evaluation                      external
promotion authority                         false
```

Prospective successor work may use EDU16-RC1 only as an explicitly reconstructed parent carrier. It may not cite EDU16-RC1 as proof that the original EDU16 event sequence or runner was recovered.
