"""Rank exact description strings with Ibis/DuckDB and apply semantic review.

Category is absent from the source. The annotations below record review of
both title and full description for the longest 40 articles. Only membership
in Sports is needed. Every longer article was reviewed, so shorter articles
cannot alter the maximum. Titles and lengths are always read from Parquet.
"""
import json
from pathlib import Path
import ibis

OUT = Path('/workspace/work')
# Human semantic annotations, based solely on the supplied article text.
NONSPORTS = [
    19776, 96745, 105792, 112789, 95659, 106486, 63582, 93941,
    32433, 64097, 96644, 69024, 63799, 65815, 112806, 112808,
    1061, 106827, 108623, 110407, 60485, 57164, 105416, 10769,
    99285, 111618, 9411, 18778, 106905, 57215, 95309, 15168,
    99237, 85027, 61768, 60884, 16666, 51521, 110047,
]
SPORTS = [69413]  # College football matchup, team performance and player fitness.

def main():
    con = ibis.duckdb.connect()
    articles = con.read_parquet('/workspace/data/articles/articles.parquet')
    ranked = articles.mutate(description_characters=articles.description.length())
    labels = ibis.memtable(
        [(i, False) for i in NONSPORTS] + [(i, True) for i in SPORTS],
        schema={'article_id': 'int64', 'is_sports': 'boolean'},
    )
    reviewed = ranked.join(labels, 'article_id')
    sports = reviewed.filter(reviewed.is_sports)
    winners = sports.filter(
        sports.description_characters == sports.description_characters.max()
    ).order_by('article_id')
    result = winners.to_pyarrow().to_pylist()
    assert result, 'No reviewed sports article'
    cutoff = result[0]['description_characters']
    # Ensure no longer or tied article escaped semantic review.
    unchecked = ranked.filter(ranked.description_characters >= cutoff).anti_join(labels, 'article_id')
    assert unchecked.count().execute() == 0, 'Additional semantic review required'
    audit = reviewed.order_by(ibis.desc('description_characters'), 'article_id').to_pyarrow().to_pylist()
    (OUT / 'reviewed_articles.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2))
    answer = '; '.join(r['title'] for r in result)
    (OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
    print(json.dumps({'answer': answer}, ensure_ascii=False))

if __name__ == '__main__':
    main()
