import unittest
import tempfile,csv,json
from pathlib import Path
from evaluation import Evaluator
from evaluation.config import column_rule, ConfigError
from evaluation.normalization import normalize

class UTCDatetimeTests(unittest.TestCase):
    def test_key_alignment_and_protocol(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);gt=p/'gt';cand=p/'cand';gt.mkdir();cand.mkdir()
            def put(folder,stamp):
                with (folder/'output.csv').open('w',newline='') as f:
                    csv.writer(f).writerows([['timestamp','value'],[stamp,'2']])
            put(gt,'05/01/2021 21:44:55');put(cand,'2021-01-06T05:44:55+08:00')
            cfg={'files':{'output.csv':{'key':['timestamp'],'ignore_order':True,'columns':{'timestamp':{'type':'datetime','formats':['%d/%m/%Y %H:%M:%S'],'assume_timezone':'UTC'},'value':{'type':'integer'}}}}}
            cp=p/'config.json';cp.write_text(json.dumps(cfg))
            report=Evaluator(gt,cand,cp).run();self.assertTrue(report['passed'],report);self.assertEqual(report['protocol_version'],'dfarena-table-v8')
            put(cand,'2021-01-06T05:44:55+00:00');self.assertFalse(Evaluator(gt,cand,cp).run()['passed'])

    def test_equivalent_instants_and_naive_utc(self):
        rule=column_rule({'type':'datetime','assume_timezone':'UTC','formats':['%d/%m/%Y %H:%M:%S']})
        base=normalize('05/01/2021 21:44:55',rule)
        for s in ['2021-01-05T21:44:55Z','2021-01-05T21:44:55+00:00',
                  '2021-01-06T05:44:55+08:00','2021-01-05T16:44:55-05:00',
                  '2021-01-05 21:44:55.000000','2021-01-05T21:44:55']:
            with self.subTest(s=s):self.assertEqual(base,normalize(s,rule))
        for s in ['2021-01-05T21:44:55+08:00','2021-01-05T21:44:56Z','2021-01-05T21:44:55.000001Z']:
            with self.subTest(s=s):self.assertNotEqual(base,normalize(s,rule))

    def test_default_rejects_timezone(self):
        for rule in [column_rule({'type':'datetime'}),column_rule('datetime')]:
            with self.assertRaises(ValueError):normalize('2021-01-05T21:44:55Z',rule)

    def test_invalid_aware_values_rejected(self):
        rule=column_rule({'type':'datetime','assume_timezone':'UTC'})
        for s in ['2021-02-30T00:00:00Z','2021-01-01T00:00:00.0000001Z',
                  '2021-01-01T00:00:00-00:00','2021-01-01T00:00:00+24:00',
                  '2021-01-01T00:00:00+01:99','2021-01-01T00:00:00UTC',
                  '2021-01-01T00:00:00+0100','2021-01-01Z']:
            with self.subTest(s=s),self.assertRaises(ValueError):normalize(s,rule)

    def test_invalid_configuration_rejected(self):
        for kind,value in [('date','UTC'),('time','UTC'),('number','UTC'),('datetime','Europe/London'),('datetime',None),('datetime',True)]:
            with self.subTest(kind=kind,value=value),self.assertRaises(ConfigError):column_rule({'type':kind,'assume_timezone':value})

if __name__=='__main__':unittest.main()
