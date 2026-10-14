import csv
import json
from pathlib import Path
import tempfile
import unittest

from evaluation import Evaluator
from evaluation.config import ConfigError, column_rule
from evaluation.normalization import normalize


class TextAliasTests(unittest.TestCase):
    def test_exact_opt_in(self):
        rule = column_rule({'type': 'text_exact', 'aliases': {'short': 'Full label'}})
        self.assertEqual(normalize('short', rule), normalize('Full label', rule))
        for other in ('Short', ' short', 'short ', 'Full label (extra)'):
            self.assertNotEqual(normalize(other, rule), 'Full label')
        self.assertEqual(normalize('short', column_rule({'type':'text_exact'})), 'short')

    def test_invalid_maps(self):
        for aliases in ({}, [], {'a':1}, {'a':''}, {'':'a'},
                        {'a':'b','b':'c'}, {'a':'b','b':'a'}, {'a':'a'}):
            with self.subTest(aliases=aliases), self.assertRaises(ConfigError):
                column_rule({'type':'text_exact','aliases':aliases})
        for nulls in (['a'], ['b']):
            with self.assertRaises(ConfigError):
                column_rule({'type':'text_exact','aliases':{'a':'b'},'null_values':nulls})

    def test_keys_values_and_other_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for folder in ('gt','candidate'):(root/folder).mkdir()
            spec={'key':['id'],'columns':{
                'id':{'type':'text_exact','aliases':{'short id':'Full ID'}},
                'category':{'type':'text_exact','aliases':{'short':'Full category'}},
                'amount':{'type':'number','abs_tol':0,'rel_tol':0}}}
            (root/'config.json').write_text(json.dumps({'files':{'out.csv':spec}}))
            def write(folder,rows):
                with (root/folder/'out.csv').open('w',newline='') as f:
                    w=csv.writer(f);w.writerow(['id','category','amount']);w.writerows(rows)
            write('gt',[['short id','Full category','12'],['other','short','5']])
            good=[['Full ID','short','12.00'],['other','Full category','5']]
            for rows,expected in [(good,True),([good[0],good[0]],False),(good[:1],False),
                                  ([['Full ID','wrong','12'],good[1]],False),
                                  ([['Full ID','short','12.01'],good[1]],False)]:
                write('candidate',rows)
                result=Evaluator(root/'gt',root/'candidate',root/'config.json').run()
                self.assertEqual(result['passed'],expected,result)
                self.assertEqual(result['protocol_version'],'dfarena-table-v6')


if __name__=='__main__':unittest.main()
