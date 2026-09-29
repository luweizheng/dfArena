"""Count 2015 World reports by publication region using pandas.

No category is supplied. Titles and descriptions were grouped by their joint
text, then reviewed semantically. semantic_annotations.csv records the binary
World/not-World decisions for reviewed reports (not region-level answers).
Remaining reports use the semantically interpreted topic groups. Region was
not used as a classification feature. Metadata dates, not dates mentioned in
article prose, determine the reporting year.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '2'
from pathlib import Path
import json
import re
from collections import Counter
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

ROOT = Path('/workspace/work')

def main():
    articles = pd.read_parquet('/workspace/data/articles/articles.parquet')
    metadata = pd.read_parquet('/workspace/data/metadata/article_metadata.parquet')
    dates = pd.to_datetime(metadata['publication_date'], errors='raise')
    reports = metadata.loc[dates.dt.year.eq(2015)].merge(
        articles, on='article_id', how='inner', validate='many_to_one', sort=False)
    stop = set(('the a an of to in on at for and or with by from as is are was were '
        'be been has have had that this it its their his her he she they said says '
        'will would could after before new over into than but not who which about '
        'reuters ap afp quot lt gt amp more one two first last year years monday '
        'tuesday wednesday thursday friday saturday sunday com all also up out us').split())
    docs = [Counter(t for t in re.findall('[a-z]{3,}', text.lower()) if t not in stop)
            for text in reports['title'].str.cat(reports['description'], sep=' ')]
    df = Counter(t for doc in docs for t in doc)
    terms = sorted(t for t, count in df.items() if 3 <= count < len(reports)*.6)
    vocab = {t: i for i, t in enumerate(terms)}
    rows, cols, values = [], [], []
    for i, doc in enumerate(docs):
        for term, count in doc.items():
            if term in vocab:
                rows.append(i)
                cols.append(vocab[term])
                values.append((1 + np.log(count))*np.log(1 + len(reports)/df[term]))
    x = csr_matrix((values, (rows, cols)), shape=(len(reports), len(terms)))
    x = x.multiply(1/np.sqrt(x.multiply(x).sum(axis=1))).tocsr()
    rng = np.random.default_rng(42)
    w = rng.random((len(reports), 60))
    h = rng.random((60, len(terms)))
    for _ in range(160):
        h *= (x.T @ w).T / (w.T @ w @ h + 1e-9)
        w *= (x @ h.T) / (w @ (h @ h.T) + 1e-9)
        norms = np.sqrt((h*h).sum(axis=1))
        h /= norms[:, None]
        w *= norms
    # Semantic interpretation of joint-text topics: Darfur; governments and
    # diplomacy; nuclear diplomacy; attacks; US politics; Israel/Palestine;
    # Afghan politics; Iraq; Arafat. Mixed-topic reports are manually reviewed.
    world_topics = [1, 4, 13, 24, 26, 27, 31, 36, 55]
    reports['is_world'] = pd.Series(w.argmax(axis=1)).isin(world_topics)
    annotations = pd.read_csv(ROOT/'semantic_annotations.csv').set_index('article_id')['is_world']
    reviewed = reports['article_id'].map(annotations)
    reports['is_world'] = reviewed.where(reviewed.notna(), reports['is_world']).astype(bool)
    counts = reports.loc[reports['is_world']].groupby('region').size().sort_values(ascending=False)
    reports[['article_id', 'region', 'publication_date', 'is_world']].to_csv(ROOT/'classification_audit.csv', index=False)
    counts.rename('world_articles').to_csv(ROOT/'region_counts.csv')
    winners = counts.index[counts.eq(counts.max())].tolist()
    answer = ', '.join(winners)
    (ROOT/'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
    print(counts.to_string())
    print(json.dumps({'answer': answer}))

if __name__ == '__main__':
    main()
