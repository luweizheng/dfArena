from pathlib import Path
import json
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

# Semantic annotations from reading each selected article's title and description.
# Company financial results, acquisitions, and commercial litigation are Business;
# research, computing capabilities, and environmental science are Science/Technology.
category_ids = {
    'Science/Technology': [192, 2844, 2987, 15473, 22354, 24495, 35882, 46531,
        89666, 92992, 93804, 105804, 106908, 108586, 119651, 126655],
    'Sports': [2161,4447,8962,15100,21238,26535,28079,29164,35408,38608,
        39117,39623,47439,54906,57918,70498,70608,78200,80853,83273,
        96986,101514,103695,104996,107036,112063,120765,124509],
    'World': [5354,6705,6869,9677,19469,20362,29297,33489,40545,62404,
        62754,66827,68509,69262,69393,72525,82668,88553,93287,94618,
        103003,103591,104998,113058,119920,120129,122137,126412],
    'Business': [3451,3970,9858,14861,17491,23914,25960,27429,36182,36483,
        37042,41616,48635,48833,49035,52459,57510,57860,64102,68958,
        73025,73684,80578,81851,82526,88911,91286,91822,96641,99699,
        100613,104123,109601,110096,111422,112770,116698,123747,126966],
}
notes = {
    15473: 'Rebuilding scientific research, centered on an Iraqi physicist.',
    17491: 'Revenue forecast and product sales, rather than chip technology.',
    24495: 'Repairing the space shuttle fleet; cost is context for a space program report.',
    25960: 'Settlement of litigation between two companies over technology.',
    41616: 'Acquisitions and corporate cost reductions.',
    52459: 'Drug launch delay and its setback for the pharmaceutical company.',
    64102: 'Quarterly profits are the main focus.',
    73025: 'Regulatory approval of a corporate merger.',
    89666: 'How blogs spread and debunk online claims about the election.',
    93804: 'Funding studies of ecological effects on watersheds.',
    106908: 'Predicted technological convergence of satellite radio and cellphones.',
    108586: 'New functionality on an online marketplace.',
    109601: 'Acquisition of a computer business.',
    112770: 'Commercial payment partnership and securing retailer business.',
    119651: 'Ocean research, fisheries management and pollution oversight.',
}

def main():
    authors = pl.read_parquet(DATA / 'metadata/authors.parquet')
    metadata = pl.read_parquet(DATA / 'metadata/article_metadata.parquet')
    articles = pl.read_parquet(DATA / 'articles/articles.parquet')
    selected = (metadata.join(authors.filter(pl.col('name') == 'Amy Jones'),
                              on='author_id', how='semi')
                .join(articles, on='article_id', how='left', validate='m:1'))
    labels = pl.DataFrame([
        {'article_id': aid, 'category': category, 'rationale': notes.get(aid, '')}
        for category, ids in category_ids.items() for aid in ids
    ])
    classified = selected.join(labels, on='article_id', how='left', validate='m:1')
    assert classified['category'].null_count() == 0, 'Unclassified article'
    assert classified['title'].null_count() == 0, 'Missing article'
    assert labels.height == classified['article_id'].n_unique(), 'Annotation scope mismatch'
    classified.sort('article_id').write_csv(OUT / 'classified_articles.csv')
    counts = classified.select(
        pl.len().alias('total'),
        (pl.col('category') == 'Science/Technology').sum().alias('science')
    ).row(0, named=True)
    total, science = counts['total'], counts['science']
    answer = f'{science}/{total} (approximately {100 * science / total:.2f}%).'
    (OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
    print(answer)

if __name__ == '__main__':
    main()
