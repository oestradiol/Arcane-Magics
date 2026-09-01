# Public export audit

**Scope:** the curated public Venus × Minerva surface. The private unified workspace is outside this audit because it intentionally contains raw provenance material.

The export was checked for internal participant aliases, email addresses, common credential/token formats, private-key headers, symlinks, `.env` payloads, and accidental `.git`/workspace state. Exact Version 0 source and the raw Old Venus archive remain private because historical source may contain unnecessary identifying material.

The knowledge graph was checked for unresolved and ambiguous Obsidian wiki-links. The BibTeX bank was deduplicated by citation key and cross-checked against its function-partitioned export.

These checks reduce accidental disclosure and graph-breakage risk; they do not prove that pattern matching can detect every identifying fact. The governing rule remains privacy minimization: public claims must survive without private trajectory evidence.
