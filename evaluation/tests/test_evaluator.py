import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from evaluation import Evaluator


class TableTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.gt, self.cand = self.root/'gt', self.root/'cand'
        self.gt.mkdir()
        self.cand.mkdir()
        self.config = self.root/'config.json'

    def write(self, root, header, rows):
        with (root/'out.csv').open('w', newline='') as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)

    def compare(self, gt, cand, columns=None, key=None, **options):
        columns = columns or {'ID': 'text_exact', 'Value': 'integer'}
        spec = {'columns': columns, 'key': key or ['ID'], **options}
        self.config.write_text(json.dumps({'files': {'out.csv': spec}}))
        self.write(self.gt, list(columns), gt)
        self.write(self.cand, list(columns), cand)
        return self.run_eval()

    def run_eval(self):
        return Evaluator(self.gt, self.cand, self.config).run()

    def error(self, report, code, side=None):
        self.assertFalse(report['passed'], report)
        self.assertEqual(report['errors'][0]['error_type'], code, report)
        if side:
            self.assertEqual(report['errors'][0]['side'], side)

    def order(self, column='Value', direction='desc', nulls='last'):
        return {'column': column, 'direction': direction, 'nulls': nulls}

    def test_default_ignore_and_integer_representation(self):
        r = self.compare([['A','1'],['B','2']], [['B','2.0'],['A','1.0']])
        self.assertTrue(r['passed'])
        self.assertEqual(r['files']['out.csv']['order_status'], 'ignored')

    def test_integer_exact_and_invalid(self):
        self.error(self.compare([['A','1000']], [['A','1001']]), 'VALUE_MISMATCH')
        self.error(self.compare([['A','1']], [['A','1.1']]), 'TYPE_ERROR', 'candidate')
        self.assertTrue(self.compare([['A','9007199254740993']], [['A','9007199254740993.0']])['passed'])
        self.error(self.compare([['A','9007199254740993']], [['A','9007199254740992']]), 'VALUE_MISMATCH')

    def test_legacy_number_boundary_and_zero(self):
        cols = {'ID':'text_exact','Value':'number'}
        self.assertTrue(self.compare([['A',100]], [['A',101]], cols)['passed'])
        self.error(self.compare([['A',98]], [['A',100]], cols), 'VALUE_MISMATCH')
        self.assertTrue(self.compare([['A',0]], [['A',0.019]], cols)['passed'])
        self.error(self.compare([['A',0]], [['A',0.02]], cols), 'VALUE_MISMATCH')

    def test_explicit_tolerances(self):
        cols = {'ID':'text_exact','Value':{'type':'number','rel_tol':0.01}}
        self.assertTrue(self.compare([['A',100]], [['A',101]], cols)['passed'])
        self.error(self.compare([['A',100]], [['A',101.0001]], cols), 'VALUE_MISMATCH')
        self.error(self.compare([['A',0]], [['A',0.0001]], cols), 'VALUE_MISMATCH')
        cols['Value'] = {'type':'number','abs_tol':0.1}
        self.assertTrue(self.compare([['A',0]], [['A',0.1]], cols)['passed'])
        cols['Value'] = {'type':'number'}
        self.error(self.compare([['A',100]], [['A',100.00001]], cols), 'VALUE_MISMATCH')

    def test_invalid_values_do_not_become_null(self):
        for kind, bad in [('number','oops'),('number','Infinity'),('date','2020-99-99'),('boolean','maybe')]:
            with self.subTest(kind=kind,bad=bad):
                self.error(self.compare([['A','']], [['A',bad]], {'ID':'text_exact','Value':kind}), 'TYPE_ERROR')

    def test_legacy_date_and_explicit_date(self):
        cols={'ID':'date','Value':'integer'}
        self.assertTrue(self.compare([['01/02/2020',1]], [['2020-02-01',1]], cols)['passed'])
        cols['ID']={'type':'date'}
        self.error(self.compare([['2020-02-01',1]], [['01/02/2020',1]], cols), 'TYPE_ERROR')
        cols['ID']={'type':'date','formats':['%Y-%m-%d','%d/%m/%Y']}
        self.assertTrue(self.compare([['2020-02-01',1]], [['01/02/2020',1]], cols)['passed'])
        cols['ID']['formats'].append('%m/%d/%Y')
        self.error(self.compare([['2020-02-01',1]], [['01/02/2020',1]], cols), 'TYPE_ERROR')

    def test_strict_text_null_and_leading_zero(self):
        cols={'ID':{'type':'text_exact'},'Value':'integer'}
        self.error(self.compare([['001',1]], [['1',1]], cols), 'KEY_MISMATCH')
        self.error(self.compare([['NA',1]], [['',1]], cols), 'KEY_MISMATCH')
        self.error(self.compare([['A',1]], [['a',1]], cols), 'KEY_MISMATCH')
        self.error(self.compare([['A',1]], [[' A ',1]], cols), 'KEY_MISMATCH')
        cols['ID']['null_values']=['','NA']
        self.assertTrue(self.compare([['NA',1]], [['',1]], cols)['passed'])

    def test_legacy_quoted_nulls_in_keys_and_values(self):
        for kind in ('text_exact', 'text_norm'):
            for raw in ("' NA '", '" null "', "'   '", "' NaN '", '" n/a "'):
                for key in (['ID'], ['ID', 'Value']):
                    with self.subTest(kind=kind, raw=raw, key=key):
                        cols = {'ID': 'text_exact', 'Value': kind}
                        for gt, cand in (([['A', '']], [['A', raw]]),
                                         ([['A', raw]], [['A', '']])):
                            r = self.compare(gt, cand, cols, key)
                            self.assertTrue(r['passed'], r)

    def test_legacy_non_null_quoted_text_preserves_rules(self):
        cols = {'ID': 'text_exact', 'Value': 'text_exact'}
        self.assertTrue(self.compare([['A', "' Alice '"]],
                                     [['A', '" Alice "']], cols)['passed'])
        self.error(self.compare([['A', "' Alice '"]], [['A', 'Alice']], cols),
                   'VALUE_MISMATCH')
        cols['Value'] = 'text_norm'
        self.assertTrue(self.compare([['A', "' Alice '"]],
                                     [['A', 'alice']], cols)['passed'])

    def test_object_null_tokens_remain_exact(self):
        for kind in ('text_exact', 'text_norm'):
            cols = {'ID': 'text_exact', 'Value': {'type': kind}}
            for raw in ("' NA '", '" null "', "'   '"):
                with self.subTest(kind=kind, raw=raw):
                    self.error(self.compare([['A', '']], [['A', raw]], cols),
                               'VALUE_MISMATCH')
            cols['Value']['null_values'] = ['', 'NA']
            self.assertTrue(self.compare([['A', '']], [['A', 'NA']], cols)['passed'])
            for raw in (' NA ', 'na', "' NA '"):
                self.error(self.compare([['A', '']], [['A', raw]], cols),
                           'VALUE_MISMATCH')

    def test_datetime_backend_formats_and_precision(self):
        cols = {'ID': 'text_exact', 'Value': {'type': 'datetime'}}
        gt = [['A', '2024-01-02 10:30:00']]
        for key in (['ID'], ['ID', 'Value']):
            for value in ('2024-01-02T10:30:00', '2024-01-02T10:30:00.000000',
                          '2024-01-02 10:30:00.000000', '2024-01-02 10:30',
                          '2024-01-02T10:30'):
                self.assertTrue(self.compare(gt, [['A', value]], cols, key)['passed'])
            code = 'VALUE_MISMATCH' if key == ['ID'] else 'KEY_MISMATCH'
            self.error(self.compare(gt, [['A', '2024-01-02T10:30:00.000001']], cols, key), code)
        self.error(self.compare(gt, [['A', '2024-01-02T10:30:00.000000001']], cols), 'TYPE_ERROR')
        self.error(self.compare(gt, [['A', '2024-01-02T10:30:00Z']], cols), 'TYPE_ERROR')
        cols['Value']['formats'] = ['%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S']
        self.assertTrue(self.compare(gt, [['A', '2024-01-02 10:30']], cols)['passed'])
        self.assertTrue(self.compare(gt, [['A', '2024-01-02T10:30:00']], cols)['passed'])

    def test_datetime_extra_formats_keys_order_and_ambiguity(self):
        cols = {'ID': {'type': 'datetime', 'formats': ['%d/%m/%Y %H:%M:%S']},
                'Value': 'integer'}
        gt = [['05/01/2020 21:31:00', 1], ['06/01/2020 00:00:00', 2]]
        cand = [['2020-01-05T21:31:00.000000', 1], ['2020-01-06 00:00', 2]]
        options = dict(ignore_order=False, order_by=[self.order('ID', 'asc')])
        self.assertTrue(self.compare(gt, cand, cols, **options)['passed'])
        self.assertTrue(self.compare(cand, gt, cols, **options)['passed'])
        self.error(self.compare(gt, list(reversed(cand)), cols, **options), 'ROW_ORDER_MISMATCH')
        # An ISO value must not win just because its format was tried first.
        cols['ID']['formats'] = ['%Y-%d-%m %H:%M:%S']
        self.error(self.compare([['2020-01-01 00:00:00', 1]],
                                [['2020-01-02 00:00:00', 1]], cols), 'TYPE_ERROR', 'candidate')
        cols['ID']['formats'] = ['%d/%m/%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S']
        self.error(self.compare([['2020-01-01 00:00:00', 1]],
                                [['01/02/2020 00:00:00', 1]], cols), 'TYPE_ERROR', 'candidate')
        self.assertTrue(self.compare([['2020-01-01 00:00:00', 1]],
                                     [['01/01/2020 00:00:00', 1]], cols)['passed'])
        cols['ID'] = 'datetime'
        self.assertTrue(self.compare([['05/01/2020 21:31:00', 1]], [cand[0]], cols)['passed'])

    def test_date_contract_and_error_sides(self):
        cols = {'ID': 'text_exact', 'Value': {'type': 'date'}}
        gt = [['A', '2024-01-02']]
        for key in (['ID'], ['ID', 'Value']):
            for value in ('2024-01-02 00:00:01', '2024-02-30',
                          '2024-01-02T00:00:00.000000001', '2024-01-02T00:00:00Z',
                          '2024-01-02T00:00:00+00:00'):
                self.error(self.compare(gt, [['A', value]], cols, key), 'TYPE_ERROR', 'candidate')
                self.error(self.compare([['A', value]], gt, cols, key), 'TYPE_ERROR', 'gt')
        cols['Value']['formats'] = ['%Y-%m-%d %H:%M:%S']
        self.error(self.compare(gt, gt, cols), 'CONFIG_ERROR')
        for fmt in ('%Y-%m-%d%z', '%Y-%m-%dZ', '%Y-%m-%d %Q'):
            cols['Value']['formats'] = [fmt]
            self.error(self.compare(gt, gt, cols), 'CONFIG_ERROR')

    def test_date_equivalent_representations(self):
        for rule in ('date', {'type': 'date', 'formats': ['%d/%m/%Y']}):
            cols = {'ID': 'text_exact', 'Value': rule}
            gt = [['A', '02/01/2024']]
            for key in (['ID'], ['ID', 'Value']):
                for value in ('2024-01-02', '2024-01-02 00:00:00',
                              '2024-01-02T00:00:00.000000000'):
                    self.assertTrue(self.compare(gt, [['A', value]], cols, key)['passed'])
                    self.assertTrue(self.compare([['A', value]], gt, cols, key)['passed'])
                code = 'VALUE_MISMATCH' if key == ['ID'] else 'KEY_MISMATCH'
                self.error(self.compare(gt, [['A', '2024-01-03 00:00:00']], cols, key), code)
        cols['Value'] = {'type': 'date', 'formats': ['%d/%m/%Y', '%m/%d/%Y']}
        self.error(self.compare([['A', '2024-01-02']], [['A', '02/01/2024']], cols), 'TYPE_ERROR')
        # Even an explicit alternative ISO-looking format cannot override ambiguity.
        cols['Value'] = {'type': 'date', 'formats': ['%Y-%d-%m']}
        self.error(self.compare([['A', '2024-01-02']], [['A', '2024-01-02']], cols), 'TYPE_ERROR', 'gt')
        cols['Value'] = {'type': 'date'}
        gt = [['A', '2024-01-02'], ['B', '2024-01-03']]
        cand = [['A', '2024-01-02T00:00:00'], ['B', '2024-01-03 00:00:00']]
        opts = {'ignore_order': False, 'order_by': [self.order(direction='asc')]}
        self.assertTrue(self.compare(gt, cand, cols, **opts)['passed'])
        self.error(self.compare(gt, cand[::-1], cols, **opts), 'ROW_ORDER_MISMATCH')

    def test_temporal_nulls_and_order(self):
        for kind in ('date', 'datetime'):
            cols = {'ID': 'text_exact', 'Value': {'type': kind, 'null_values': ['', 'NA', 'null']}}
            for key in (['ID'], ['ID', 'Value']):
                self.assertTrue(self.compare([['A', ' NA ']], [['A', ' Null ']], cols, key)['passed'])
            cols['Value']['null_values'] = []
            self.error(self.compare([['A', '']], [['A', '']], cols), 'TYPE_ERROR', 'gt')
        cols = {'ID': 'text_exact', 'Value': {'type': 'datetime'}}
        gt = [['A', '2024-01-02 10:00:00'], ['B', '2024-01-02 11:00:00']]
        cand = [['A', '2024-01-02T10:00:00.000000'], ['B', '2024-01-02T11:00:00.000000']]
        options = {'ignore_order': False, 'order_by': [self.order(direction='asc')]}
        self.assertTrue(self.compare(gt, cand, cols, **options)['passed'])
        self.error(self.compare(gt, cand[::-1], cols, **options), 'ROW_ORDER_MISMATCH')

    def test_key_vs_value_error(self):
        cols={'ID':'text_exact','Value':{'type':'number'}}
        self.error(self.compare([['A',100]], [['A',101]], cols), 'VALUE_MISMATCH')
        self.error(self.compare([['A',100]], [['A',101]], cols, ['ID','Value']), 'KEY_MISMATCH')

    def test_duplicate_and_ambiguous_keys(self):
        self.error(self.compare([['A',1],['A',2]], [['A',1],['B',2]]), 'GROUP_SIZE_MISMATCH')
        self.error(self.compare([['A',1],['B',2]], [['A',1],['A',2]]), 'KEY_MISMATCH')
        self.assertTrue(self.compare([['A',1],['A',2]], [['A',2],['A',1]])['passed'])
        self.error(self.compare([['A',1],['A',2]], [['A',1],['A',3]]), 'VALUE_MISMATCH')
        self.assertTrue(self.compare([['A',1],['A',1]], [['A',1],['A',1]])['passed'])
        self.assertTrue(self.compare([['A',1],['B',2]], [['B',2],['A',1]])['passed'])
        full = {'ID': 'text_exact', 'Value': 'integer'}
        self.assertTrue(self.compare([['A',1],['A',1]], [['A',1],['A',1]], full,
                                     key=['ID', 'Value'])['passed'])
        cols={'ID':{'type':'number','abs_tol':2}}
        r=self.compare([[100],[200]], [[99],[101]], cols)
        self.error(r,'KEY_MISMATCH')
        self.assertEqual(r['errors'][0]['detail']['reason'],'multiple_matches')
        r=self.compare([[100],[101]], [[100.5],[300]], cols)
        self.error(r,'KEY_MISMATCH')
        self.assertEqual(r['errors'][0]['detail']['reason'],'competing_matches')

    def test_exact_matches_reserved_before_tolerant_matching(self):
        cols={'ID':{'type':'number','abs_tol':2}}
        for gt in ([[100],[101]], [[101],[100]]):
            for cand in ([[101],[99]], [[99],[101]]):
                self.assertTrue(self.compare(gt,cand,cols)['passed'])

    def test_order_ties_and_inversion(self):
        gt=[['A',100],['B',100],['C',90]]
        self.assertTrue(self.compare(gt,[gt[1],gt[0],gt[2]], ignore_order=False, order_by=[self.order()])['passed'])
        r=self.compare(gt,[gt[0],gt[2],gt[1]], ignore_order=False, order_by=[self.order()])
        self.error(r,'ROW_ORDER_MISMATCH','candidate')
        self.assertEqual(r['files']['out.csv']['content_status'],'passed')
        self.error(self.compare(gt,[gt[1],gt[0],gt[2]],ignore_order=False,
                               order_by=[self.order(),self.order('ID','asc')]),'ROW_ORDER_MISMATCH')

    def test_tolerance_does_not_create_sort_ties(self):
        cols={'ID':'text_exact','Value':'number'}
        self.error(self.compare([['A',100],['B',100]], [['A',100],['B',100.01]],cols,
                                ignore_order=False,order_by=[self.order()]),'ROW_ORDER_MISMATCH')

    def test_gt_sort_errors_and_null_placement(self):
        gt=[['A',1],['B',2]]
        self.error(self.compare(gt,gt,ignore_order=False,order_by=[self.order()]),'GT_ORDER_ERROR','gt')
        for direction in ['asc','desc']:
            for nulls in ['first','last']:
                gt=[['A',''],['B',1]] if nulls=='first' else [['B',1],['A','']]
                self.assertTrue(self.compare(gt,gt,ignore_order=False,order_by=[self.order(direction=direction,nulls=nulls)])['passed'])

    def test_date_order_uses_chronology(self):
        cols={'ID':'text_exact','Value':'date'}
        gt=[['A','01/02/2018'],['B','01/01/2019']]
        self.assertTrue(self.compare(gt,gt,cols,ignore_order=False,order_by=[self.order(direction='asc')])['passed'])

    def test_time_semantics_keys_and_order(self):
        cols = {'ID': {'type': 'time'}, 'Value': 'integer'}
        gt = [['7:19', 1], ['12:40:00.123', 2]]
        cand = [['07:19:00', 1], ['12:40:00.123000', 2]]
        options = dict(ignore_order=False, order_by=[self.order('ID', 'asc')])
        self.assertTrue(self.compare(gt, cand, cols, **options)['passed'])
        self.error(self.compare(gt, list(reversed(cand)), cols, **options), 'ROW_ORDER_MISMATCH')
        self.error(self.compare(gt, [['07:19:01', 1], cand[1]], cols), 'KEY_MISMATCH')

    def test_time_values_formats_and_invalid_inputs(self):
        for rule in ['time', {'type': 'time'}]:
            cols = {'ID': 'text_exact', 'Value': rule}
            self.assertTrue(self.compare([['A', '0:40']], [['A', '00:40:00']], cols)['passed'])
            self.error(self.compare([['A', '07:19']], [['A', '07:19:00.000001']], cols), 'VALUE_MISMATCH')
            self.assertTrue(self.compare([['A', '']], [['A', ' ']], cols)['passed'])
            for bad in ['24:00', '07:60', '07:19:60', '2020-01-01 07:19', '07:19+08:00', 'NA']:
                self.error(self.compare([['A', '07:19']], [['A', bad]], cols), 'TYPE_ERROR')
        cols['Value'] = {'type': 'time', 'formats': ['%I:%M %p']}
        self.assertTrue(self.compare([['A', '7:19 PM']], [['A', '07:19 PM']], cols)['passed'])
        self.error(self.compare([['A', '7:19 PM']], [['A', '19:19']], cols), 'TYPE_ERROR')
        for fmt in ['%Y-%m-%d %H:%M', '%H:%M%z', '%H:%M UTC']:
            cols['Value'] = {'type': 'time', 'formats': [fmt]}
            self.error(self.compare([['A', '07:19']], [['A', '07:19']], cols), 'CONFIG_ERROR')

    def test_config_validation(self):
        for options in [{'ignore_order':False},{'ignore_order':'false'},
                        {'order_by':[self.order()]},
                        {'ignore_order':False,'order_by':[{'column':'Value','direction':'asc'}]},
                        {'ignore_order':False,'order_by':[self.order('Missing')]}]:
            self.error(self.compare([['A',1]],[['A',1]],**options),'CONFIG_ERROR','config')
        for rule in [{'type':'number','rel_tol':-1},{'type':'number','abs_tol':True},
                     {'type':'integer','rel_tol':0.01},{'type':[]},'id',{'type':'date','formats':[]}]:
            self.error(self.compare([['A',1]],[['A',1]],{'ID':'text_exact','Value':rule}),'CONFIG_ERROR')

    def test_file_schema_and_rows(self):
        self.compare([['A',1]],[['A',1]])
        self.write(self.cand,['ID'],[['A']])
        self.error(self.run_eval(),'MISSING_COLUMNS','candidate')
        self.write(self.cand,['ID','Value'],[['A',1],['B',2]])
        self.error(self.run_eval(),'ROW_COUNT_MISMATCH')
        self.write(self.cand,['Extra','Value','ID'],[['ignored',1,'A']])
        self.assertTrue(self.run_eval()['passed'])
        (self.cand/'out.csv').rename(self.cand/'wrong.csv')
        self.error(self.run_eval(),'MISSING_FILE')
        (self.cand/'wrong.csv').unlink()
        self.error(self.run_eval(),'FILE_COUNT_MISMATCH')

    def test_empty_tables_and_malformed_csv(self):
        self.assertTrue(self.compare([],[])['passed'])
        (self.cand/'out.csv').write_text('ID,Value\nA,1,extra\n')
        self.error(self.run_eval(),'READ_ERROR')

    def test_cli_report_and_exit_codes(self):
        self.compare([['A',1]],[['A',1]])
        report=self.root/'report.json'
        cmd=[sys.executable,'-m','evaluation','--gt-dir',str(self.gt),'--cand-dir',str(self.cand),
             '--config',str(self.config),'--report',str(report)]
        p=subprocess.run(cmd,capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertTrue(json.loads(report.read_text())['passed'])
        self.write(self.cand,['ID','Value'],[['A',2]])
        self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,1)


class CuratedAssets(unittest.TestCase):
    def test_six_cases_self_and_reversed_rows(self):
        root=Path(__file__).resolve().parents[2]/'PrepBench'
        cases = sorted(root.glob('case_00[1-6]'))
        self.assertEqual(len(cases), 6)
        for case in cases:
            with self.subTest(case=case.name), tempfile.TemporaryDirectory() as tmp:
                gt=case/'evaluation/gt'
                config=case/'evaluation/config.json'
                self.assertTrue(Evaluator(gt,gt,config).run()['passed'])
                for source in gt.glob('*.csv'):
                    with source.open(newline='') as f:
                        rows=list(csv.reader(f))
                    with (Path(tmp)/source.name).open('w',newline='') as f:
                        csv.writer(f).writerows([rows[0],*reversed(rows[1:])])
                result=Evaluator(gt,tmp,config).run()
                self.assertTrue(result['passed'],result)


if __name__ == '__main__':
    unittest.main()
