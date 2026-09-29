"""Compute the fraction using Ibis/DuckDB and explicit semantic annotations.

Category annotations are based on reading the selected titles and descriptions,
not keyword matching. Financial results, acquisitions, employment cuts, and
commercial litigation are Business even when a technology firm is involved.
"""
import json
from pathlib import Path
import ibis

OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
articles = con.read_parquet('/workspace/data/articles/articles.parquet')
metadata = con.read_parquet('/workspace/data/metadata/article_metadata.parquet')
authors = con.read_parquet('/workspace/data/metadata/authors.parquet')
selected = (metadata.join(authors.filter(authors.name == 'Amy Jones'), 'author_id')
            .join(articles, 'article_id')
            .select('article_id', 'title', 'description'))

# Human semantic review of both fields. These are category annotations, not
# a stored numerator or denominator; the actual counts are computed below.
science_reasons = {
    192: 'Innovation in video game design.',
    2844: 'Student laboratory research and a science competition.',
    2987: 'A wave-energy electricity invention wins a science award.',
    15473: 'Rebuilding scientific activity, centered on a nuclear physicist.',
    22354: 'The Genesis space probe and its failed sample return.',
    24495: 'Repairing the space shuttle fleet.',
    35882: 'New email storage and management software.',
    46531: 'Feasibility of future space tourism.',
    89666: 'How blogs spread and debunk election claims; online media behavior.',
    92992: 'A study of fear transmission and body language in crowds.',
    93804: 'Environmental research on watersheds and development impacts.',
    105804: 'Software designed to inhibit computer virus transmission.',
    106908: 'Predicted convergence of satellite radio and mobile technology.',
    108586: 'A new online marketplace feature.',
    112770: 'Integration of an online payment system with a digital music service.',
    119651: 'Ocean research, fisheries management, and pollution oversight.',
    126655: 'New Internet-based satellite imagery technology.',
}
sports = [2161,4447,8962,15100,21238,26535,28079,29164,35408,38608,
          39117,39623,47439,54906,57918,70498,70608,78200,80853,83273,
          96986,101514,103695,104996,107036,112063,120765,124509]
world = [5354,6705,6869,9677,19469,20362,29297,33489,40545,62404,
         62754,66827,68509,69262,69393,72525,82668,88553,93287,94618,
         103003,103591,104998,113058,119920,120129,122137,126412]
business = [3451,3970,9858,14861,17491,23914,25960,27429,36182,36483,
            37042,41616,48635,48833,49035,52459,57510,57860,64102,
            68958,73025,73684,80578,81851,82526,88911,91286,91822,
            96641,99699,100613,104123,109601,110096,111422,116698,
            123747,126966]
annotations = []
for category, ids in [('Science/Technology', science_reasons), ('Sports', sports),
                      ('World', world), ('Business', business)]:
    for article_id in ids:
        annotations.append({'article_id': article_id, 'category': category,
                            'reason': science_reasons.get(article_id, '')})
assert len({r['article_id'] for r in annotations}) == len(annotations)
labels = ibis.memtable(annotations)
assert selected.anti_join(labels, 'article_id').count().execute() == 0
assert labels.anti_join(selected, 'article_id').count().execute() == 0
classified = selected.join(labels, 'article_id')
counts = classified.aggregate(
    total=classified.count(),
    science=(classified.category == 'Science/Technology').cast('int64').sum(),
).to_pyarrow().to_pylist()[0]
review = classified.order_by('article_id').to_pyarrow().to_pylist()
(OUT / 'article_classifications.json').write_text(json.dumps(review, indent=2))
n, d = counts['science'], counts['total']
answer = f'{n}/{d} (approximately {100*n/d:.2f}%).'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(answer)

if __name__ == '__main__':
    pass
