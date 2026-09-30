"""CVE task 2 tie acceptance and protection against substring false positives."""
import importlib.util
from pathlib import Path
import unittest


path = Path(__file__).resolve().parents[2] / "cve/tasks/task2/validate.py"
spec = importlib.util.spec_from_file_location("cve_task2_validator", path)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class VendorValidationTests(unittest.TestCase):
    def test_either_tied_vendor(self):
        for answer in ["fortinet", "ivanti", "Fortinet", "IVANTI", " fortinet\n", "\tivanti "]:
            with self.subTest(answer=answer):
                self.assertTrue(validator.validate(answer)[0])

    def test_wrong_missing_or_multiple_answers(self):
        for answer in ["", " \n", "cisco", "microsoft", "notfortinet", "ivanti_extra",
                       "not ivanti", "fortinet or cisco", "ivanti, microsoft",
                       "fortinet, ivanti", None, 4, ["ivanti"]]:
            with self.subTest(answer=answer):
                self.assertFalse(validator.validate(answer)[0])


if __name__ == "__main__":
    unittest.main()
