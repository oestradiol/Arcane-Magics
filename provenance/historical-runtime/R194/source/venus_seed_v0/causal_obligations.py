from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import fnmatch, json, re

_ALLOWED = {
    'EXECUTABLE_LAW','REGRESSION_OR_FALSIFIER','PROVENANCE_OR_EVIDENCE',
    'MATURE_REDUCED_EQUIVALENCE','INVALID_ZERO_AUTHORITY','OPEN_OR_WITHHOLD_GATE',
    'SUPERSEDED_BUT_CAUSAL','EXECUTABLE_COMPOSITION'
}

@dataclass(frozen=True)
class CausalObligation:
    r_id: str
    label: str
    status: str
    burden: str
    source_class: str
    original_disposition: str
    implementation_mode: str

class CausalCoverageError(RuntimeError):
    pass


def _rnum(rid:str)->int|None:
    m=re.fullmatch(r'R(\d+)', rid or '')
    return int(m.group(1)) if m else None


def _mode(text:str, transaction_class:str='', status:str='')->str:
    blob=' '.join([text or '',transaction_class or '',status or '']).upper()
    if 'ZERO SCIENTIFIC AUTHORITY' in blob or 'INVALID' in blob or 'QUARANTIN' in blob:
        return 'INVALID_ZERO_AUTHORITY'
    if 'MATURE-REDUC' in blob or 'REDUCTION' in blob or 'ANTI-PRIVILEGE' in blob:
        return 'MATURE_REDUCED_EQUIVALENCE' if 'NEGATIVE' not in blob else 'REGRESSION_OR_FALSIFIER'
    if 'FALSIFIER' in blob or 'NEGATIVE' in blob or 'FAIL' in blob:
        return 'REGRESSION_OR_FALSIFIER'
    if 'OPEN' in blob or 'WITHHOLD' in blob or 'EXTERNAL' in blob or 'GOVERNANCE LANE' in blob:
        return 'OPEN_OR_WITHHOLD_GATE'
    if 'EXECUTABLE' in blob or 'DEVELOPMENTAL REGRESSION' in blob or 'NATIVE KERNEL' in blob or 'ENGINEERING RESULT' in blob:
        return 'EXECUTABLE_LAW'
    if 'SUPERSEDED' in blob:
        return 'SUPERSEDED_BUT_CAUSAL'
    return 'PROVENANCE_OR_EVIDENCE'


class CausalObligationRegistry:
    """Lossless causal custody compiler for the Python prototype.

    It does not convert every historical noun/file into a runtime natural kind.
    It requires every R1..R194 causal revision to resolve to an executable law/test,
    falsifier, provenance/evidence obligation, mature-reduction equivalence,
    invalid-zero-authority record, or explicit open/withhold gate.
    """
    SCHEMA='Canonical.CausalObligationRegistry.R194.v1'
    def __init__(self, root:Path):
        self.root=Path(root)
        self.custody=self.root/'custody'
        self.entries:dict[str,CausalObligation]={}
        self.genealogy_nodes:list[dict]=[]
        self.repository_rules:list[dict]=[]
        self._load()

    def _j(self,name): return json.loads((self.custody/name).read_text())

    def _add(self, ob:CausalObligation):
        if ob.r_id in self.entries:
            # Exact later ledger/crosswalk overlap must agree on the same causal identity;
            # the earlier R1-R178 crosswalk remains controlling for those IDs.
            return
        if ob.implementation_mode not in _ALLOWED:
            raise CausalCoverageError(f'unsupported implementation mode: {ob}')
        self.entries[ob.r_id]=ob

    def _load(self):
        cross=self._j('VMK1_R1_R178_OBLIGATION_CROSSWALK.json')
        if cross.get('count')!=178 or len(cross.get('entries',[]))!=178:
            raise CausalCoverageError('R1-R178 crosswalk is not exact')
        for e in cross['entries']:
            self._add(CausalObligation(
                e['r_id'],e.get('label',''),e.get('status',''),e.get('surviving_burden',''),
                'R1_R178_CROSSWALK',e.get('vmk1_disposition',''),
                _mode(e.get('vmk1_disposition',''),e.get('transaction_class',''),e.get('status',''))))

        ledger=self._j('POST_R69_R186_RECONCILIATION_LEDGER.json')
        if len(ledger.get('entries',[]))!=117:
            raise CausalCoverageError('R70-R186 ledger record count changed')
        for e in ledger['entries']:
            n=_rnum(e.get('r_id',''))
            if n is None or n<=178: continue
            disposition='; '.join(filter(None,[e.get('native_obligation_test',''),e.get('gate_class',''),e.get('notes','')]))
            self._add(CausalObligation(
                e['r_id'],e.get('label',''),e.get('scientific_effect',''),
                e.get('notes','') or e.get('label',''), 'R70_R186_LEDGER', disposition,
                _mode(disposition,e.get('transaction_class',''),e.get('scientific_effect',''))))

        post=self._j('POST_R186_OBLIGATIONS.json')
        for e in post['entries']:
            disp=e['implementation_disposition']
            if disp.startswith('EXECUTABLE_COMPOSITION'): mode='EXECUTABLE_COMPOSITION'
            elif 'EXECUTABLE' in disp: mode='EXECUTABLE_LAW'
            elif 'INVALID' in disp: mode='INVALID_ZERO_AUTHORITY'
            elif 'FALSIFIER' in disp or 'ANTI_PRIVILEGE' in disp: mode='REGRESSION_OR_FALSIFIER'
            elif 'MATURE' in disp: mode='MATURE_REDUCED_EQUIVALENCE'
            elif 'OPEN' in disp or 'WITHHOLD' in disp: mode='OPEN_OR_WITHHOLD_GATE'
            else: mode='PROVENANCE_OR_EVIDENCE'
            self._add(CausalObligation(e['r_id'],e['label'],e['status'],e['surviving_burden'],'POST_R186',disp,mode))

        genealogy=self._j('R125_ROADMAP_GENEALOGY.json')
        self.genealogy_nodes=list(genealogy.get('nodes',[]))
        manifest=self._j('R179_REPOSITORY_WIDE_DISPOSITION_MANIFEST.json')
        self.repository_rules=list(manifest.get('rules',[]))
        self.source_contract=self._j('SOURCE_COVERAGE_CONTRACT.json')
        self.dag=self._j('FULL_DEVELOPMENTAL_DAG.json')

    def assert_complete(self):
        missing=[f'R{i}' for i in range(1,195) if f'R{i}' not in self.entries]
        if missing: raise CausalCoverageError(f'missing revision obligations: {missing}')
        if len(self.entries)!=194:
            extras=sorted(set(self.entries)-{f'R{i}' for i in range(1,195)})
            raise CausalCoverageError(f'unexpected obligation identities: {extras}')
        required=('Research/History/**','MetaTheory/Reconciliations/**','MetaTheory/History/**','MetaTheory/Core/**')
        manifest_matches=[r.get('match','') for r in self.repository_rules]
        for req in required:
            if not any(req in x for x in manifest_matches):
                raise CausalCoverageError(f'repository disposition rule missing: {req}')
        if not self.genealogy_nodes:
            raise CausalCoverageError('pre-R70 genealogy missing')
        if self.dag.get('ledger',{}).get('count',117)!=117 and len(self.dag.get('r_nodes',[]))!=117:
            raise CausalCoverageError('developmental DAG/ledger mismatch')
        unresolved=[o.r_id for o in self.entries.values() if o.implementation_mode not in _ALLOWED]
        if unresolved: raise CausalCoverageError(f'unresolved implementation modes: {unresolved}')
        return True

    def counts(self):
        out={k:0 for k in sorted(_ALLOWED)}
        for e in self.entries.values(): out[e.implementation_mode]+=1
        return out

    def open_gates(self):
        return tuple(e for e in self.entries.values() if e.implementation_mode=='OPEN_OR_WITHHOLD_GATE')

    def as_dict(self):
        self.assert_complete()
        return {
            'schema':self.SCHEMA,'revision_count':len(self.entries),'revision_span':['R1','R194'],
            'pre_r1_genealogy_nodes':len(self.genealogy_nodes),'counts':self.counts(),
            'open_gates':[e.r_id for e in self.open_gates()],
            'entries':[e.__dict__ for e in sorted(self.entries.values(),key=lambda x:_rnum(x.r_id) or 10**9)]
        }

    def classify_repository_path(self, path:str)->str:
        """Executable subset of the R179 pathwise disposition function for Research/MetaTheory.
        Historical bytes remain provenance; classification never creates authority.
        """
        p=path.replace('\\','/').lstrip('/')
        if p.startswith('Canonical/Past/'): p=p[len('Canonical/Past/'):]
        elif p.startswith('Canonical/'): p=p[len('Canonical/'):]
        if p.startswith('Research/History/'):
            return 'PROVENANCE_OR_EVIDENCE'
        if p.startswith('Research/Runtime/Integration/R179_VMK1_KERNEL_CURRENT_2026-09-18/'):
            return 'EXECUTABLE_LAW'
        if p.startswith('Research/Runtime/Integration/R154_N1_RELATIONAL_INTERFACE_CURRENT_2026-09-14/'):
            return 'SUPERSEDED_BUT_CAUSAL'
        if p.startswith('Research/'):
            return 'PROVENANCE_OR_EVIDENCE'
        if p.startswith('MetaTheory/Reconciliations/') or p.startswith('MetaTheory/History/'):
            return 'PROVENANCE_OR_EVIDENCE'
        if p.startswith('MetaTheory/Core/'):
            return 'PROVENANCE_OR_EVIDENCE'
        if p in {'MetaTheory/CURRENT.md','MetaTheory/README.md'}:
            return 'PROVENANCE_OR_EVIDENCE'
        raise CausalCoverageError(f'unclassified Research/MetaTheory path: {path}')
