"""Formatting equivalence, complete numeric tokens and incorrect values."""
import importlib.util
from pathlib import Path
import unittest
path=Path(__file__).resolve().parents[2]/'PANCANCER_ATLAS/tasks/task1/validate.py'
spec=importlib.util.spec_from_file_location('pancancer_task1_validator',path)
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
CODES=['9382/3','9400/3','9401/3','9450/3','9451/3']
VALUES=['2.7136','2.6014','2.5584','2.6967','2.5826']
def answer(values=VALUES,style='{c}: {n}'):
    return '\n'.join(style.format(c=c,n=n) for c,n in zip(CODES,values))
class HistologyScoresTests(unittest.TestCase):
    def test_presentations(self):
        for style in ['{c}: {n}','| {c} | {n} |','| **{c}** | **{n}** |',
                      '| `{c}` | `{n}` |','**{c}**: **{n}**','__{c}__: __{n}__',
                      '- {c}: {n}','{c}: mean {n}','{c}: {n}.']:
            with self.subTest(style=style):self.assertTrue(v.validate(answer(style=style))[0])
    def test_full_precision_and_scientific(self):
        self.assertTrue(v.validate(answer(['2.713571305193452','2.6014163319762287','2.558390345072906','2.6967184429497295','2.5826348457075095']))[0])
        self.assertTrue(v.validate(answer(['2.7136e0','2.6014e0','2.5584e0','2.6967e0','2.5826e0']))[0])
        self.assertTrue(v.validate(answer(style='| **{c}** | **{n}000000** |'))[0])
    def test_wrong_values_and_signs(self):
        for i in range(5):
            values=list(VALUES);values[i]='1.0000'
            with self.subTest(code=CODES[i]):self.assertFalse(v.validate(answer(values))[0])
        for n in ['-2.7136','2.7134','2.71366','27.136','unknown','']:
            with self.subTest(value=n):self.assertFalse(v.validate(answer([n]+VALUES[1:]))[0])
    def test_missing_and_mismatched_codes(self):
        self.assertFalse(v.validate(answer().replace('9382/3','9999/3'))[0])
        self.assertFalse(v.validate(answer(VALUES[1:]+VALUES[:1]))[0])
        self.assertFalse(v.validate(answer().replace('9382/3: 2.7136','9382/3:'))[0])
if __name__=='__main__':unittest.main()
