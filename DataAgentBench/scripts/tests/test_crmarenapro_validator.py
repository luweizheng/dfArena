"""CRM task 2 policy alternatives and protection against accidental matches."""
import importlib.util
from pathlib import Path
import unittest


path = Path(__file__).resolve().parents[2] / 'crmarenapro/tasks/task2/validate.py'
spec = importlib.util.spec_from_file_location('crm_task2_validator', path)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class PolicyValidationTests(unittest.TestCase):
    def test_either_policy_or_both(self):
        a, b = 'ka0Wt000000Eq0MIAS', 'ka0Wt000000Ens5IAC'
        for answer in [a, b, '  ' + a + '\n', a + ', ' + b, b + '\n' + a,
                       f'["{a}", "{b}"]', f'`{a}`; `{b}`', a + ' and ' + b,
                       f'Article: {b}.', a + ', ' + a]:
            with self.subTest(answer=answer):
                self.assertTrue(validator.validate(answer)[0])

    def test_wrong_missing_malformed_and_mixed_ids(self):
        a, b, wrong = 'ka0Wt000000Eq0MIAS', 'ka0Wt000000Ens5IAC', 'ka0Wt000000Abc1IAC'
        for answer in ['', 'None', 'No violation', wrong, a + ', ' + wrong,
                       a + ', ' + b + ', ' + wrong, a.lower(), b.upper(),
                       a[:-1], a + 'X', 'X' + a, '_' + a, a + '_extra',
                       b + ', ka0', a + ', ' + b[:-1], None, [a, b], 42]:
            with self.subTest(answer=answer):
                self.assertFalse(validator.validate(answer)[0])


if __name__ == '__main__':
    unittest.main()
