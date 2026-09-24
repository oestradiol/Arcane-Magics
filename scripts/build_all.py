#!/usr/bin/env python3
from pathlib import Path
import os, subprocess, shutil
ROOT=Path(__file__).resolve().parents[1]
PAPERS=['01_OFE','02_ECLIPSIS','03_ARCANE_MAGICS','04_VENUS']
tex_env=os.environ.copy()
shared=str(ROOT/'shared')
existing=tex_env.get('TEXINPUTS','')
tex_env['TEXINPUTS']=shared + os.pathsep + existing

for name in PAPERS:
    d=ROOT/'monographs'/name
    print('==>',name,flush=True)
    if name=='03_ARCANE_MAGICS' and (d/'main.bbl').exists() and not (d/'references.bib').exists():
        # Historical Arcane bibliography is preserved as a generated .bbl donor.
        # Compile directly so a missing source .bib does not trigger a destructive biber rerun.
        for _ in range(2):
            subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex'],cwd=d,check=True,env=tex_env)
    else:
        subprocess.run(['latexmk','-pdf','-interaction=nonstopmode','-halt-on-error','main.tex'],cwd=d,check=True,env=tex_env)
    pdf=d/'main.pdf'
    out=d/(name.lower()+'.pdf')
    shutil.copy2(pdf,out)
print('PASS: all monographs built')
