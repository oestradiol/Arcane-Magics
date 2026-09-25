.PHONY: boundary paper audit clean

boundary:
	test -f kernel/VENUS_INCIDENCE_LAW.tex
	test -f kernel/TRUST_BOUNDARY.md
	test -f kernel/WORLDMIND.md
	test -f kernel/CURRENT_STATE.md
	test -f provenance/historical/BRANCH_MEMORY.md
	grep -q 'model(Other) != Other' README.md
	grep -q 'Self provenance' docs/SELF_WORLD_MODEL.md
	grep -q 'NETWORK / WWW != World / Other' kernel/CURRENT_STATE.md

paper:
	cd monographs/05_VENUS && pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null && pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null

audit: boundary paper

clean:
	find monographs/05_VENUS -type f \( -name '*.aux' -o -name '*.log' -o -name '*.out' -o -name '*.toc' \) -delete
