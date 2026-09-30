"""Regression checks for equivalent answer formats and misleading units."""
import importlib.util
from pathlib import Path
import unittest


path = Path(__file__).resolve().parents[2] / 'GITHUB_REPOS/tasks/task1/validate.py'
spec = importlib.util.spec_from_file_location('github_task1_validator', path)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class ProportionValidationTests(unittest.TestCase):
    def test_equivalent_formats(self):
        for answer in ['0.3333333333333333', '0.33', '.3333', '33.33%',
                       '33.33 percent', '1/3', '1 / 3', 'The proportion is 0.33.',
                       '33.33% (1 of 3 README.md files with available contents).']:
            with self.subTest(answer=answer):
                self.assertTrue(validator.validate(answer)[0])

    def test_incorrect_or_incomplete_values(self):
        for answer in ['0.33%', '0.33 percent', '33.33', '33', '-0.33',
                       '25%', '1/4', '1/0', '0.33/2', '3 README files', 'unknown']:
            with self.subTest(answer=answer):
                self.assertFalse(validator.validate(answer)[0])


if __name__ == '__main__':
    unittest.main()
