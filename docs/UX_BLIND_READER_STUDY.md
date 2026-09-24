# Blind-reader UX study

Issue #36 treats navigation as research infrastructure because a reader who cannot find current authority can accidentally reconstruct a stale project.

The machine-readable protocol is [`UX_BLIND_READER_PROTOCOL.json`](UX_BLIND_READER_PROTOCOL.json).

## Procedure

Give an unfamiliar reader only the repository README. Do not explain project vocabulary or point them toward specific files.

Ask the ten frozen reconstruction tasks in the protocol. Record:
- correctness;
- completion time;
- intentional navigation hops;
- whether a stale/wrong authority surface was used;
- whether the answer depended on unexplained private vocabulary;
- reader confidence.

The automated navigation contract already checks that key destinations are reachable within two Markdown hops. This study tests the harder question: whether humans actually reconstruct the intended distinctions.

## Failure handling

A reader failure is evidence about information architecture, not evidence that the underlying research claim is false.

Preserve each failed route and repair only the navigation/content surface responsible for the confusion. Re-run with new readers rather than coaching the exposed reader into success.

## Claim fence

Better UX does not promote scientific claims. It reduces accidental authority confusion and makes real evidence easier to inspect.
