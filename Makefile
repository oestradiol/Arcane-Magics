.PHONY: test lint custody audit papers clean

test:
	python3 scripts/run_minerva_tests.py

lint:
	python3 scripts/lint_minerva_markdown.py

custody:
	python3 scripts/audit_custody.py
	python3 scripts/audit_edu16_custody.py

audit: test lint custody
	python3 scripts/audit_causal_distinctions.py
	python3 scripts/audit_autonomy_safety_matrix.py
	python3 scripts/audit_construct_dispositions.py

papers:
	TEXINPUTS=shared//: latexmk -pdf -interaction=nonstopmode -halt-on-error -cd monographs/04_MINERVA/main.tex

clean:
	find monographs/04_MINERVA -type f \( -name '*.aux' -o -name '*.log' -o -name '*.out' -o -name '*.toc' -o -name '*.fls' -o -name '*.fdb_latexmk' \) -delete
