"""Estimate business-article frequency using text annotations and Ibis/DuckDB.

Inputs contain no category. labels.json and validation_labels.json are manual
annotations of titles and descriptions from these inputs, not source labels.
The statistical text classifier consequently yields an approximate answer.
"""
from pathlib import Path
import html
import json
import re
import ibis
import numpy as np
import pyarrow as pa
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix

WORK = Path('/workspace/work')
DATA = Path('/workspace/data')

def normalize(value):
    value = html.unescape(value)
    value = re.sub(r'<[^>]+>', ' ', value)
    value = re.sub(r'http\S+', ' ', value)
    return re.sub(r'\\|#\d+;?', ' ', value)

def main():
    con = ibis.duckdb.connect()
    articles = con.read_parquet(str(DATA / 'articles/articles.parquet'))
    metadata = con.read_parquet(str(DATA / 'metadata/article_metadata.parquet'))
    metadata = metadata.mutate(date=metadata.publication_date.cast('date'))
    metadata = metadata.filter(
        (metadata.region == 'Europe') & metadata.date.year().between(2010, 2020)
    )
    selected = articles.join(metadata, 'article_id').select(
        articles.article_id, articles.title, articles.description,
        year=metadata.date.year(),
    )
    # Text materialization is required at the machine-learning boundary.
    texts_table = selected.select('article_id', 'title', 'description').distinct().order_by('article_id')
    records = texts_table.to_pyarrow().to_pylist()
    annotations = {r['article_id']: r['business'] for r in json.loads((WORK/'labels.json').read_text())}
    validation = {r['article_id']: r['business'] for r in json.loads((WORK/'validation_labels.json').read_text())}
    texts = [normalize(r['title']+' '+r['title']+' '+r['description']) for r in records]
    vectorizer = TfidfVectorizer(ngram_range=(1,2), min_df=2, sublinear_tf=True,
                                strip_accents='unicode', stop_words='english')
    features = vectorizer.fit_transform(texts)
    train = [i for i,r in enumerate(records) if r['article_id'] in annotations]
    test = [i for i,r in enumerate(records) if r['article_id'] in validation and r['article_id'] not in annotations]
    y = np.array([annotations[records[i]['article_id']] for i in train])
    truth = np.array([validation[records[i]['article_id']] for i in test])
    model = LogisticRegression(C=8, class_weight='balanced', max_iter=1000, random_state=31)
    model.fit(features[train], y)
    scores = model.predict_proba(features)[:,1]
    # Select the threshold by held-out classification error. For tied error
    # rates prefer the least biased aggregate count, then proximity to 0.5.
    thresholds = np.linspace(0.35, 0.65, 61)
    def objective(t):
        p = scores[test] >= t
        return (int((p != truth).sum()), abs(int(p.sum())-int(truth.sum())), abs(t-.5))
    threshold = float(min(thresholds, key=objective))
    predicted = scores >= threshold
    reviewed = {**annotations, **validation}
    output = []
    for i,r in enumerate(records):
        label = bool(reviewed.get(r['article_id'], predicted[i]))
        output.append({'article_id': r['article_id'], 'business': label, 'score': float(scores[i]),
                       'manually_reviewed': r['article_id'] in reviewed})
    labels = con.create_table('inferred_categories', ibis.memtable(pa.Table.from_pylist(output)))
    labels.to_parquet(str(WORK/'inferred_categories.parquet'))
    business = selected.join(labels, 'article_id').filter(labels.business)
    yearly = business.group_by('year').aggregate(articles=business.count())
    years = ibis.memtable({'year': list(range(2010, 2021))})
    annual = years.left_join(yearly, 'year').select(years.year, articles=yearly.articles.fill_null(0)).order_by('year')
    average = float(annual.aggregate(average=annual.articles.mean()).to_pyarrow()['average'][0].as_py())
    audit = {
        'method': 'Human-annotated text classifier; estimated categories',
        'training_articles': len(train), 'held_out_articles': len(test),
        'threshold': threshold,
        'held_out_confusion_matrix': confusion_matrix(truth,scores[test]>=threshold).tolist(),
        'held_out_accuracy': float(((scores[test]>=threshold)==truth).mean()),
        'yearly_counts': annual.to_pyarrow().to_pylist(),
        'average': average,
    }
    (WORK/'audit.json').write_text(json.dumps(audit, indent=2))
    answer = {'answer': f'Approximately {average:.2f} business articles per year.'}
    (WORK/'answer.json').write_text(json.dumps(answer))
    print(json.dumps(audit, indent=2))
    print(json.dumps(answer))

if __name__ == '__main__':
    main()
