from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import hashlib, json
from .runtime import OntogeneticVM
from .post_r69 import PostR69Registry, PostR69ConservationGate

@dataclass
class R149ReductionFalsificationSeed:
    vm: OntogeneticVM
    gate: dict
    label: str='R149_REDUCTION_FALSIFICATION_AUDIT'

    @classmethod
    def boot_current(cls,root=None,adapter=None,allow_blocked=False):
        from .canonical import digest
        from .organism_language import OrganismLanguageMembrane
        from .capability_pressure_multifamily import MultiMachineryMembrane
        from .capability_pressure_diagnosis import P9DiagnosticMembrane
        root=Path(root) if root else Path(__file__).parents[1]
        manifest=json.loads((root/'state'/'CURRENT_R149_REDUCTION_FALSIFICATION_MANIFEST_v0.1.json').read_text())
        for rel,desc in manifest['files'].items():
            p=root/rel
            if not p.exists(): raise RuntimeError(f'R149 current payload missing: {rel}')
            raw=p.read_bytes()
            if len(raw)!=desc['bytes'] or hashlib.sha256(raw).hexdigest()!=desc['sha256']:
                raise RuntimeError(f'R149 current payload mismatch: {rel}')
        reg=PostR69Registry.load(root/'post_r69'/'POST_R69_R149_RECONCILIATION_LEDGER.json',root=root)
        gate=PostR69ConservationGate(reg).evaluate()
        if not allow_blocked and not gate['current_vm_eligible']:
            raise RuntimeError(f'POST_R69_R149_CONSERVATION_BLOCKED: {len(gate["failures"])} failures')
        vm=OntogeneticVM(root/'state'/'CURRENT_R149_REDUCTION_FALSIFICATION_TRAJECTORY_v0.1.jsonl',adapter=adapter)
        exp=manifest['expected']; lang=OrganismLanguageMembrane(vm,dimensions=16384)
        checks=(
            vm.project_state.get('through')==exp['project_state_through'], len(vm.reconciliations)==exp['reconciliation_count'],
            len(vm.journal.events)==exp['event_count'], vm.journal.head==exp['trajectory_head'], digest(vm.project_state)==exp['project_state_digest'],
            lang.state.state_digest==exp['language_state_digest'], len(lang.state.episode_ids)==exp['language_episode_count'],
            MultiMachineryMembrane(vm).state.state_digest==exp['task_machinery_state_digest'], P9DiagnosticMembrane(vm).state.state_digest==exp['diagnostic_state_digest'],
            vm.project_state.get('developmental',{}).get('SELF_MODEL_REDUCTION_R149')==exp['self_model_reduction'],
            vm.project_state.get('science',{}).get('SELF_MODEL_SPECIFIC_CAUSAL_PRIVILEGE','').startswith('NOT ESTABLISHED'),
            vm.project_state.get('science',{}).get('N2_FULL_PARENT_R133','').startswith('CLOSED'),
        )
        if not all(checks): raise RuntimeError('R149 current audit state failed reconstruction checks')
        return cls(vm=vm,gate=gate)

CurrentAuditSeed=R149ReductionFalsificationSeed
CurrentDevelopmentalSeed=R149ReductionFalsificationSeed
