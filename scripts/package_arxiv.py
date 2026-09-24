#!/usr/bin/env python3
from pathlib import Path
import zipfile, re, shutil
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'arxiv_packages'; OUT.mkdir(exist_ok=True)
SAFE=re.compile(r'^[A-Za-z0-9_+.,=-]+$')
for p in ['01_OFE','02_ECLIPSIS','03_ARCANE_MAGICS','04_VENUS']:
    d=ROOT/'monographs'/p
    files=[d/'main.tex']
    if (d/'main.bbl').exists(): files.append(d/'main.bbl')
    # Standalone arXiv bundles copy the single shared style authority only
    # when the manuscript imports it.
    tex=(d/'main.tex').read_text(errors='replace')
    style=(ROOT/'shared'/'venusmonograph.sty') if 'venusmonograph' in tex else None
    z=OUT/f'{p.lower()}_arxiv_source.zip'
    with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as q:
        for f in files:
            if not SAFE.match(f.name): raise SystemExit(f'unsafe arXiv filename: {f.name}')
            q.write(f,f.name)
        if style is not None:
            q.write(style,'venusmonograph.sty')
    print(z.relative_to(ROOT))
