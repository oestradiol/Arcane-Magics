from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import hashlib,json
from .runtime import OntogeneticVM
from .post_r69 import PostR69Registry,PostR69ConservationGate
@dataclass
class R154N1AntiOrientedSeed:
 vm:OntogeneticVM;gate:dict;label:str='R154_N1_ANTI_ORIENTED'
 @classmethod
 def boot_current(cls,root=None,adapter=None,allow_blocked=False):
  from .canonical import digest
  from .organism_language import OrganismLanguageMembrane
  from .capability_pressure_multifamily import MultiMachineryMembrane
  from .capability_pressure_diagnosis import P9DiagnosticMembrane
  root=Path(root) if root else Path(__file__).parents[1];m=json.loads((root/'state'/'CURRENT_R154_N1_ANTI_ORIENTED_MANIFEST_v0.1.json').read_text())
  for rel,d in m['files'].items():
   p=root/rel;b=p.read_bytes()
   if len(b)!=d['bytes'] or hashlib.sha256(b).hexdigest()!=d['sha256']:raise RuntimeError(f'R154 payload mismatch: {rel}')
  reg=PostR69Registry.load(root/'post_r69'/'POST_R69_R154_RECONCILIATION_LEDGER.json',root=root);g=PostR69ConservationGate(reg).evaluate()
  if not allow_blocked and not g['current_vm_eligible']:raise RuntimeError('R154 conservation blocked')
  vm=OntogeneticVM(root/'state'/'CURRENT_R154_N1_ANTI_ORIENTED_TRAJECTORY_v0.1.jsonl',adapter=adapter);e=m['expected'];lang=OrganismLanguageMembrane(vm,dimensions=16384);sc=vm.project_state['science']
  checks=(vm.project_state.get('through')=='R154',len(vm.reconciliations)==85,len(vm.journal.events)==e['event_count'],vm.journal.head==e['trajectory_head'],digest(vm.project_state)==e['project_state_digest'],lang.state.state_digest==e['language_state_digest'],len(lang.state.episode_ids)==e['language_episode_count'],MultiMachineryMembrane(vm).state.state_digest==e['task_machinery_state_digest'],P9DiagnosticMembrane(vm).state.state_digest==e['diagnostic_state_digest'],sc['N1_RS_NPR_CC_CONJUNCTIVE_MINIMALITY'].startswith('CLOSED'),sc['N1_COMPLETE_2X2X2_INTERACTION'].startswith('OPEN'),sc['ANTI_ORIENTATION_NECESSITY'].startswith('NOT ESTABLISHED'),sc['NEXT_ORDER_RELATIONAL_INTERFACE_SUFFICIENCY'].startswith('CLOSED'),sc['ORIENTATION_CHANGE_NECESSITY'].startswith('NOT ESTABLISHED'),sc['PERSPECTIVE_OMEGA_FULL_COMPLEMENTARITY']=='OPEN')
  if not all(checks):raise RuntimeError('R154 current state reconstruction failed')
  return cls(vm=vm,gate=g)
CurrentScientificSeed=R154N1AntiOrientedSeed
CurrentReconciliationSeed=R154N1AntiOrientedSeed
CurrentDevelopmentalSeed=R154N1AntiOrientedSeed
