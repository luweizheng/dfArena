import json
import re
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data/recipients_db/recipients.parquet')
OUT = Path('/workspace/work')
# Remove suffixes only at the end, including their separating comma.
# Punctuation within the remaining recipient name is preserved.
SUFFIX = re.compile(
    r'[\s,]+(?:incorporated|inc\.?|corporation|corp\.?|limited|ltd\.?|'
    r'company|co\.?|l\.?l\.?c\.?|l\.?l\.?p\.?|l\.?p\.?|p\.?c\.?|l\.?c\.?)$',
    re.IGNORECASE,
)

def normalize_name(value):
    if pd.isna(value):
        return pd.NA
    value = value.strip().casefold()
    while SUFFIX.search(value):
        value = SUFFIX.sub('', value).strip()
    return value

def main():
    recipients = pd.read_parquet(DATA, columns=['name', 'uei'])
    recipients['recipient'] = recipients['name'].map(normalize_name)
    # The observed UEI formats are bare identifiers, uei:<id>, and <id>-uei.
    recipients['canonical_uei'] = (recipients['uei'].str.strip().str.upper()
        .str.replace(r'^UEI:', '', regex=True)
        .str.replace(r'-UEI$', '', regex=True))
    assert recipients['canonical_uei'].str.fullmatch(r'[A-Z0-9]{12}').all()
    counts = recipients.groupby('recipient')['canonical_uei'].nunique()
    multiple = counts[counts.gt(1)]
    multiple.rename('distinct_uei_count').to_csv(OUT / 'recipients_with_multiple_ueis.csv')
    answer = {'answer': str(int(multiple.size))}
    (OUT / 'answer.json').write_text(json.dumps(answer) + '\n')
    print(json.dumps(answer))

if __name__ == '__main__':
    main()
