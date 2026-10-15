import csv
import json
from pathlib import Path
import tempfile
import unittest

from evaluation import Evaluator


class AlternativeTableTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.gt = self.root / 'gt'
        self.cand = self.root / 'candidate'
        self.config = self.root / 'config.json'
        self.spec = {'key': ['id'], 'columns': {
            'id': {'type': 'text_exact'}, 'value': {'type': 'number'},
            'rank': {'type': 'integer'}}, 'ignore_order': True,
            'alternative_gt': {'second': 'second/out.csv'}}
        self.write(self.gt/'out.csv', [['a', 2, 1], ['b', 19, 2]])
        self.write(self.gt/'second/out.csv', [['a', 1, 1], ['b', 11, 2]])

    def write(self, path, rows, header=('id', 'value', 'rank')):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(header)
            writer.writerows(rows)

    def evaluate(self, rows):
        self.write(self.cand/'out.csv', rows)
        self.config.write_text(json.dumps({'files': {'out.csv': self.spec}}))
        return Evaluator(self.gt, self.cand, self.config).run()

    def test_complete_variants_and_hashes(self):
        for rows, variant in [([['b',19,2],['a',2,1]], 'primary'),
                              ([['b',11,2],['a',1,1]], 'second')]:
            report = self.evaluate(rows)
            self.assertTrue(report['passed'], report)
            self.assertEqual(report['files']['out.csv']['matched_variant'], variant)
            self.assertEqual(set(report['assets']['gt']), {'out.csv', 'second/out.csv'})
            self.assertEqual(report['protocol_version'], 'dfarena-table-v4')

    def test_mixed_rows_and_wrong_rank_rejected(self):
        for rows in [[['a',2,1],['b',11,2]], [['a',1,2],['b',11,2]],
                     [['a',1.01,1],['b',11,2]], [['a',1,1]],
                     [['a',1,1],['a',1,1]], [['a',1,1],['c',11,2]]]:
            report = self.evaluate(rows)
            self.assertFalse(report['passed'], report)
            self.assertEqual(len(report['errors'][0]['detail']['alternative_errors']), 2)

    def test_broken_alternative_is_gt_error_even_when_primary_matches(self):
        for rows, header in [([['a','oops',1]], ('id','value','rank')),
                             ([['a',1]], ('id','value'))]:
            self.write(self.gt/'second/out.csv', rows, header)
            report = self.evaluate([['a',2,1],['b',19,2]])
            self.assertFalse(report['passed'])
            self.assertEqual(report['errors'][0]['side'], 'gt')
        (self.gt/'second/out.csv').unlink()
        self.assertEqual(self.evaluate([['a',2,1],['b',19,2]])['errors'][0]['side'], 'gt')

    def test_bad_paths_rejected(self):
        for value in ['../out.csv', '/out.csv', 'C:/out.csv', 'second\\out.csv', './out.csv']:
            self.spec['alternative_gt'] = {'second': value}
            report = self.evaluate([['a',2,1],['b',19,2]])
            self.assertEqual(report['errors'][0]['side'], 'config')

    def test_order_still_enforced(self):
        self.spec.update(ignore_order=False, order_by=[{'column':'rank','direction':'asc','nulls':'last'}])
        report = self.evaluate([['b',11,2],['a',1,1]])
        self.assertFalse(report['passed'])
        self.assertTrue(self.evaluate([['a',1,1],['b',11,2]])['passed'])
        self.write(self.gt/'second/out.csv', [['b',11,2],['a',1,1]])
        report = self.evaluate([['a',2,1],['b',19,2]])
        self.assertEqual(report['errors'][0]['error_type'], 'GT_ORDER_ERROR')


if __name__ == '__main__':
    unittest.main()
