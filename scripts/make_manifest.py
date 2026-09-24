#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, fnmatch, os, subprocess
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
source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
release_id=os.environ.get('GITHUB_REF_NAME') or source_commit
(ROOT/'RELEASE_MANIFEST.json').write_text(
    json.dumps(
        {'schema':'Venus.ReleaseManifest.v3','release':release_id,'source_commit':source_commit,'files':files},
        indent=2,sort_keys=True
    )+'\n'
)
(ROOT/'SHA256SUMS').write_text(''.join(f"{m['sha256']}  {path}\n" for path,m in files.items()))
print('manifested',len(files),'public files')