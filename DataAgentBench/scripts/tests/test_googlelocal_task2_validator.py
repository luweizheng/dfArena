"""Numeric-equivalence and wrong-score regression checks."""
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[2] / 'googlelocal/tasks/task2/answer/validate.py'
spec = importlib.util.spec_from_file_location('googlelocal_task2_validator', path)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

def answer(elite='5', angel='4.33', aurora='4.18', oriental='4.17'):
    return f'Elite Massage: {elite}\nAngel-A Massage: {angel}\nAurora Massage: {aurora}\nJ B Oriental Inc: {oriental}'

class RatingTests(unittest.TestCase):
    def test_equivalent_five(self):
        for score in ['5', '5.0', '5.00', '5.000', '+5', '+5.0', '5.', '5.0.']:
            with self.subTest(score=score):
                self.assertTrue(validator.validate(answer(elite=score))[0])

    def test_two_decimal_rule_preserved(self):
        for scores in [('4.33','4.18','4.17'), ('4.333333','4.178571','4.166667'), ('4.334','4.179','4.169')]:
            with self.subTest(scores=scores):
                self.assertTrue(validator.validate(answer('5',*scores))[0])
        for scores in [('4.34','4.18','4.17'), ('4.33','4.17','4.17'), ('4.33','4.18','4.16')]:
            with self.subTest(scores=scores):
                self.assertFalse(validator.validate(answer('5',*scores))[0])

    def test_wrong_or_missing_scores(self):
        for score in ['4', '4.9', '5.1', '-5', '-5.0', '15', '50', 'unknown', '']:
            with self.subTest(score=score):
                self.assertFalse(validator.validate(answer(elite=score))[0])
        self.assertFalse(validator.validate(answer().replace('Elite Massage','Other Massage'))[0])

if __name__ == '__main__':
    unittest.main()
