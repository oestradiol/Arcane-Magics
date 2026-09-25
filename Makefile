.PHONY: test lint formal-check custody audit kernel-doc-check papers release clean

test:
	python3 -m unittest discover -s tests -p 'test_*.py'

lint:
	python3 scripts/lint_github_markdown.py

formal-check:
	cd formal/lean && lake build

custody:
	python3 scripts/audit_custody.py
	python3 scripts/audit_edu16_custody.py

audit: test lint custody
	python3 scripts/audit_causal_distinctions.py
	python3 scripts/audit_autonomy_safety_matrix.py
	python3 scripts/audit_construct_dispositions.py

kernel-doc-check:
	mkdir -p build/kernel
	pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build/kernel kernel/VENUS_INCIDENCE_LAW.tex >/dev/null

papers:
	TEXINPUTS=shared//: latexmk -pdf -interaction=nonstopmode -halt-on-error -cd monographs/04_VENUS/main.tex

release: audit kernel-doc-check papers

clean:
	rm -rf build
	find monographs -type f \( -name '*.aux' -o -name '*.log' -o -name '*.out' -o -name '*.toc' -o -name '*.fls' -o -name '*.fdb_latexmk' \) -delete
