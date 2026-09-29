from pathlib import Path
import json
import polars as pl

INPUT = Path('/workspace/data/recipients_db/recipients.parquet')
OUTPUT = Path('/workspace/work')

# Remove corporate suffixes and their adjoining separators only. Punctuation
# within the remaining recipient name is deliberately preserved.
SUFFIX = (
    r'(?:[\s,]+(?:INCORPORATED|INC\.?|CORPORATION|CORP\.?|'
    r'L\.?\s*L\.?\s*C\.?|LIMITED|LTD\.?|COMPANY|CO\.?|'
    r'L\.?\s*L\.?\s*P\.?|L\.?\s*P\.?)[\s,]*)+$'
)


def main():
    recipients = pl.read_parquet(INPUT).with_columns(
        pl.col('name').str.strip_chars().str.to_uppercase()
        .str.replace(SUFFIX, '').alias('canonical_name'),
        # These are the identifier surface forms present in this table.
        pl.col('uei').str.strip_chars().str.to_uppercase()
        .str.replace(r'^UEI:', '').str.replace(r'-UEI$', '')
        .alias('canonical_uei'),
    )
    assert recipients['canonical_uei'].str.contains(r'^[A-Z0-9]{12}$').all()
    multiple = (
        recipients.filter(pl.col('canonical_name').is_not_null())
        .group_by('canonical_name')
        .agg(
            pl.col('canonical_uei').drop_nulls().n_unique().alias('distinct_ueis'),
            pl.col('name').unique().sort().alias('source_names'),
            pl.col('canonical_uei').drop_nulls().unique().sort().alias('ueis'),
        )
        .filter(pl.col('distinct_ueis') > 1)
        .sort('canonical_name')
    )
    multiple.write_json(OUTPUT / 'recipients_with_multiple_ueis.json')
    answer = {'answer': f'{multiple.height} distinct recipients are each associated with more than one UEI.'}
    (OUTPUT / 'answer.json').write_text(json.dumps(answer) + '\n')
    print(json.dumps(answer))


if __name__ == '__main__':
    main()
