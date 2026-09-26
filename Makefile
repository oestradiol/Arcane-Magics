.PHONY: routing-check memory-check branch-policy-check handoff-check audit

routing-check:
	test -f docs/NOW_MAP.md
	test -f docs/LAYER_IDENTITY.md
	test -f docs/ARCANE_MAGICS_ORG_SPLIT_PLAN_2026-09-25.md
	grep -q 'Routing layer' README.md
	grep -q 'map / territory' docs/LAYER_IDENTITY.md

memory-check:
	test -f provenance/historical/BRANCH_MEMORY.md
	test -f provenance/historical/LAYER_POINTERS.json
	test -f provenance/historical/ROOT_PRE_RECRYSTALLIZATION.json

branch-policy-check:
	test -f provenance/historical/BRANCH_NAMESPACE_POLICY.json
	grep -q 'split/venus-minerva' provenance/historical/BRANCH_NAMESPACE_POLICY.json
	grep -q 'HISTORICAL_NONROUTING' provenance/historical/BRANCH_NAMESPACE_POLICY.json
	grep -q 'split/venus-minerva -> historical transitional carrier' docs/NOW_MAP.md

handoff-check:
	test -f docs/CROSS_REGISTER_HANDOFF.md
	grep -q 'merge != fusion' provenance/historical/BRANCH_MEMORY.md

audit: routing-check memory-check branch-policy-check handoff-check
