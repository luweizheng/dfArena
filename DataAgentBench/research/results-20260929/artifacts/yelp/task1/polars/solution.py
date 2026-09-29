import json
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def main():
    businesses = pl.scan_parquet(DATA / 'businessinfo/business.parquet')
    selected = businesses.filter(
        pl.col('description').str.contains(r'(?i)\bin Indianapolis,\s*(?:IN|Indiana)\s*[,\.]')
    ).select(pl.col('business_id').str.replace(r'^businessid_', 'businessref_').alias('business_ref'))
    reviews = pl.scan_parquet(DATA / 'user/review.parquet')
    result = reviews.join(selected, on='business_ref', how='semi').select(
        pl.len().alias('review_count'),
        pl.col('rating').sum().alias('rating_sum'),
        pl.col('rating').mean().alias('average_rating'),
    ).collect().row(0, named=True)
    assert result['review_count'] > 0 and result['average_rating'] is not None
    answer = f"The average rating of businesses in Indianapolis, Indiana is {result['average_rating']:.6f} out of 5."
    (OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
    print(json.dumps(result))

if __name__ == '__main__':
    main()
