# Autonomous-run artifacts

`autonomy/` contains returned artifacts from bounded autonomous episodes. It is **evidence custody**, not the live runtime implementation.

```text
kernel/runtime + kernel/development
→ execute bounded episode
→ external/adapter return
→ autonomy/evidence
→ later evaluation / reconstruction
```

Start at [`evidence/README.md`](evidence/README.md).

The presence of an artifact here does not grant promotion authority and does not by itself prove learning. Developmental claims require the corresponding prefrozen discriminator, returned result, and current-state admission.
