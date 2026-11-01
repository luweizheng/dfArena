import csv
import json
from pathlib import Path
import tempfile
import unittest

from evaluation import Evaluator


class GTPositionTests(unittest.TestCase):
    def evaluate(self, gold, candidate, **options):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for side, rows in [('gt', gold), ('candidate', candidate)]:
                (root / side).mkdir()
                with (root / side / 'out.csv').open('w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['group', 'value'])
                    writer.writerows(rows)
            spec = {'key': ['group'], 'columns': {
                'group': {'type': 'text_exact'},
                'value': {'type': 'number', 'abs_tol': 0, 'rel_tol': 0}},
                'ignore_order': False, 'order_mode': 'gt_position'}
            spec.update(options)
            path = root / 'config.json'
            path.write_text(json.dumps({'files': {'out.csv': spec}}))
            return Evaluator(root/'gt', root/'candidate', path).run()

    def test_custom_sequence_and_numeric_equivalence(self):
        result = self.evaluate([['B', 20], ['A', 30], ['B', 10]],
                               [['B', '20.00'], ['A', 30], ['B', 10]])
        self.assertTrue(result['passed'])
        self.assertEqual(result['protocol_version'], 'dfarena-table-v7')

    def test_swapped_blocks_and_within_block(self):
        gold = [['B', 20], ['A', 30], ['B', 10]]
        for candidate in ([gold[2], gold[1], gold[0]], [gold[1], gold[0], gold[2]]):
            result = self.evaluate(gold, candidate)
            self.assertFalse(result['passed'])
            self.assertEqual(result['errors'][0]['error_type'], 'ROW_ORDER_MISMATCH')
            self.assertEqual(result['files']['out.csv']['content_status'], 'passed')

    def test_duplicates_and_incorrect_values(self):
        gold = [['B', 20], ['B', 20], ['A', 10]]
        self.assertTrue(self.evaluate(gold, gold)['passed'])
        self.assertFalse(self.evaluate(gold, gold[1:])['passed'])
        self.assertFalse(self.evaluate(gold, [['B', 20], ['B', 20], ['A', 11]])['passed'])

    def test_invalid_combinations(self):
        for options in ({'ignore_order': True}, {'order_mode': 'guess'},
                        {'order_by': [{'column': 'group', 'direction': 'asc', 'nulls': 'last'}]},
                        {'alternative_gt': {'other': 'variants/other.csv'}}):
            result = self.evaluate([['A', 1]], [['A', 1]], **options)
            self.assertEqual(result['errors'][0]['error_type'], 'CONFIG_ERROR')

    def test_positional_comparison_respects_numeric_tolerance(self):
        cols = {'group': {'type': 'text_exact'},
                'value': {'type': 'number', 'abs_tol': 1e-10, 'rel_tol': 0}}
        gold = [['A', '522.6'], ['A', '200']]
        self.assertTrue(self.evaluate(gold, [['A', '522.5999999999999'], ['A', 200]], columns=cols)['passed'])
        wrong_order = self.evaluate(gold, [['A', 200], ['A', '522.5999999999999']], columns=cols)
        self.assertEqual(wrong_order['errors'][0]['error_type'], 'ROW_ORDER_MISMATCH')
        self.assertFalse(self.evaluate(gold, [['A', '522.6000000002'], ['A', 200]], columns=cols)['passed'])

    def test_default_mode_still_ignores_order(self):
        self.assertTrue(self.evaluate([['B', 20], ['A', 10]], [['A', 10], ['B', 20]],
                                      ignore_order=True, order_mode='fields')['passed'])
