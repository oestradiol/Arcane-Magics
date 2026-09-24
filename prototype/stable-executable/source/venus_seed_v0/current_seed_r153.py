from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import hashlib,json
from .runtime import OntogeneticVM
from .post_r69 import PostR69Registry,PostR69ConservationGate
@dataclass
class R153BidirectionalIdentifiabilitySeed:
 vm:OntogeneticVM;gate:dict;label:str='R153_BIDIRECTIONAL_IDENTIFIABILITY'
 @classmethod
 def boot_current(cls,root=None,adapter=None,allow_blocked=False):
  from .canonical import digest
  from .organism_language import OrganismLanguageMembrane
  from .capability_pressure_multifamily import MultiMachineryMembrane
  from .capability_pressure_diagnosis import P9DiagnosticMembrane
  root=Path(root) if root else Path(__file__).parents[1];m=json.loads((root/'state'/'CURRENT_R153_BIDIRECTIONAL_IDENTIFIABILITY_MANIFEST_v0.1.json').read_text())
  for rel,d in m['files'].items():
   p=root/rel;b=p.read_bytes()
   if len(b)!=d['bytes'] or hashlib.sha256(b).hexdigest()!=d['sha256']:raise RuntimeError(f'R153 payload mismatch: {rel}')
  reg=PostR69Registry.load(root/'post_r69'/'POST_R69_R153_RECONCILIATION_LEDGER.json',root=root);g=PostR69ConservationGate(reg).evaluate()
  if not allow_blocked and not g['current_vm_eligible']:raise RuntimeError('R153 conservation blocked')
  vm=OntogeneticVM(root/'state'/'CURRENT_R153_BIDIRECTIONAL_IDENTIFIABILITY_TRAJECTORY_v0.1.jsonl',adapter=adapter);e=m['expected'];lang=OrganismLanguageMembrane(vm,dimensions=16384);sc=vm.project_state['science']
  checks=(vm.project_state.get('through')=='R153',len(vm.reconciliations)==84,len(vm.journal.events)==e['event_count'],vm.journal.head==e['trajectory_head'],digest(vm.project_state)==e['project_state_digest'],lang.state.state_digest==e['language_state_digest'],len(lang.state.episode_ids)==e['language_episode_count'],MultiMachineryMembrane(vm).state.state_digest==e['task_machinery_state_digest'],P9DiagnosticMembrane(vm).state.state_digest==e['diagnostic_state_digest'],sc['REALIZATION_POSSIBILITY_BIDIRECTIONAL_NONIDENTIFIABILITY'].startswith('CLOSED'),sc['JOINT_RELATION_PREDICTIVE_SUFFICIENCY'].startswith('CLOSED'),sc['JOINT_RELATION_MINIMALITY']=='OPEN',sc['PERSPECTIVE_OMEGA_FULL_COMPLEMENTARITY']=='OPEN',sc['N1_WHOLE_OBJECT']=='OPEN')
  if not all(checks):raise RuntimeError('R153 current state reconstruction failed')
  return cls(vm=vm,gate=g)
CurrentScientificSeed=R153BidirectionalIdentifiabilitySeed
CurrentReconciliationSeed=R153BidirectionalIdentifiabilitySeed
CurrentDevelopmentalSeed=R153BidirectionalIdentifiabilitySeed
