#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, fnmatch
ROOT=Path(__file__).resolve().parents[1]
SKIP_PATTERNS=[
    '*.aux','*.log','*.out','*.toc','*.fls','*.fdb_latexmk','*.bcf','*.run.xml','main.pdf',
    '*-SAVE-ERROR','*.synctex.gz','__pycache__/*','*.pyc','.pytest_cache/*','.git/*',
    'RELEASE_MANIFEST.json','SHA256SUMS'
]
def skip(rel:Path):
    s=rel.as_posix()
    return any(fnmatch.fnmatch(rel.name,p) or fnmatch.fnmatch(s,p) for p in SKIP_PATTERNS)
files={}
for p in sorted(ROOT.rglob('*')):
    if p.is_file():
        rel=p.relative_to(ROOT)
        if skip(rel): continue
        h=hashlib.sha256(p.read_bytes()).hexdigest()
        files[rel.as_posix()]={'sha256':h,'bytes':p.stat().st_size}
(ROOT/'RELEASE_MANIFEST.json').write_text(json.dumps({'release':'2026-09-24-bundle-v1','files':files},indent=2,sort_keys=True)+'\n')
(ROOT/'SHA256SUMS').write_text(''.join(f"{m['sha256']}  {path}\n" for path,m in files.items()))
print('manifested',len(files),'public files')
