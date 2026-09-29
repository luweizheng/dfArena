"""Compute Amy Jones's category share with pandas.

Categories are semantic annotations of the supplied title AND description,
not inferred from IDs, individual keywords, or unavailable original labels.
Financial results, mergers, commercial agreements and corporate litigation
are Business; research, computing features, and environmental science are
Science/Technology. The final answer is computed from joined input records.
"""
import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

# Manual content annotations, made after reading each selected article.
SCIENCE = {
    192: 'Innovation in video games',
    2844: 'Student laboratory research and a science competition',
    2987: 'An invention generating electricity from ocean waves',
    15473: 'A physicist rebuilding scientific work in Iraq',
    22354: 'Failure of a solar-sample space mission',
    24495: 'Repairs to the NASA space shuttle fleet',
    35882: 'New email storage and management software',
    46531: 'Technical feasibility of future space tourism',
    89666: 'How weblogs propagate and debunk election theories',
    92992: 'Research into body language and crowd fear',
    93804: 'Studies of ecological effects on watersheds',
    105804: 'Software to slow computer virus propagation',
    106908: 'Future convergence of satellite radio and mobile phones',
    108586: 'A new online marketplace software feature',
    119651: 'Ocean research, fisheries management and pollution oversight',
    126655: 'Internet technology for accessing satellite imagery',
}
SPORTS = {
    2161,4447,8962,15100,21238,26535,28079,29164,35408,38608,
    39117,39623,47439,54906,57918,70498,70608,78200,80853,83273,
    96986,101514,103695,104996,107036,112063,120765,124509,
}
BUSINESS = {
    3451,3970,9858,14861,17491,23914,25960,27429,36182,36483,
    37042,41616,48635,48833,49035,52459,57510,57860,64102,
    68958,73025,73684,80578,81851,82526,88911,91286,91822,
    96641,99699,100613,104123,109601,110096,111422,112770,
    116698,123747,126966,
}
WORLD = {
    5354,6705,6869,9677,19469,20362,29297,33489,40545,62404,
    62754,66827,68509,69262,69393,72525,82668,88553,93287,
    94618,103003,103591,104998,113058,119920,120129,122137,126412,
}

def main():
    authors = pd.read_parquet(DATA / 'metadata/authors.parquet')
    metadata = pd.read_parquet(DATA / 'metadata/article_metadata.parquet')
    articles = pd.read_parquet(DATA / 'articles/articles.parquet')
    selected = (metadata.merge(authors.loc[authors['name'].eq('Amy Jones')],
                               on='author_id', validate='many_to_one')
                .merge(articles, on='article_id', validate='one_to_one'))
    groups = {'Science/Technology': set(SCIENCE), 'Sports': SPORTS,
              'Business': BUSINESS, 'World': WORLD}
    labels = {key: category for category, keys in groups.items() for key in keys}
    assert sum(map(len, groups.values())) == len(labels), 'Overlapping annotations'
    assert set(selected.article_id) == set(labels), 'Unreviewed or missing articles'
    selected['category'] = selected.article_id.map(labels)
    selected['science_rationale'] = selected.article_id.map(SCIENCE).fillna('')
    selected.to_csv(OUT / 'classified_articles.csv', index=False)
    count = int(selected.category.eq('Science/Technology').sum())
    total = len(selected)
    answer = f'{count}/{total} (approximately {100 * count / total:.2f}%).'
    (OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
    print(answer)

if __name__ == '__main__':
    main()
