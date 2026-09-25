.PHONY: test boundary paper audit clean

test:
	python3 -m unittest discover -s tests -p 'test_*.py'

boundary:
	test -f docs/SELF_WORLD_MODEL.md
	test -f provenance/historical/BRANCH_MEMORY.md
	grep -q 'prediction != return' README.md
	grep -q 'independent return' docs/SELF_WORLD_MODEL.md

paper:
	cd monographs/05_VENUS && pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null && pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null

audit: test boundary

clean:
	find monographs/05_VENUS -type f \( -name '*.aux' -o -name '*.log' -o -name '*.out' -o -name '*.toc' \) -delete
