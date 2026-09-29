from pathlib import Path
from datetime import date
import json
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def clean_id(name):
    return pl.col(name).str.strip_chars().str.strip_chars_start('#')

def main():
    today = date(2022, 11, 25)
    start = pl.select(pl.lit(today).dt.offset_by('-5mo')).item()
    # Orders use EffectiveDate; the contract-date policy pertains to opportunities.
    orders = pl.read_parquet(DATA / 'products_orders/Order.parquet').select(
        clean_id('Id').alias('OrderId'), clean_id('OwnerId'),
        pl.col('EffectiveDate').str.strip_chars().str.to_date().alias('OrderDate'),
    )
    assert orders['OrderId'].n_unique() == orders.height
    eligible = orders.filter(pl.col('OrderDate').is_between(start, today))
    items = pl.read_parquet(DATA / 'products_orders/OrderItem.parquet').select(
        clean_id('OrderId'),
        (pl.col('Quantity').str.strip_chars().cast(pl.Float64) *
         pl.col('UnitPrice').str.strip_chars().cast(pl.Float64)).alias('SalesAmount'),
    )
    order_sales = items.group_by('OrderId').agg(pl.col('SalesAmount').sum())
    ranking = eligible.join(order_sales, on='OrderId', how='inner', validate='1:1').group_by('OwnerId').agg(
        pl.col('SalesAmount').sum()
    ).sort(['SalesAmount', 'OwnerId'], descending=[True, False])
    assert ranking.height > 0
    assert ranking.height == 1 or ranking['SalesAmount'][0] > ranking['SalesAmount'][1]
    winner = ranking['OwnerId'][0]
    users = pl.read_parquet(DATA / 'core_crm/User.parquet').select(clean_id('Id'))
    assert winner in users['Id'].to_list()
    ranking.write_csv(OUT / 'agent_sales.csv')
    (OUT / 'answer.json').write_text(json.dumps({'answer': winner}) + '\n')
    print(ranking)
    print(winner)

if __name__ == '__main__':
    main()
