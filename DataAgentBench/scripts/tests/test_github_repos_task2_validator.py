"""Exact short answers must pass; preserve the upstream fuzzy fallback."""
import importlib.util
from pathlib import Path
import sys
import unittest

path = Path(__file__).resolve().parents[2] / 'GITHUB_REPOS/tasks/task2/answer/validate.py'
sys.path.insert(0, str(path.parent))
spec = importlib.util.spec_from_file_location('github_task2_validator', path)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class RepositoryValidationTests(unittest.TestCase):
    def test_exact_name_and_presentations(self):
        for answer in ['SwiftAndroid/swift', 'swiftandroid/SWIFT',
                       '  SwiftAndroid/swift  ', '`SwiftAndroid/swift`',
                       '**SwiftAndroid/swift**', 'SwiftAndroid/swift.',
                       'The answer is SwiftAndroid/swift.',
                       '| Repository |\n|---|\n| SwiftAndroid/swift |']:
            with self.subTest(answer=answer):
                self.assertTrue(validator.validate(answer)[0])

    def test_existing_fuzzy_acceptance(self):
        # Each candidate has the old fixed window length and distance <= 3.
        for answer in ['SwiftAndroid/swiftXYZ', 'abcSwiftAndroid/swift',
                       'SwiftXAndroid/swiftYZ']:
            with self.subTest(answer=answer):
                self.assertTrue(validator.validate(answer)[0])

    def test_wrong_or_missing_repository(self):
        for answer in ['', 'unknown', 'swift', 'SwiftAndroid',
                       'apple/swift', 'OtherOwner/other-repo',
                       'The answer is apple/swift.', 'xxxxxxxxxxxxxxxxxxxx']:
            with self.subTest(answer=answer):
                self.assertFalse(validator.validate(answer)[0])


if __name__ == '__main__':
    unittest.main()
