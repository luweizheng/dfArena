"""Determine the leading region for World news published in 2015.

No source category exists. category_annotations.parquet contains semantic
judgments of title and description made during review, including focused
review of ambiguous records. A text classifier handles the remaining records.
Region and publication date are not classifier features. Polars performs all
loading, filtering, joining, and aggregation; sklearn supplies only text ML.
"""
from pathlib import Path
import json
import polars as pl
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

WORK = Path('/workspace/work')
DATA = Path('/workspace/data')

def main():
    articles = pl.read_parquet(DATA / 'articles/articles.parquet')
    metadata = pl.read_parquet(DATA / 'metadata/article_metadata.parquet')
    rows = (
        metadata.filter(pl.col('publication_date').str.to_date('%Y-%m-%d').dt.year() == 2015)
        .join(articles, on='article_id', how='inner', validate='m:1')
        .with_row_index('row_number')
    )
    annotations = pl.read_parquet(WORK / 'category_annotations.parquet')
    # Retain text in the annotation file to make the judgments auditable.
    rows = rows.join(annotations.select('article_id', 'is_world'),
                     on='article_id', how='left', validate='m:1').sort('row_number')
    texts = rows.select(
        pl.concat_str(['title', 'title', 'description'], separator=' ').alias('text')
    )['text'].to_list()
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True,
                               min_df=2, stop_words='english')
    features = vectorizer.fit_transform(texts)
    reviewed = rows.filter(pl.col('is_world').is_not_null())
    model = LinearSVC(C=2, class_weight='balanced', random_state=0)
    model.fit(features[reviewed['row_number'].to_numpy()], reviewed['is_world'].to_numpy())
    scores = model.decision_function(features)
    rows = rows.with_columns(pl.Series('classifier_score', scores)).with_columns(
        pl.col('is_world').fill_null(pl.col('classifier_score') > 0).alias('world_category')
    )
    totals = rows.filter(pl.col('world_category')).group_by('region').agg(
        pl.len().alias('article_count')
    ).sort(['article_count', 'region'], descending=[True, False])
    assert totals.height > 0
    assert totals['article_count'][0] > totals['article_count'][1], 'Tied leading regions'
    totals.write_csv(WORK / 'region_counts.csv')
    rows.write_parquet(WORK / 'classified_2015.parquet')
    result = {'answer': totals['region'][0]}
    (WORK / 'answer.json').write_text(json.dumps(result) + '\n')
    print(totals)
    print(json.dumps(result))

if __name__ == '__main__':
    main()
