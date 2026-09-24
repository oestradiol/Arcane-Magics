from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import hashlib, json
from .runtime import OntogeneticVM
from .post_r69 import PostR69Registry,PostR69ConservationGate,replay_reconciliations

@dataclass
class R131ReintegrationCandidate:
    """Conservation-closed R131 integrated Venus Seed successor.

    Heritage/evidence bytes stay outside learner state. The VM receives only hash-bound
    reconciliation dispositions and the resulting ProjectState projection. Invalid and
    negative historical lineages remain replayable without acquiring scientific authority.
    """
    vm: OntogeneticVM
    gate: dict
    label: str="R131_REINTEGRATED_VM"
    @classmethod
    def boot(cls,root=None,journal_path=None,adapter=None,allow_blocked=False):
        root=Path(root) if root else Path(__file__).parents[1]
        reg=PostR69Registry.load(root/'post_r69'/'POST_R69_RECONCILIATION_LEDGER.json',root=root)
        gate=PostR69ConservationGate(reg).evaluate()
        if not allow_blocked and not gate['current_vm_eligible']:
            raise RuntimeError(f"POST_R69_CONSERVATION_BLOCKED: {len(gate['failures'])} failures")
        vm=OntogeneticVM(journal_path=journal_path,adapter=adapter)
        replay_reconciliations(vm,reg)
        return cls(vm=vm,gate=gate)

# Promoted name. The historical class name is retained for compatibility.
R131IntegratedSeed = R131ReintegrationCandidate


@dataclass
class R132IntegratedSeed:
    """Conservation-closed R132 scientific successor.

    R132 adds the bounded N2 reconstructed-invariant causal/action-core result to the
    already conserved R131 organism while preserving all stronger/open residuals.
    """
    vm: OntogeneticVM
    gate: dict
    label: str="R132_N2_CAUSAL_ACTION_INTEGRATED_VM"

    @classmethod
    def boot(cls,root=None,journal_path=None,adapter=None,allow_blocked=False):
        root=Path(root) if root else Path(__file__).parents[1]
        reg=PostR69Registry.load(root/'post_r69'/'POST_R69_R132_RECONCILIATION_LEDGER.json',root=root)
        gate=PostR69ConservationGate(reg).evaluate()
        if not allow_blocked and not gate['current_vm_eligible']:
            raise RuntimeError(f"POST_R69_R132_CONSERVATION_BLOCKED: {len(gate['failures'])} failures")
        vm=OntogeneticVM(journal_path=journal_path,adapter=adapter)
        replay_reconciliations(vm,reg,through=132)
        return cls(vm=vm,gate=gate)

    @classmethod
    def promote_from_r131_vm(cls,vm,root=None,allow_blocked=False):
        """Append only the R132 reconciliation/project-state writeback to an existing R131 history."""
        root=Path(root) if root else Path(__file__).parents[1]
        if not isinstance(getattr(vm,"project_state",None),dict) or vm.project_state.get("through")!="R131":
            raise ValueError("R132 promotion requires an existing conserved ProjectState through R131")
        reg=PostR69Registry.load(root/'post_r69'/'POST_R69_R132_RECONCILIATION_LEDGER.json',root=root)
        gate=PostR69ConservationGate(reg).evaluate()
        if not allow_blocked and not gate['current_vm_eligible']:
            raise RuntimeError(f"POST_R69_R132_CONSERVATION_BLOCKED: {len(gate['failures'])} failures")
        replay_reconciliations(vm,reg,through=132)
        if vm.project_state.get("through")!="R132":
            raise RuntimeError("R132 promotion did not produce ProjectState through R132")
        return cls(vm=vm,gate=gate)


R132CurrentSeed = R132IntegratedSeed


@dataclass
class R132ProjectLanguageSeed:
    """Persistent current developmental state after R132-gated project-language learning."""
    vm: OntogeneticVM
    gate: dict
    learner_state_digest: str
    label: str="R132_PROJECT_LANGUAGE_DEVELOPMENTAL_STATE_v0.1"

    @classmethod
    def boot_current(cls,root=None,adapter=None,allow_blocked=False):
        from .semantic_learning import SemanticLearningMembrane
        from .canonical import digest
        root=Path(root) if root else Path(__file__).parents[1]
        manifest_path=root/'state'/'CURRENT_R132_PROJECT_LANGUAGE_MANIFEST_v0.1.json'
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        for rel,desc in manifest['files'].items():
            p=root/rel
            if not p.exists():
                raise RuntimeError(f"current developmental state missing payload: {rel}")
            raw=p.read_bytes()
            if len(raw)!=desc['bytes'] or hashlib.sha256(raw).hexdigest()!=desc['sha256']:
                raise RuntimeError(f"current developmental state payload mismatch: {rel}")
        reg=PostR69Registry.load(root/manifest['conservation_ledger'],root=root)
        gate=PostR69ConservationGate(reg).evaluate()
        if not allow_blocked and not gate['current_vm_eligible']:
            raise RuntimeError(f"POST_R69_R132_CONSERVATION_BLOCKED: {len(gate['failures'])} failures")
        vm=OntogeneticVM(journal_path=root/'state'/'CURRENT_R132_PROJECT_LANGUAGE_TRAJECTORY_v0.1.jsonl',adapter=adapter)
        learner=SemanticLearningMembrane(vm)
        exp=manifest['expected']
        checks=(
            vm.project_state.get('through')==exp['project_state_through'],
            len(vm.reconciliations)==exp['reconciliation_count'],
            len(learner.state.completed_items)==exp['completed_item_count'],
            learner.state.state_digest==exp['final_learner_state_digest'],
            vm.journal.head==exp['final_trajectory_head'],
            digest(vm.project_state)==exp['project_state_digest'],
            vm.project_state.get('developmental',{}).get('N2_HSTAR_id')==exp['hstar_id'],
        )
        if not all(checks):
            raise RuntimeError('current R132 developmental state failed reconstruction checks')
        return cls(vm=vm,gate=gate,learner_state_digest=learner.state.state_digest)


CurrentDevelopmentalSeed = R132ProjectLanguageSeed

@dataclass
class R133RecanonicalizedSeed:
    """Executable routing successor carrying R133 attribution narrowing; no new science."""
    vm: OntogeneticVM
    gate: dict
    label: str="R133_RECANONICALIZED_VM"

    @classmethod
    def boot(cls,root=None,journal_path=None,adapter=None,allow_blocked=False):
        root=Path(root) if root else Path(__file__).parents[1]
        reg=PostR69Registry.load(root/'post_r69'/'POST_R69_R133_RECONCILIATION_LEDGER.json',root=root)
        gate=PostR69ConservationGate(reg).evaluate()
        if not allow_blocked and not gate['current_vm_eligible']:
            raise RuntimeError(f"POST_R69_R133_CONSERVATION_BLOCKED: {len(gate['failures'])} failures")
        vm=OntogeneticVM(journal_path=journal_path,adapter=adapter)
        replay_reconciliations(vm,reg,through=133)
        return cls(vm=vm,gate=gate)

@dataclass
class R134LanguageEngineeringSeed:
    """Current R134 engineering successor with organism-owned learned language state.

    This is an engineering carrier only. It preserves R133's reopened N2 scientific status.
    """
    vm: OntogeneticVM
    gate: dict
    language_state_digest: str
    label: str="R134_ORGANISM_LANGUAGE_ENGINEERING_v0.1"

    @classmethod
    def boot_current(cls,root=None,adapter=None,allow_blocked=False):
        from .organism_language import OrganismLanguageMembrane
        from .canonical import digest
        root=Path(root) if root else Path(__file__).parents[1]
        manifest_path=root/'state'/'CURRENT_R134_LANGUAGE_MANIFEST_v0.1.json'
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        for rel,desc in manifest['files'].items():
            p=root/rel
            if not p.exists():
                raise RuntimeError(f"current R134 language state missing payload: {rel}")
            raw=p.read_bytes()
            if len(raw)!=desc['bytes'] or hashlib.sha256(raw).hexdigest()!=desc['sha256']:
                raise RuntimeError(f"current R134 language payload mismatch: {rel}")
        reg=PostR69Registry.load(root/manifest['conservation_ledger'],root=root)
        gate=PostR69ConservationGate(reg).evaluate()
        if not allow_blocked and not gate['current_vm_eligible']:
            raise RuntimeError(f"POST_R69_R134_CONSERVATION_BLOCKED: {len(gate['failures'])} failures")
        vm=OntogeneticVM(journal_path=root/'state'/'CURRENT_R134_LANGUAGE_TRAJECTORY_v0.1.jsonl',adapter=adapter)
        lang=OrganismLanguageMembrane(vm,dimensions=16384)
        exp=manifest['expected']
        checks=(
            vm.project_state.get('through')==exp['project_state_through'],
            len(vm.reconciliations)==exp['reconciliation_count'],
            len(lang.state.episode_ids)==exp['language_episode_count'],
            len(lang.state.prototype_sums)==exp['response_prototype_count'],
            lang.state.state_digest==exp['language_state_digest'],
            vm.journal.head==exp['trajectory_head'],
            digest(vm.project_state)==exp['project_state_digest'],
        )
        if not all(checks):
            raise RuntimeError('current R134 developmental state failed reconstruction checks')
        return cls(vm=vm,gate=gate,language_state_digest=lang.state.state_digest)

CurrentDevelopmentalSeed = R134LanguageEngineeringSeed


@dataclass
class R143IntegratedSeed:
    """Current unified VM through R143 governance reintegration; R142 remains latest science."""
    vm: OntogeneticVM
    gate: dict
    label: str="R143_UNIFIED_VM_INTEGRATED"

    @classmethod
    def boot_current(cls,root=None,adapter=None,allow_blocked=False):
        from .canonical import digest
        from .organism_language import OrganismLanguageMembrane
        from .capability_pressure_multifamily import MultiMachineryMembrane
        from .capability_pressure_diagnosis import P9DiagnosticMembrane
        root=Path(root) if root else Path(__file__).parents[1]
        manifest=json.loads((root/'state'/'CURRENT_R143_VM_INTEGRATED_MANIFEST_v0.1.json').read_text(encoding='utf-8'))
        for rel,desc in manifest['files'].items():
            p=root/rel
            raw=p.read_bytes()
            if len(raw)!=desc['bytes'] or hashlib.sha256(raw).hexdigest()!=desc['sha256']:
                raise RuntimeError(f'R143 current-integrated payload mismatch: {rel}')
        reg=PostR69Registry.load(root/'post_r69'/'POST_R69_R143_RECONCILIATION_LEDGER.json',root=root)
        gate=PostR69ConservationGate(reg).evaluate()
        if not allow_blocked and not gate['current_vm_eligible']:
            raise RuntimeError(f'POST_R69_R143_CONSERVATION_BLOCKED: {len(gate["failures"])} failures')
        vm=OntogeneticVM(root/'state'/'CURRENT_R143_VM_INTEGRATED_TRAJECTORY_v0.1.jsonl',adapter=adapter)
        exp=manifest['expected']
        checks=(
            vm.project_state.get('through')==exp['project_state_through'],
            len(vm.reconciliations)==exp['reconciliation_count'],
            vm.journal.head==exp['trajectory_head'],
            len(vm.journal.events)==exp['event_count'],
            digest(vm.project_state)==exp['project_state_digest'],
            OrganismLanguageMembrane(vm,dimensions=16384).state.state_digest==exp['language_state_digest'],
            MultiMachineryMembrane(vm).state.state_digest==exp['task_machinery_state_digest'],
            P9DiagnosticMembrane(vm).state.state_digest==exp['diagnostic_state_digest'],
        )
        if not all(checks):
            raise RuntimeError('R143 current integrated VM failed reconstruction checks')
        return cls(vm=vm,gate=gate)

CurrentDevelopmentalSeed = R143IntegratedSeed

@dataclass
class R144T10DevelopmentalSeed:
    """Current R144 developmental successor: T10 mature vocabulary admitted; comparison WITHHOLD.

    R142 remains the scientific head. R144 changes organism language state only through
    post-gate curriculum and records a returned comparison Residual without inventing a
    MAP/PARTIAL-MAP/REJECT verdict.
    """
    vm: OntogeneticVM
    gate: dict
    label: str="R144_T10_PROJECT_LANGUAGE_DEVELOPMENTAL"

    @classmethod
    def boot_current(cls,root=None,adapter=None,allow_blocked=False):
        from .canonical import digest
        from .organism_language import OrganismLanguageMembrane
        from .capability_pressure_multifamily import MultiMachineryMembrane
        from .capability_pressure_diagnosis import P9DiagnosticMembrane
        root=Path(root) if root else Path(__file__).parents[1]
        manifest=json.loads((root/'state'/'CURRENT_R144_T10_MANIFEST_v0.1.json').read_text(encoding='utf-8'))
        for rel,desc in manifest['files'].items():
            p=root/rel
            raw=p.read_bytes()
            if len(raw)!=desc['bytes'] or hashlib.sha256(raw).hexdigest()!=desc['sha256']:
                raise RuntimeError(f'R144 current T10 payload mismatch: {rel}')
        reg=PostR69Registry.load(root/'post_r69'/'POST_R69_R144_RECONCILIATION_LEDGER.json',root=root)
        gate=PostR69ConservationGate(reg).evaluate()
        if not allow_blocked and not gate['current_vm_eligible']:
            raise RuntimeError(f'POST_R69_R144_CONSERVATION_BLOCKED: {len(gate["failures"])} failures')
        vm=OntogeneticVM(root/'state'/'CURRENT_R144_T10_TRAJECTORY_v0.1.jsonl',adapter=adapter)
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
        )
        if not all(checks):
            raise RuntimeError('R144 current T10 developmental state failed reconstruction checks')
        return cls(vm=vm,gate=gate)

CurrentDevelopmentalSeed = R144T10DevelopmentalSeed


@dataclass
class R145RelationalComparisonSeed:
    """Current R145 developmental successor: bounded relational comparison returns PARTIAL-MAP.

    R142 remains the scientific head. R145 adds no science; it closes only the local
    R144 comparison-production engineering residual at a structured operational interface
    while preserving N1 whole-object interaction/minimality as open.
    """
    vm: OntogeneticVM
    gate: dict
    label: str="R145_RELATIONAL_COMPARISON_DEVELOPMENTAL"

    @classmethod
    def boot_current(cls,root=None,adapter=None,allow_blocked=False):
        from .canonical import digest
        from .organism_language import OrganismLanguageMembrane
        from .capability_pressure_multifamily import MultiMachineryMembrane
        from .capability_pressure_diagnosis import P9DiagnosticMembrane
        root=Path(root) if root else Path(__file__).parents[1]
        manifest=json.loads((root/'state'/'CURRENT_R145_RELATIONAL_COMPARISON_MANIFEST_v0.1.json').read_text(encoding='utf-8'))
        for rel,desc in manifest['files'].items():
            p=root/rel
            if not p.exists():
                raise RuntimeError(f'R145 current payload missing: {rel}')
            raw=p.read_bytes()
            if len(raw)!=desc['bytes'] or hashlib.sha256(raw).hexdigest()!=desc['sha256']:
                raise RuntimeError(f'R145 current payload mismatch: {rel}')
        reg=PostR69Registry.load(root/'post_r69'/'POST_R69_R145_RECONCILIATION_LEDGER.json',root=root)
        gate=PostR69ConservationGate(reg).evaluate()
        if not allow_blocked and not gate['current_vm_eligible']:
            raise RuntimeError(f'POST_R69_R145_CONSERVATION_BLOCKED: {len(gate["failures"])} failures')
        vm=OntogeneticVM(root/'state'/'CURRENT_R145_RELATIONAL_COMPARISON_TRAJECTORY_v0.1.jsonl',adapter=adapter)
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
            vm.project_state.get('science',{}).get('N1_WHOLE_OBJECT')=='OPEN',
        )
        if not all(checks):
            raise RuntimeError('R145 current relational-comparison developmental state failed reconstruction checks')
        return cls(vm=vm,gate=gate)

CurrentDevelopmentalSeed = R145RelationalComparisonSeed
