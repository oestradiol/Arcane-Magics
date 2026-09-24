from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / 'benchmarks' / 'edu17r1_mention_incidence'


class EDU17R1BenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = [json.loads(line) for line in (BENCH / 'dev.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
        spec = importlib.util.spec_from_file_location('mention_baseline', BENCH / 'mention_baseline.py')
        cls.baseline = importlib.util.module_from_spec(spec)
        cls.public_result = json.loads((BENCH / 'PUBLIC_DEV_BASELINE_RESULT.json').read_text(encoding='utf-8'))
        assert spec.loader is not None
        spec.loader.exec_module(cls.baseline)

    def test_ids_unique_and_labels_typed(self):
        ids = [r['id'] for r in self.rows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue({r['label'] for r in self.rows} <= {'incidence', 'non_incidence'})

    def test_required_trap_classes_are_present(self):
        subtypes = {r['subtype'] for r in self.rows}
        for subtype in (
            'meta_uncertainty', 'historical', 'methodological', 'negated',
            'other_referent', 'generic_limitation', 'title_trap',
            'resolved_formerly_unknown', 'quoted_uncertainty',
            'availability_not_support', 'object_unresolved', 'conflicting_evidence'
        ):
            self.assertIn(subtype, subtypes)

    def test_naive_mention_baseline_exhibits_the_original_failure_mode(self):
        false_positives = []
        for row in self.rows:
            pred = self.baseline.predict(row['text'])
            if pred == 'incidence' and row['label'] == 'non_incidence':
                false_positives.append(row['id'])
        self.assertGreaterEqual(len(false_positives), 5)

    def test_benchmark_contains_positive_incidence_not_only_traps(self):
        self.assertGreaterEqual(sum(r['label'] == 'incidence' for r in self.rows), 4)


    def test_frozen_public_baseline_matches_current_code_and_data(self):
        tp = fp = tn = fn = 0
        false_positive_ids = []
        for row in self.rows:
            pred = self.baseline.predict(row['text'])
            gold = row['label']
            tp += pred == 'incidence' and gold == 'incidence'
            fp += pred == 'incidence' and gold == 'non_incidence'
            tn += pred == 'non_incidence' and gold == 'non_incidence'
            fn += pred == 'non_incidence' and gold == 'incidence'
            if pred == 'incidence' and gold == 'non_incidence':
                false_positive_ids.append(row['id'])
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        self.assertEqual(self.public_result['n'], len(self.rows))
        self.assertEqual((tp, fp, tn, fn), (
            self.public_result['tp'], self.public_result['fp'],
            self.public_result['tn'], self.public_result['fn'],
        ))
        self.assertAlmostEqual(self.public_result['precision_incidence'], precision)
        self.assertAlmostEqual(self.public_result['recall_incidence'], recall)
        self.assertAlmostEqual(self.public_result['f1_incidence'], f1)
        self.assertEqual(self.public_result['false_positive_ids'], false_positive_ids)
        self.assertFalse(self.public_result['promotion_authority'])


if __name__ == '__main__':
    unittest.main()
