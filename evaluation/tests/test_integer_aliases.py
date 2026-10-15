import csv
import json
from pathlib import Path
import tempfile
import unittest

from evaluation import Evaluator
from evaluation.config import ConfigError, column_rule
from evaluation.normalization import normalize


class IntegerAliasTests(unittest.TestCase):
    def test_opt_in_exact_labels(self):
        rule = column_rule({'type': 'integer', 'aliases': {'Level 2': '2'}})
        for raw in ('2', '2.0', 'Level 2'):
            self.assertEqual(normalize(raw, rule), 2)
        for raw in ('Level 2.5', 'Level 3', 'level 2', ' Level 2 ', '2.5'):
            with self.assertRaises(ValueError):
                normalize(raw, rule)
        with self.assertRaises(ValueError):
            normalize('Level 2', column_rule({'type': 'integer'}))

    def test_invalid_config(self):
        for aliases in ([], {}, {'2': '3'}, {'2.0': '3'}, {'NaN': '1'},
                        {'': '1'}, {'Label': 1}, {'Label': '1.5'},
                        {'Label': 'Other'}, {'Label': '1e2'}):
            with self.subTest(aliases=aliases), self.assertRaises(ConfigError):
                column_rule({'type': 'integer', 'aliases': aliases})
        for nulls in (['Label'], ['2']):
            with self.assertRaises(ConfigError):
                column_rule({'type': 'integer', 'aliases': {'Label': '2'}, 'null_values': nulls})
        with self.assertRaises(ConfigError):
            column_rule({'type': 'number', 'aliases': {'Label': '2'}})

    def test_keys_values_multiplicity_and_numeric_order(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for d in ('gt', 'candidate'):
                (root/d).mkdir()
            spec = {'key': ['id'], 'columns': {
                'id': {'type': 'integer', 'aliases': {'Level 2': '2', 'Level 10': '10'}},
                'cost': {'type': 'number', 'abs_tol': 0, 'rel_tol': 0}},
                'ignore_order': False,
                'order_by': [{'column': 'id', 'direction': 'asc', 'nulls': 'last'}]}
            config = root/'config.json'
            config.write_text(json.dumps({'files': {'out.csv': spec}}))
            def write(side, rows):
                with (root/side/'out.csv').open('w', newline='') as f:
                    w = csv.writer(f); w.writerow(['id', 'cost']); w.writerows(rows)
            write('gt', [['Level 2', '30'], ['10', '40']])
            for rows, expected in [([['2', '30'], ['Level 10', '40']], True),
                                   ([['Level 2', '30'], ['10', '40']], True),
                                   ([['Level 10', '40'], ['2', '30']], False),
                                   ([['Level 2', '31'], ['10', '40']], False),
                                   ([['Level 2', '30'], ['Level 2', '40']], False),
                                   ([['Level 2', '30']], False)]:
                write('candidate', rows)
                result = Evaluator(root/'gt', root/'candidate', config).run()
                self.assertEqual(result['passed'], expected, result)
                self.assertEqual(result['protocol_version'], 'dfarena-table-v5')


if __name__ == '__main__':
    unittest.main()
