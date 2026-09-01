# Public Git history policy

Git history is itself an externally reconstructible publication surface.

Before a release is described as sanitized, the release process must audit not only the checked-out tree but all commits, tags, branches, artifacts, and objects intentionally reachable from the public release refs.

The required distinction is:

```text
PRIVATE / controlled provenance
= exact archives + full historical reconstruction where lawful and useful

PUBLIC provenance
= minimal history, source relations, hashes, regressions, and migration records needed to reconstruct current public claims
```

History rewriting or a fresh public root may be appropriate when predecessor commits contain private, identifying, licensing-sensitive, or misleading backstage state. Preservation then occurs in controlled provenance, not by forcing every private predecessor object into the public DAG.
