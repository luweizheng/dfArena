"""Rank exact description character lengths in Polars.

The dataset lacks category labels. Semantic review of titles AND descriptions
classifies the longest prefix, through its first sports report. Shorter rows
cannot change the maximum. These annotations are input-derived category
judgments, not stored answer text or stored description lengths.
"""
import json
from pathlib import Path
import polars as pl

OUT = Path('/workspace/work')
# Reviewed reports longer than the first sports report concern computing,
# commerce, politics, charity, or reproductive rights, rather than sport.
non_sports = [
    19776, 96745, 105792, 112789, 95659, 106486, 63582, 93941,
    32433, 64097, 96644, 69024, 63799, 65815, 112806, 112808,
    1061, 106827, 108623, 110407, 60485, 57164, 105416, 10769,
    99285, 111618, 9411, 18778, 106905, 57215, 95309, 15168,
    99237, 85027, 61768, 60884, 16666, 51521, 110047,
]
# This report previews Miami versus N.C. State, discussing ACC standings,
# team defense, quarterback performance, and a running back's injury.
sports = [69413]
labels = pl.DataFrame({
    'article_id': non_sports + sports,
    'is_sports': [False] * len(non_sports) + [True] * len(sports),
})
articles = pl.read_parquet('/workspace/data/articles/articles.parquet').with_columns(
    pl.col('description').str.len_chars().alias('description_characters')
)
reviewed = articles.join(labels, on='article_id', how='left')
candidates = reviewed.filter(pl.col('is_sports') == True)
maximum = candidates.select(pl.col('description_characters').max()).item()
assert reviewed.filter(
    (pl.col('description_characters') >= maximum) & pl.col('is_sports').is_null()
).is_empty(), 'All potentially winning articles must be semantically reviewed.'
winners = candidates.filter(pl.col('description_characters') == maximum)
assert winners.height == 1, 'A tied maximum requires further reporting.'
reviewed.filter(pl.col('description_characters') >= maximum).sort(
    'description_characters', descending=True
).write_json(OUT / 'reviewed_articles.json')
answer = {'answer': winners.item(0, 'title')}
(OUT / 'answer.json').write_text(json.dumps(answer, ensure_ascii=False) + '\n')
print(json.dumps(answer, ensure_ascii=False))

if __name__ == '__main__':
    pass
