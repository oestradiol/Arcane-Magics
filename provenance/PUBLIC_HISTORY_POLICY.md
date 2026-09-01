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

## Current status

On 1 September 2026 the maintained Venus-Minerva public tree was rewritten onto a fresh parentless root after audit of the predecessor DAG. The predecessor history had included a full Research v1.5 working tree that was no longer intended as public release provenance. All maintained non-main rebuild/tmp branches were removed and no tags remain.

The resulting closure is scoped to refs maintained as part of the public release surface. It does not assert physical deletion of GitHub-managed pull-request refs, Actions records, provider caches, or retention objects. Those may retain older object identifiers outside the maintained release graph.

The sanitation gate reopens if:

- a maintained branch or tag reconnects predecessor/backstage history;
- private or identifying provenance is mounted into the public DAG;
- the release tree and intentionally reachable history no longer have the same reviewed boundary;
- a platform-retained object is later promoted back into a maintained public ref.
