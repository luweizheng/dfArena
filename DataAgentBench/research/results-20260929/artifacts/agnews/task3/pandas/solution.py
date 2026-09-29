"""Compute the requested average using pandas and reviewed text classifications.

There is no category field. labels.json contains manual semantic annotations of
actual title/description pairs, made during this run, not reference labels.
A regularized text classifier infers business membership for unreviewed rows.
The result is consequently reported as an estimate.
"""
from pathlib import Path
from collections import Counter
import html
import json
import re
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.linear_model import LogisticRegression

DATA = Path('/workspace/data')
WORK = Path('/workspace/work')
YEARS = pd.Index(range(2010, 2021), name='year')


def tokenize(value):
    words = re.findall(r'[a-z][a-z]+', html.unescape(value.lower()))
    return words + [a + ' ' + b for a, b in zip(words, words[1:])]


def text_features(frame):
    # Weight the headline twice, but always include the complete description.
    documents = [Counter(tokenize(r.title + ' ' + r.title + ' ' + r.description))
                 for r in frame.itertuples()]
    frequencies = Counter()
    for document in documents:
        frequencies.update(document.keys())
    vocabulary = {word: j for j, word in enumerate(
        word for word, count in frequencies.items()
        if 3 <= count < len(frame) * 0.5)}
    idf = np.array([np.log((len(frame) + 1) / (frequencies[word] + 1)) + 1
                    for word in vocabulary])
    row_indices, column_indices, values = [], [], []
    for row, document in enumerate(documents):
        for word, count in document.items():
            if word in vocabulary:
                column = vocabulary[word]
                row_indices.append(row)
                column_indices.append(column)
                values.append((1 + np.log(count)) * idf[column])
    matrix = csr_matrix((values, (row_indices, column_indices)),
                        shape=(len(frame), len(vocabulary)))
    norms = np.sqrt(np.asarray(matrix.multiply(matrix).sum(axis=1)).ravel())
    return matrix.multiply((1 / np.maximum(norms, 1e-12))[:, None]).tocsr()


def main():
    articles = pd.read_parquet(DATA / 'articles/articles.parquet')
    metadata = pd.read_parquet(DATA / 'metadata/article_metadata.parquet')
    metadata['publication_date'] = pd.to_datetime(metadata['publication_date'], errors='raise')
    selected = metadata.loc[
        metadata['region'].eq('Europe')
        & metadata['publication_date'].ge('2010-01-01')
        & metadata['publication_date'].lt('2021-01-01')
    ]
    frame = selected.merge(articles, on='article_id', how='left', validate='one_to_one')
    assert frame[['title', 'description']].notna().all().all()
    annotations = {int(key): int(value)
                   for key, value in json.loads((WORK / 'labels.json').read_text()).items()}
    labels = frame['article_id'].map(annotations)
    reviewed = labels.notna().to_numpy()
    matrix = text_features(frame)
    model = LogisticRegression(C=10, max_iter=1000, solver='lbfgs', random_state=42)
    model.fit(matrix[reviewed], labels.loc[reviewed].astype(int))
    frame['business_probability'] = model.predict_proba(matrix)[:, 1]
    frame['business'] = frame['business_probability'].ge(0.5)
    # Reviewed semantic judgments take precedence over model predictions.
    frame.loc[reviewed, 'business'] = labels.loc[reviewed].astype(bool)
    frame['category_source'] = np.where(reviewed, 'manual semantic review', 'text classifier')
    frame['year'] = frame['publication_date'].dt.year
    counts = frame.loc[frame.business].groupby('year').size().reindex(YEARS, fill_value=0)
    counts.name = 'business_articles'
    average = counts.mean()
    assert len(counts) == 11
    assert counts.sum() == frame['business'].sum()
    counts.to_csv(WORK / 'yearly_counts.csv')
    frame.to_csv(WORK / 'article_classifications.csv', index=False)
    frame.loc[reviewed, ['article_id', 'title', 'description', 'business']].to_csv(
        WORK / 'reviewed_examples.csv', index=False)
    audit = pd.read_json(WORK / 'audit_labeled.json')
    prior_predictions = audit['probability'].ge(0.5)
    audit_errors = prior_predictions.ne(audit['business'].astype(bool))
    diagnostics = {
        'region': 'Europe', 'first_year': 2010, 'last_year': 2020,
        'number_of_years': len(counts), 'eligible_articles': len(frame),
        'reviewed_articles': int(reviewed.sum()),
        'classified_business_articles': int(counts.sum()),
        'average_business_articles_per_year': float(average),
        'pre_final_fit_random_audit_size': len(audit),
        'pre_final_fit_random_audit_errors': int(audit_errors.sum()),
        'limitation': 'Category labels are inferred from title and description; the average is an estimate.'
    }
    (WORK / 'diagnostics.json').write_text(json.dumps(diagnostics, indent=2) + '\n')
    answer = f'Estimated average: {average:.2f} business articles per year (2010–2020 inclusive).'
    (WORK / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
    print(json.dumps(diagnostics, indent=2))
    print(answer)


if __name__ == '__main__':
    main()
