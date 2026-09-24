from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
BENCH=ROOT/'benchmarks'/'world_input_security'

class WorldInputSecurityPublicDevTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=[json.loads(x) for x in (BENCH/'dev.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
        cls.protocol=json.loads((BENCH/'protocol.json').read_text(encoding='utf-8'))
        cls.expected=json.loads((BENCH/'PUBLIC_DEV_BASELINE_RESULT.json').read_text(encoding='utf-8'))
        spec=importlib.util.spec_from_file_location('world_input_baselines',BENCH/'baselines.py')
        cls.baselines=importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(cls.baselines)

    def test_ids_unique_and_dispositions_typed(self):
        ids=[r['id'] for r in self.rows]
        self.assertEqual(len(ids),len(set(ids)))
        allowed=set(self.protocol['dispositions'])
        self.assertTrue(all(r['gold'] in allowed for r in self.rows))

    def test_required_threat_classes_are_present(self):
        attacks={r['attack'] for r in self.rows}
        self.assertEqual(set(self.protocol['threat_classes'])-attacks,set())

    def test_public_floor_results_recompute(self):
        for name,predictor in self.baselines.BASELINES.items():
            got=self.baselines.evaluate(self.rows,predictor)
            exp=self.expected['baselines'][name]
            self.assertEqual(got['correct'],exp['correct'])
            self.assertAlmostEqual(got['accuracy'],exp['accuracy'])
        self.assertFalse(self.expected['promotion_authority'])

    def test_trust_all_and_block_all_are_both_bad_controls(self):
        scores=[self.baselines.evaluate(self.rows,p)['accuracy'] for p in self.baselines.BASELINES.values()]
        self.assertLess(max(scores),0.30)

    def test_protocol_requires_dynamic_hidden_security_evaluation(self):
        self.assertTrue(self.protocol['hidden_dynamic_attack_required_for_promotion'])
        self.assertFalse(self.protocol['promotion_authority'])
        self.assertIn('mature_security_defense',self.protocol['conditions'])

if __name__=='__main__':
    unittest.main()
