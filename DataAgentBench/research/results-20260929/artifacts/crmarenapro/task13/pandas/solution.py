import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def clean_id(series):
    return series.astype('string').str.strip().str.lstrip('#')

def main():
    orders = pd.read_parquet(DATA / 'products_orders/Order.parquet')
    items = pd.read_parquet(DATA / 'products_orders/OrderItem.parquet')
    for col in ['Id', 'OwnerId']:
        orders[col] = clean_id(orders[col])
    items['OrderId'] = clean_id(items['OrderId'])
    # Orders are dated by EffectiveDate; contract dates apply to opportunities.
    today = pd.Timestamp('2022-11-25')
    start = today - pd.DateOffset(months=5)
    dates = pd.to_datetime(orders['EffectiveDate'].str.strip(), errors='raise')
    eligible = orders.loc[(dates >= start) & (dates < today + pd.Timedelta(days=1))]
    items['sales'] = pd.to_numeric(items['Quantity'], errors='raise') * pd.to_numeric(items['UnitPrice'], errors='raise')
    totals = items.groupby('OrderId', as_index=False)['sales'].sum()
    sales = eligible.merge(totals, left_on='Id', right_on='OrderId', how='inner', validate='one_to_one')
    ranking = sales.groupby('OwnerId')['sales'].sum().sort_values(ascending=False)
    assert not ranking.empty
    assert len(ranking) == 1 or ranking.iloc[0] > ranking.iloc[1]
    (OUT / 'answer.json').write_text(json.dumps({'answer': str(ranking.index[0])}))
    print(ranking.to_string())

if __name__ == '__main__':
    main()
