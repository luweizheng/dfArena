"""Empty-result representations, polarity, contradictions and retained failures."""
import importlib.util
import os
from pathlib import Path
import unittest

path = Path(os.environ.get('CIVIC_TASK3_VALIDATOR_PATH', str(
    Path(__file__).resolve().parents[2] / 'civic_unstructured/tasks/task3/validate.py')))
spec = importlib.util.spec_from_file_location('civic_task3_validator', path)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class CivicEmptySourcesTests(unittest.TestCase):
    def check(self, answer, expected):
        passed, message = validator.validate(answer)
        self.assertIs(passed, expected, message)

    def test_empty_formats(self):
        for answer in ['[]', '[ ]', '{}', '∅', 'set()', 'None.', 'No funding sources qualify.',
                       'No funding source qualifies.', 'No qualifying funding sources.',
                       'There are no eligible funding sources.', 'None of the funding sources qualify.',
                       'No funding sources meet the criteria.', 'The result is empty.',
                       'The answer is an empty set.', 'Zero qualifying funding sources.',
                       'No funding sources qualify; the answer is an empty set.',
                       '**No funding sources qualify.**', '```json\n[]\n```',
                       'As of 2022-08-01, no funding sources qualify.',
                       'No funding sources qualify as of 2022-08-01.',
                       '| Funding source |\n|---|\n| None |']:
            with self.subTest(answer=answer):
                self.check(answer, True)

    def test_explicit_explanations(self):
        for explanation in ['Municipal Fund does not qualify.',
                            'In particular, Municipal Fund does not qualify.',
                            'Municipal Fund is excluded because its completed-project share is 23.08%.',
                            'Municipal Fund and County Grant do not qualify.',
                            'Excluded funding sources: Municipal Fund, County Grant.',
                            'Excluded sources:\n- Municipal Fund\n- County Grant']:
            with self.subTest(explanation=explanation):
                self.check('No funding sources qualify.\n' + explanation, True)

    def test_nonempty_selections(self):
        for answer in ['Municipal Fund', 'County Grant; Municipal Fund; Public-Private Partnership.',
                       '["Municipal Fund"]', 'Imaginary Fund', 'Public_Private_Partnership',
                       'One funding source qualifies: Municipal Fund.']:
            with self.subTest(answer=answer):
                self.check(answer, False)

    def test_contradictions_and_exceptions(self):
        for answer in ['No funding sources qualify. Municipal Fund qualifies.',
                       '[]\nMunicipal Fund', 'None, except Municipal Fund.',
                       'No funding sources qualify except County Grant.',
                       'No funding sources qualify. Imaginary Fund qualifies.',
                       'No funding sources qualify. Municipal Fund does not qualify, but County Grant qualifies.',
                       'No funding sources qualify. County Grant qualifies and Municipal Fund does not qualify.',
                       'No funding sources qualify. Municipal Fund does not qualify because County Grant qualifies.',
                       'Excluded sources: Municipal Fund, also include County Grant.\nNone.']:
            with self.subTest(answer=answer):
                self.check(answer, False)

    def test_no_broad_empty_keyword_matching(self):
        for answer in ['The answer is not empty.', 'None of the sources are ineligible.',
                       'There are no errors; Municipal Fund qualifies.',
                       'The completed project count is zero.', 'I have no answer.',
                       'No funding sources were excluded.', 'Zero', 'null', '[null]', '',
                       'Municipal Fund does not qualify.']:
            with self.subTest(answer=answer):
                self.check(answer, False)

    def test_explicit_25_percent_empty_results(self):
        for answer in [
            'No funding sources meet the 25% threshold.',
            'No funding sources meet the 25% completed-project threshold as of 2022-08-01.',
            'No funding sources meet the 25% threshold as of 2022-08-01.',
            'As of 2022-08-01, no funding sources meet the 25% threshold.',
            'No funding sources meet the 25 percent threshold.',
            'No funding source meets the 25% threshold.',
            'No sources satisfy the 25% cutoff.',
            '**No funding sources meet the 25% threshold.**',
            'The answer is No funding sources meet the 25% threshold.',
            'No funding sources meet the 25% threshold. Municipal Fund does not qualify.',
        ]:
            with self.subTest(answer=answer):
                self.check(answer, True)

    def test_threshold_claim_does_not_hide_wrong_answers(self):
        for answer in [
            'No funding sources meet the 50% threshold.',
            'No funding sources meet the 20% threshold.',
            'No funding sources meet the 125% threshold.',
            'No funding sources meet the 25% threshold except Municipal Fund.',
            'No funding sources meet the 25% threshold. Municipal Fund qualifies.',
            'No funding sources meet the 25% threshold; County Grant',
            'No funding sources meet the 25% threshold, but County Grant qualifies.',
            'No funding sources meet the 25% threshold and Municipal Fund qualifies.',
            'Some funding sources meet the 25% threshold.',
            'It is not true that no funding sources meet the 25% threshold.',
            'No funding sources fail to meet the 25% threshold.',
        ]:
            with self.subTest(answer=answer):
                self.check(answer, False)

    def test_all_eight_sources_explicitly_excluded(self):
        sources = ['Public-Private Partnership', 'Municipal Fund', 'Municipal Bond',
                   'Emergency Relief Fund', 'Private Donation', 'County Grant',
                   'State Grant', 'Federal Grant']
        self.check('\n'.join(s + ' does not qualify.' for s in sources), True)


if __name__ == '__main__':
    unittest.main()
