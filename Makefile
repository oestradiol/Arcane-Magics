.PHONY: papers arxiv texbundle forum audit manifest bundle release clean

papers:
	python3 scripts/build_all.py

arxiv:
	python3 scripts/package_arxiv.py

texbundle:
	python3 scripts/bundle_tex.py

forum:
	python3 scripts/export_forum.py

audit:
	python3 scripts/audit_release.py

manifest:
	python3 scripts/make_manifest.py

bundle:
	python3 scripts/package_repository.py

release: papers arxiv texbundle forum audit clean manifest bundle

clean:
	find monographs -type f \( -name '*.aux' -o -name '*.log' -o -name '*.out' -o -name '*.toc' -o -name '*.fdb_latexmk' -o -name '*.fls' -o -name 'main.pdf' -o -name '*.bcf' -o -name '*.run.xml' -o -name '*-SAVE-ERROR' \) -delete
