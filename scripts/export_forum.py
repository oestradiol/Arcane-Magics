#!/usr/bin/env python3
from pathlib import Path
import subprocess, re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'preprints'/'lesswrong'/'generated'; OUT.mkdir(parents=True,exist_ok=True)
BOX={
 'claimbox':'Claim boundary', 'readerbox':'Reader reconstruction',
 'devilbox':"Devil's Audit", 'mythosbox':'Mythos register',
 'translationbox':'Vocabulary bridge', 'center':'',
 'definition':'Definition', 'proposition':'Proposition', 'theorem':'Theorem', 'corollary':'Corollary',
 'proof':'Proof', 'example':'Example', 'remark':'Remark', 'hypothesis':'Hypothesis',
 'criterion':'Criterion', 'readercheck':'Reader reconstruction',
 'statusnote':'Status', 'devilaudit':"Devil's Audit", 'mythosregister':'Mythos register',
 'cruxbox':'Crux / falsifier', 'tcolorbox':'Claim/register note', 'thebibliography':''
}
for name in ['01_OFE','02_ECLIPSIS','03_ARCANE_MAGICS','04_VENUS']:
    src=ROOT/'monographs'/name/'main.tex'; dst=OUT/f'{name.lower()}.md'
    try:
        subprocess.run(['pandoc','-f','latex','-t','gfm','--wrap=none',str(src),'-o',str(dst)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        body=dst.read_text(errors='replace')
        for cls,title in BOX.items():
            body=re.sub(rf'<div class="{re.escape(cls)}">\s*', (f'**{title}.**\n\n' if title else ''), body)
        body=body.replace('</div>','')
        # Keep the forum copy conservative: no project CSS dependency, no raw centering wrappers.
        body=re.sub(r'\n{3,}','\n\n',body).strip()+'\n'
        pre='**Epistemic status:** Discussion draft. Claim strength and register follow the manuscript; project vocabulary may be tabooed and replaced by the ordinary referent without changing the claim. Check equations, citations, and footnotes against the PDF before posting.\n\n'
        dst.write_text(pre+body)
    except Exception as e:
        dst.write_text(f'# Export failed\n\n{e}\n')
print('Generated forum drafts. Review before posting; editor conversion can be lossy.')
