from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import hashlib, json
from .runtime import OntogeneticVM
from .post_r69 import PostR69Registry, PostR69ConservationGate

@dataclass
class R148MultiTurnCompositionSeed:
    """Current R148 developmental successor: bounded internal multi-turn composition.

    R142 remains the scientific head. R148 adds no independently authored language
    evidence, unrestricted natural-language competence, or N1 whole-object closure.
    """
    vm: OntogeneticVM
    gate: dict
    label: str="R148_MULTITURN_COMPOSITION_DEVELOPMENTAL"

    @classmethod
    def boot_current(cls,root=None,adapter=None,allow_blocked=False):
        from .canonical import digest
        from .organism_language import OrganismLanguageMembrane
        from .capability_pressure_multifamily import MultiMachineryMembrane
        from .capability_pressure_diagnosis import P9DiagnosticMembrane
        root=Path(root) if root else Path(__file__).parents[1]
        manifest=json.loads((root/'state'/'CURRENT_R148_MULTITURN_COMPOSITION_MANIFEST_v0.1.json').read_text(encoding='utf-8'))
        for rel,desc in manifest['files'].items():
            p=root/rel
            if not p.exists():
                raise RuntimeError(f'R148 current payload missing: {rel}')
            raw=p.read_bytes()
            if len(raw)!=desc['bytes'] or hashlib.sha256(raw).hexdigest()!=desc['sha256']:
                raise RuntimeError(f'R148 current payload mismatch: {rel}')
        reg=PostR69Registry.load(root/'post_r69'/'POST_R69_R148_RECONCILIATION_LEDGER.json',root=root)
        gate=PostR69ConservationGate(reg).evaluate()
        if not allow_blocked and not gate['current_vm_eligible']:
            raise RuntimeError(f'POST_R69_R148_CONSERVATION_BLOCKED: {len(gate["failures"])} failures')
        vm=OntogeneticVM(root/'state'/'CURRENT_R148_MULTITURN_COMPOSITION_TRAJECTORY_v0.1.jsonl',adapter=adapter)
        exp=manifest['expected']
        lang=OrganismLanguageMembrane(vm,dimensions=16384)
        checks=(
            vm.project_state.get('through')==exp['project_state_through'],
            len(vm.reconciliations)==exp['reconciliation_count'],
            vm.journal.head==exp['trajectory_head'],
            len(vm.journal.events)==exp['event_count'],
            digest(vm.project_state)==exp['project_state_digest'],
            lang.state.state_digest==exp['language_state_digest'],
            len(lang.state.episode_ids)==exp['language_episode_count'],
            MultiMachineryMembrane(vm).state.state_digest==exp['task_machinery_state_digest'],
            P9DiagnosticMembrane(vm).state.state_digest==exp['diagnostic_state_digest'],
            vm.project_state.get('developmental',{}).get('T10_COMPARISON')==exp['t10_comparison'],
            vm.project_state.get('developmental',{}).get('R148_MULTITURN_COMPOSITION')==exp['r148_status'],
            vm.project_state.get('science',{}).get('N1_WHOLE_OBJECT')=='OPEN',
            vm.project_state.get('science',{}).get('NATURAL_LANGUAGE_EXTERNAL_GENERALIZATION','').startswith('OPEN'),
        )
        if not all(checks):
            raise RuntimeError('R148 current multi-turn developmental state failed reconstruction checks')
        return cls(vm=vm,gate=gate)

CurrentDevelopmentalSeed = R148MultiTurnCompositionSeed
