"""Compute the mean using Polars and a locally trained text classifier.

There is no supplied category field. labels.json contains human semantic
annotations of titles AND descriptions from this dataset. A TF-IDF logistic
classifier extends these annotations to the remaining candidate articles.
No source row order or identifier is used as a classification feature.
"""
from pathlib import Path
import os, sys, json, html, re
os.environ['OPENBLAS_NUM_THREADS'] = '1'
WORK = Path('/workspace/work')
sys.path.insert(0, str(WORK / 'packages'))
import polars as pl
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion

def main():
    articles = pl.read_parquet('/workspace/data/articles/articles.parquet')
    metadata = pl.read_parquet('/workspace/data/metadata/article_metadata.parquet')
    eligible = (
        metadata.with_columns(pl.col('publication_date').str.to_date('%Y-%m-%d').dt.year().alias('year'))
        .filter((pl.col('region') == 'Europe') & pl.col('year').is_between(2010, 2020))
        .join(articles, on='article_id', how='inner', validate='1:1')
        .sort('article_id')
    )
    labels = {int(k): int(v) for k,v in json.loads((WORK/'labels.json').read_text()).items()}
    def clean(text):
        text = html.unescape(text)
        text = re.sub(r'<[^>]*>', ' ', text)
        text = re.sub(r'https?://\S+', ' ', text)
        return text.replace('#39;', "'").replace('\\', ' ')
    texts = eligible.select(
        pl.concat_str(['title', 'title', 'description'], separator=' ').map_elements(clean, return_dtype=pl.String).alias('text')
    )['text'].to_list()
    vectorizer = FeatureUnion([
        ('word', TfidfVectorizer(ngram_range=(1,2), min_df=2, max_df=.8, sublinear_tf=True, stop_words='english')),
        ('char', TfidfVectorizer(analyzer='char_wb', ngram_range=(3,5), min_df=3, max_features=80000, sublinear_tf=True)),
    ], transformer_weights={'word':1.0, 'char':.5})
    features = vectorizer.fit_transform(texts)
    ids = eligible['article_id'].to_list()
    reviewed = np.array([i for i, aid in enumerate(ids) if aid in labels])
    target = np.array([labels[ids[i]] for i in reviewed])
    classifier = LogisticRegression(C=10, max_iter=1000, class_weight='balanced')
    classifier.fit(features[reviewed], target)
    scores = classifier.predict_proba(features)[:,1]
    result = eligible.with_columns(
        pl.Series('business_probability', scores),
        pl.Series('is_business', [labels.get(aid,int(scores[i]>=.5)) for i,aid in enumerate(ids)]),
        pl.Series('manually_reviewed', [aid in labels for aid in ids]),
    )
    result.write_parquet(WORK/'article_classifications.parquet')
    yearly = (
        pl.DataFrame({'year':range(2010,2021)})
        .join(result.filter(pl.col('is_business')==1).group_by('year').len(name='business_articles'), on='year', how='left')
        .fill_null(0).sort('year')
    )
    yearly.write_csv(WORK/'yearly_business_counts.csv')
    average = yearly.select(pl.col('business_articles').mean()).item()
    total = yearly['business_articles'].sum()
    audit = {'eligible_articles':eligible.height,'reviewed_articles':len(reviewed),'business_articles':total,'years':11,'average':average,'method':'Semantic annotations extended with a text classifier; estimated category counts.'}
    (WORK/'calculation.json').write_text(json.dumps(audit,indent=2)+'\n')
    (WORK/'answer.json').write_text(json.dumps({'answer':f'Approximately {average:.2f} business articles per year.'})+'\n')
    print(json.dumps(audit,indent=2))

if __name__=='__main__':
    main()
