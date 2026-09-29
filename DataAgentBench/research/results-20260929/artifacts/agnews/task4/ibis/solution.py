"""Aggregate World articles using Ibis/DuckDB and content-reviewed annotations.

Category annotations were produced by reviewing the supplied article titles,
checking descriptions for ambiguous titles and overlapping subjects. World
covers public affairs, conflicts, diplomacy, general news and disasters;
sports, commercial/market reporting, and scientific/technical reports are
excluded. The annotations contain article decisions, never regional totals
or a hard-coded winning region. review_candidates.py provides the lexical
triage used to find possible omissions; its scores do not determine labels.
"""
import json
from pathlib import Path
import ibis

WORK = Path('/workspace/work')
DATA = Path('/workspace/data')

def main():
    con = ibis.duckdb.connect()
    articles = con.read_parquet(str(DATA / 'articles/articles.parquet'))
    metadata = con.read_parquet(str(DATA / 'metadata/article_metadata.parquet'))
    labels = con.read_json(str(WORK / 'category_annotations.json'))

    dated = metadata.mutate(published=metadata.publication_date.cast('date'))
    in_year = dated.filter(dated.published.year() == 2015)
    annotated = articles.join(labels, 'article_id').select(
        articles.article_id, labels.is_world
    )
    candidates = in_year.join(annotated, 'article_id')
    # Every metadata row is retained, including any repeated records.
    assert candidates.count().execute() == in_year.count().execute()
    assert labels.article_id.nunique().execute() == labels.count().execute()
    world = candidates.filter(candidates.is_world)
    counts = world.group_by('region').aggregate(articles=world.count())
    result = counts.order_by(ibis.desc('articles'), 'region').to_pyarrow().to_pylist()
    assert result, 'No matching articles'
    highest = result[0]['articles']
    winners = [x['region'] for x in result if x['articles'] == highest]
    answer = ', '.join(winners)
    (WORK / 'region_counts.json').write_text(json.dumps(result, indent=2))
    (WORK / 'answer.json').write_text(json.dumps({'answer': answer}))
    print(json.dumps({'answer': answer}))

if __name__ == '__main__':
    main()
