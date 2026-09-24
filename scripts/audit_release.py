#!/usr/bin/env python3
from pathlib import Path
import re, sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]
for needed in [
    'README.md','PUBLICATION_CONSTITUTION.md','NxRxI_VOCABULARY_CENTER.md','LICENSE',
    'licenses/CC-BY-NC-SA-4.0.txt','licenses/PolyForm-Noncommercial-1.0.0.txt',
    'review/DEVILS_AUDIT_CHECKLIST.md','review/PROSE_AND_DIDACTICS_AUDIT.md',
    'review/REVIEWER_AND_RESEARCHER_PROTOCOL.md']:
    if not (ROOT/needed).exists(): errors.append('missing '+needed)
for name in ['01_OFE','02_ECLIPSIS','03_ARCANE_MAGICS','04_VENUS']:
    tex=ROOT/'monographs'/name/'main.tex'
    pdf=ROOT/'monographs'/name/(name.lower()+'.pdf')
    if not tex.exists(): errors.append('missing '+str(tex)); continue
    if not pdf.exists(): errors.append('missing built PDF '+str(pdf))
    t=tex.read_text(errors='replace')
    if 'SPDX-License-Identifier: CC-BY-NC-SA-4.0' not in t: errors.append(f'{name}: missing SPDX')
    if name=='04_VENUS' and 'AGI' in t and 'not establish' not in t.lower(): errors.append('Venus: AGI vocabulary without fence')
    if name=='03_ARCANE_MAGICS' and 'License: CC BY 4.0' in t: errors.append('Arcane successor: stale CC BY 4.0 body notice')
# current receipt assertion
r=ROOT/'prototype/current-developmental-receipts/EDU15R1_SELF_PREREGISTRATION_VERIFIER_REPAIR_RESULT.md'
if not r.exists() or '1699' not in r.read_text() or 'PASS_BOUNDED_SELF_PREREGISTRATION_GATE_OWNERSHIP' not in r.read_text():
    errors.append('EDU15R1 current receipt mismatch')
# exact stable-vs-current separation
pr=(ROOT/'prototype/README.md').read_text(errors='replace') if (ROOT/'prototype/README.md').exists() else ''
if 'R00' not in pr or 'R194' not in pr or 'EDU15R1' not in pr: errors.append('prototype README does not distinguish stable executable and current receipt')
# License semantic check
lic=(ROOT/'licenses/README.md').read_text(errors='replace')
if 'PolyForm Noncommercial' not in lic: errors.append('software license map missing')
if 'not OSI Open Source' not in lic: errors.append('software source-available/Open-Source distinction missing')
# arXiv packages
for name in ['01_ofe','02_eclipsis','03_arcane_magics','04_venus']:
    if not (ROOT/'arxiv_packages'/f'{name}_arxiv_source.zip').exists(): errors.append(f'missing arXiv source package {name}')
# Forum exports must be real outputs, not failed placeholders or escaped-newline preambles.
for expected in ['01_ofe.md','02_eclipsis.md','03_arcane_magics.md','04_venus.md']:
    f=ROOT/'preprints/lesswrong/generated'/expected
    if not f.exists(): errors.append('missing forum export '+expected); continue
    txt=f.read_text(errors='replace')
    if txt.startswith('# Export failed'): errors.append(f'forum export failed: {f.name}')
    if '\\n\\n' in txt[:400]: errors.append(f'forum export escaped-newline bug: {f.name}')
    if '<div class=' in txt: errors.append(f'forum export raw project div remains: {f.name}')
if errors:
    print('AUDIT FAIL')
    print('\n'.join('- '+x for x in errors))
    sys.exit(1)
print('AUDIT PASS')
