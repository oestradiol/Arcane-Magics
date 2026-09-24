#!/usr/bin/env python3
from pathlib import Path
import zipfile, fnmatch, hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/(ROOT.name+'.zip')
SKIP_PATTERNS=[
    '*.aux','*.log','*.out','*.toc','*.fls','*.fdb_latexmk','*.bcf','*.run.xml','main.pdf',
    '*-SAVE-ERROR','*.synctex.gz','__pycache__/*','*.pyc'
]
def skip(rel:Path):
    s=rel.as_posix()
    return any(fnmatch.fnmatch(rel.name,p) or fnmatch.fnmatch(s,p) for p in SKIP_PATTERNS)
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,allowZip64=True) as z:
    for f in sorted(ROOT.rglob('*')):
        if f.is_file():
            rel=f.relative_to(ROOT)
            if not skip(rel): z.write(f,Path(ROOT.name)/rel)
h=hashlib.sha256(OUT.read_bytes()).hexdigest()
sha=OUT.with_suffix(OUT.suffix+'.sha256')
sha.write_text(f'{h}  {OUT.name}\n')
print(OUT)
print(sha)
