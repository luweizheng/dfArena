import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from evaluation import Evaluator
from evaluation.csv_compat import compatible_rows


class CSVCompatibilityTests(unittest.TestCase):
    def test_standard_preserves_literal_backslashes(self):
        rows = [['ID', 'Name'], ['1', r'C:\data\new'], ['2', r'literal \" text']]
        out = io.StringIO(newline='');csv.writer(out).writerows(rows)
        parsed, dialect = compatible_rows(out.getvalue())
        self.assertEqual(parsed, rows)
        self.assertEqual(dialect, 'standard')

    def test_backslash_quotes_commas_newlines_and_paths(self):
        # Quoted-field backslashes are doubled by this dialect's writer;
        # unquoted paths stay literal, including backslash+n, not a newline.
        text = 'ID,Name\n1,"\\"Movie\\", part\nTwo"\n2,C:\\new\\file\n3,"C:\\\\path \\"quoted\\""\n'
        parsed, dialect = compatible_rows(text)
        self.assertEqual(dialect, 'backslash')
        self.assertEqual(parsed, [['ID','Name'],['1','"Movie", part\nTwo'],['2',r'C:\new\file'],['3','C:\\path "quoted"']])

    def test_malformed_documents_are_not_repaired(self):
        for text in ['ID,Name\n1,"unfinished', 'ID,Name\n1,"\\"Movie\\""garbage\n',
                     'ID,Name\n1,"\\"Movie\\"\n', 'ID,Name\n1,"a"b\n']:
            with self.subTest(text=text), self.assertRaises(csv.Error):compatible_rows(text)

    def test_evaluation_opt_in_and_content_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);gt=p/'gt';cand=p/'cand';gt.mkdir();cand.mkdir()
            with (gt/'a.csv').open('w',newline='') as f:csv.writer(f).writerows([['ID','Name'],['1','"Movie"']])
            raw='ID,Name\n1,"\\"Movie\\""\n'
            (cand/'a.csv').write_text(raw)
            cfg={'files':{'a.csv':{'key':['ID'],'columns':{'ID':{'type':'integer'},'Name':{'type':'text_exact'}}}}}
            cp=p/'config.json'
            def run():
                cp.write_text(json.dumps(cfg));return Evaluator(gt,cand,cp).run()
            self.assertEqual(run()['errors'][0]['error_type'],'READ_ERROR')
            cfg['files']['a.csv']['csv_quoting']='standard_or_backslash'
            r=run();self.assertTrue(r['passed'],r);self.assertEqual(r['protocol_version'],'dfarena-table-v9')
            self.assertEqual(r['files']['a.csv']['csv_dialects']['candidate'],'backslash')
            self.assertEqual((cand/'a.csv').read_text(),raw)
            for bad in [raw.replace('Movie','Wrong'),raw+'2,Extra\n',raw.replace('1,','2,'),raw.replace('1,','1,extra,')]:
                (cand/'a.csv').write_text(bad);self.assertFalse(run()['passed'])
            cfg['files']['a.csv']['csv_quoting']='guess'
            self.assertEqual(run()['errors'][0]['error_type'],'CONFIG_ERROR')

if __name__=='__main__':unittest.main()
