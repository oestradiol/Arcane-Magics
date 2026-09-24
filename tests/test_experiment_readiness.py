from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'evaluation'/'EVIDENCE_GOVERNANCE_PREFREEZE.json'

class ExperimentReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec=importlib.util.spec_from_file_location('readiness',ROOT/'scripts'/'audit_experiment_readiness.py')
        cls.mod=importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(cls.mod)
        cls.data=json.loads(MANIFEST.read_text(encoding='utf-8'))

    def test_prefreeze_is_validly_non_executable(self):
        self.assertEqual(self.mod.validate_readiness(self.data),[])
        self.assertFalse(self.data['readiness']['executable'])
        self.assertFalse(self.data['promotion_authority'])

    def test_missing_dependencies_are_real(self):
        missing=set(self.mod.missing_run_fields(self.data))
        self.assertIn('base_model.model',missing)
        self.assertIn('task_surface.hidden_split_hash',missing)
        self.assertIn('evaluator.identity',missing)
        self.assertIn('conditions.A.implementation.adapter_id', missing)
        self.assertIn('conditions.B.implementation.sha256', missing)
        self.assertIn('conditions.E.implementation.version', missing)

    def test_zero_monetary_budget_counts_as_frozen_value(self):
        changed=json.loads(json.dumps(self.data))
        shared=changed['shared_condition']
        shared['monetary_budget_usd']=0
        missing=set(self.mod.missing_run_fields(changed))
        self.assertNotIn('shared_condition.monetary_budget_usd',missing)
    def test_cannot_flip_executable_without_freezing_dependencies(self):
        changed=json.loads(json.dumps(self.data))
        changed['readiness']['executable']=True
        errors=self.mod.validate_readiness(changed)
        self.assertTrue(any('missing run fields' in e for e in errors))

    def test_condition_implementations_are_part_of_run_identity(self):
        changed=json.loads(json.dumps(self.data))
        for row in changed['conditions']:
            row['implementation']={
                'adapter_id': f"adapter-{row['id']}",
                'artifact': f"evaluation/adapters/{row['id']}.json",
                'sha256': 'a'*64,
                'version': 'v1',
            }
        missing=set(self.mod.missing_run_fields(changed))
        self.assertFalse(any(name.startswith('conditions.') for name in missing))

if __name__=='__main__': unittest.main()
