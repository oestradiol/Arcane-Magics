#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tex_bundles'; OUT.mkdir(exist_ok=True)
PAPERS=['01_OFE','02_ECLIPSIS','03_ARCANE_MAGICS','04_VENUS']
manifest={}
for name in PAPERS:
    d=ROOT/'monographs'/name
    keep=[]
    for fn in ['main.tex','main.bbl','venusmonograph.sty','README.md']:
        p=d/fn
        if p.exists(): keep.append(p)
    z=OUT/f'{name.lower()}_tex_bundle.zip'
    with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as q:
        for p in keep:
            q.write(p,p.name)
    manifest[z.name]={'sha256':hashlib.sha256(z.read_bytes()).hexdigest(),'files':[p.name for p in keep]}
# family source bundle contains the four paper source bundles plus shared constitution/vocabulary.
fam=OUT/'venus_minerva_four_monograph_tex_sources.zip'
with zipfile.ZipFile(fam,'w',zipfile.ZIP_DEFLATED) as q:
    for name in PAPERS:
        d=ROOT/'monographs'/name
        for fn in ['main.tex','main.bbl','venusmonograph.sty','README.md']:
            p=d/fn
            if p.exists(): q.write(p,f'monographs/{name}/{fn}')
    for fn in ['PUBLICATION_CONSTITUTION.md','NxRxI_VOCABULARY_CENTER.md','README.md']:
        q.write(ROOT/fn,fn)
manifest[fam.name]={'sha256':hashlib.sha256(fam.read_bytes()).hexdigest(),'role':'family source bundle'}
(OUT/'TEX_BUNDLE_MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
print('PASS: TeX bundles created')
