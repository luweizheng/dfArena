"""Check project-set equality, equivalent list formats, and exclusion scope."""
import importlib.util
import os
from pathlib import Path
import unittest

path = Path(os.environ.get('CIVIC_VALIDATOR_PATH', str(
    Path(__file__).resolve().parents[2] / 'civic_unstructured/tasks/task1/validate.py')))
spec = importlib.util.spec_from_file_location('civic_task1_validator', path)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

PROJECTS = [
    'Annual Street Maintenance',
    'Civic Center Water Treatment Facility Phase 2',
    'Marie Canyon Green Streets',
    'Michael Landon Center Roof Replacement Project',
    'PCH Median Improvements Project',
    'PCH Signal Synchronization System Improvements Project',
    'PCH at Trancas Canyon Road Right Turn Lane',
    'Permanent Skate Park',
    'Westward Beach Road Repair Project',
]


class CivicProjectListTests(unittest.TestCase):
    def check(self, answer, expected):
        ok, reason = validator.validate(answer)
        self.assertIs(ok, expected, reason)

    def test_supported_formats(self):
        import json
        aliases = list(PROJECTS)
        aliases[0] = '2022 Annual Street Maintenance'
        aliases[3] = 'Malibu Bluffs Park Roof Replacement Project'
        aliases[-1] = 'Westward Beach Road Improvements Project'
        variants = [
            '\n'.join(PROJECTS),
            '; '.join(reversed(PROJECTS)),
            ', '.join(PROJECTS[:-1]) + ', and ' + PROJECTS[-1],
            '\n'.join(f'{i}. {p}' for i, p in enumerate(PROJECTS, 1)),
            '\n'.join(f'- **{p}**' for p in PROJECTS),
            '\n'.join(aliases),
            '\n'.join(PROJECTS + [PROJECTS[0]]),
            'The qualifying projects are: ' + '; '.join(PROJECTS),
            '\n'.join(f'{p} ($1,340,000)' for p in PROJECTS),
            '\n'.join(f'{p} — $1,340,000 USD' for p in PROJECTS),
            '| Project | Total funding (USD) | Type | Status |\n|---|---:|---|---|\n' +
            '\n'.join(f'| **{p}** | $1,340,000 | capital | design |' for p in PROJECTS),
            json.dumps(PROJECTS),
            '```json\n' + json.dumps(PROJECTS) + '\n```',
            '\n'.join(PROJECTS).lower().replace(' ', '_'),
        ]
        for answer in variants:
            with self.subTest(answer=answer):
                self.check(answer, True)

    def test_missing_and_extra(self):
        for i in range(len(PROJECTS)):
            with self.subTest(missing=i):
                self.check('\n'.join(PROJECTS[:i] + PROJECTS[i+1:]), False)
        for extra in ['Corral Canyon Culvert Repairs', 'Imaginary Test Project',
                      'Moonlight Plaza', 'Permanent Skate Park Extension']:
            for separator in ['\n', '; ', ', and ']:
                with self.subTest(extra=extra, separator=separator):
                    self.check('\n'.join(PROJECTS) + separator + extra, False)

    def test_unknown_table_row(self):
        text = '| Project | Funding |\n|---|---|\n' + '\n'.join(
            f'| {p} | $1,000,000 |' for p in PROJECTS + ['Imaginary Test Project'])
        self.check(text, False)

    def test_explanatory_exclusion(self):
        base = '\n'.join(PROJECTS)
        for explanation in [
            'Corral Canyon Culvert Repairs does not qualify.',
            'Corral Canyon Culvert Repairs is excluded because its status is completed.',
            'Excluded: Corral Canyon Culvert Repairs.',
            'Excluded projects:\n- Corral Canyon Culvert Repairs\n- Imaginary Test Project',
            'No other projects qualify.',
        ]:
            with self.subTest(explanation=explanation):
                self.check(base + '\n' + explanation, True)

    def test_excluded_correct_project_cannot_satisfy_missing(self):
        base = '\n'.join(PROJECTS[:-1])
        self.check(base + '\n' + PROJECTS[-1] + ' does not qualify.', False)
        self.check(base + '\nExcluded: ' + PROJECTS[-1], False)

    def test_conflicting_assertions(self):
        self.check('\n'.join(PROJECTS) + '\nPermanent Skate Park is excluded.', False)

    def test_mixed_polarity(self):
        base = '\n'.join(PROJECTS[:-1])
        self.check(base + '\nCorral Canyon Culvert Repairs does not qualify, but '
                   'Westward Beach Road Repair Project qualifies.', True)
        self.check('\n'.join(PROJECTS) + '\nCorral Canyon Culvert Repairs does not qualify, but '
                   'Imaginary Test Project qualifies.', False)
        self.check('\n'.join(PROJECTS) + '\nImaginary Test Project qualifies and '
                   'Corral Canyon Culvert Repairs does not qualify.', False)
        self.check('\n'.join(PROJECTS) + '\nExcluded: Corral Canyon Culvert Repairs, '
                   'also include Imaginary Test Project.', False)

    def test_unrecognized_prose_is_not_silently_ignored(self):
        self.check('\n'.join(PROJECTS) + '\nAlso include Moonlight Plaza.', False)

    def test_empty_or_invalid(self):
        for text in ['', '[]', 'No projects qualify.', '[1, 2]', '[broken list']:
            with self.subTest(text=text):
                self.check(text, False)


if __name__ == '__main__':
    unittest.main()
