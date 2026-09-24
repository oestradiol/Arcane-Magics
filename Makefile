.PHONY: test lint proof experiment-contracts proof-containers formal-check custody edu16-custody causal-coverage navigation sota-freshness experiment-template hidden-benchmarks hidden-ready construct-dispositions audit kernel-doc-check papers arxiv texbundle forum manifest bundle release clean

test:
	python3 -m unittest discover -s tests -p 'test_*.py'

lint:
	python3 scripts/lint_github_markdown.py

proof-containers:
	python3 scripts/audit_proof_containers.py

proof: proof-containers
	@echo "NOTE: proof means proof-container/theorem-structure audit only; use formal-check for machine verification."

formal-check:
	cd formal/lean && lake build

custody:
	python3 scripts/audit_custody.py

experiment-contracts:
	python3 scripts/validate_experiment_manifest.py evaluation/MATCHED_EXPERIMENT_TEMPLATE.json
	python3 scripts/validate_experiment_manifest.py evaluation/EVIDENCE_GOVERNANCE_PREFREEZE.json
	python3 scripts/audit_experiment_readiness.py evaluation/EVIDENCE_GOVERNANCE_PREFREEZE.json

edu16-custody:
	python3 scripts/audit_edu16_custody.py

causal-coverage:
	python3 scripts/audit_causal_distinctions.py

navigation:
	python3 scripts/audit_navigation_contract.py

sota-freshness:
	python3 scripts/audit_sota_freshness.py

experiment-template:
	python3 scripts/validate_experiment_manifest.py evaluation/MATCHED_EXPERIMENT_TEMPLATE.json

hidden-benchmarks:
	python3 scripts/audit_hidden_benchmarks.py

hidden-ready:
	python3 scripts/audit_hidden_run_readiness.py

construct-dispositions:
	python3 scripts/audit_construct_dispositions.py

audit: test lint proof-containers custody edu16-custody causal-coverage navigation sota-freshness experiment-contracts hidden-benchmarks hidden-ready construct-dispositions
	SOURCE_TREE_ONLY=1 python3 scripts/audit_release.py

kernel-doc-check:
	mkdir -p build/kernel
	pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build/kernel kernel/VENUS_INCIDENCE_LAW.tex >/dev/null

papers:
	python3 scripts/build_all.py

arxiv:
	python3 scripts/package_arxiv.py

texbundle:
	python3 scripts/bundle_tex.py

forum:
	python3 scripts/export_forum.py
	python3 scripts/lint_github_markdown.py

manifest:
	python3 scripts/make_manifest.py

bundle:
	python3 scripts/package_repository.py

release: audit papers arxiv texbundle forum
	python3 scripts/audit_release.py
	$(MAKE) clean
	$(MAKE) manifest
	$(MAKE) bundle

clean:
	find monographs -type f \( -name '*.aux' -o -name '*.log' -o -name '*.out' -o -name '*.toc' -o -name '*.fdb_latexmk' -o -name '*.fls' -o -name 'main.pdf' -o -name '*.bcf' -o -name '*.run.xml' -o -name '*-SAVE-ERROR' \) -delete
