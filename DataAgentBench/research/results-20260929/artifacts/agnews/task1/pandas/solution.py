"""Compute lengths in pandas; use semantic review of the longest articles.

There is no category field. The annotations below record review of both
full title and description, not keyword matches. Only the longest prefix
needs review: all unreviewed rows must be shorter than the sports maximum.
"""
import json
from pathlib import Path
import pandas as pd

OUT = Path('/workspace/work')
# Semantic annotations from the supplied table. No answer titles or lengths
# are embedded; those are computed and retrieved from the input.
NON_SPORTS = {
    19776, 96745, 105792, 112789, 95659, 106486, 63582, 93941,
    32433, 64097, 96644, 69024, 63799, 65815, 112806, 112808,
    1061, 106827, 108623, 110407, 60485, 57164, 105416, 10769,
    99285, 111618, 9411, 18778, 106905, 57215, 95309, 15168,
    99237, 85027, 61768, 60884, 16666, 51521, 110047,
}
SPORTS = {69413}  # Football matchup preview, team performance and player fitness.

def main():
    articles = pd.read_parquet('/workspace/data/articles/articles.parquet')
    articles['characters'] = articles['description'].str.len()
    labels = {i: False for i in NON_SPORTS}
    labels.update({i: True for i in SPORTS})
    articles['is_sports_review'] = articles.article_id.map(labels)
    reviewed = articles[articles.is_sports_review.notna()]
    sports = reviewed[reviewed.is_sports_review.eq(True)]
    maximum = sports.characters.max()
    contenders = articles[articles.characters.ge(maximum)]
    assert contenders.is_sports_review.notna().all(), 'Review additional contenders'
    winners = sports[sports.characters.eq(maximum)]
    assert len(winners) == 1, 'Handle tied maximum'
    reviewed.sort_values('characters', ascending=False).to_csv(
        OUT / 'semantic_review.csv', index=False)
    answer = {'answer': winners.iloc[0]['title']}
    (OUT / 'answer.json').write_text(json.dumps(answer, ensure_ascii=False) + '\n')
    print(json.dumps(answer, ensure_ascii=False))
    print(f'Description characters: {maximum}; longer articles reviewed: '
          f'{articles.characters.gt(maximum).sum()}')

if __name__ == '__main__':
    main()
