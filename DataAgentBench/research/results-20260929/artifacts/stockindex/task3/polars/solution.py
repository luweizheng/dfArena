import json
from datetime import date
from pathlib import Path
import polars as pl

OUT = Path('/workspace/work')
df = pl.read_parquet('/workspace/data/indextrade/index_trade.parquet')
formats = ['%Y-%m-%d %H:%M:%S', '%d %b %Y, %H:%M', '%B %d, %Y at %I:%M %p']
df = df.with_columns(pl.coalesce([pl.col('Date').str.strptime(pl.Datetime, f, strict=False) for f in formats]).dt.date().alias('date'))
assert df['date'].null_count() == 0
assert df.select(pl.struct(['Index', 'date']).is_duplicated().sum()).item() == 0
# A unit contribution on the first valid trading day of each month.
# CloseUSD permits equally sized dollar investments in each market.
prices = df.filter((pl.col('date') >= date(2000, 1, 1)) & pl.col('CloseUSD').is_finite() & (pl.col('CloseUSD') > 0)).sort(['Index', 'date'])
monthly = prices.with_columns(pl.col('date').dt.truncate('1mo').alias('month')).group_by(['Index', 'month'], maintain_order=True).agg(pl.col('date').first().alias('purchase_date'), pl.col('CloseUSD').first().alias('purchase_price'))
positions = monthly.group_by('Index').agg(pl.len().alias('contributions'), (1 / pl.col('purchase_price')).sum().alias('units'), pl.col('purchase_date').min().alias('start'))
terminal = prices.group_by('Index').agg(pl.col('date').last().alias('end'), pl.col('CloseUSD').last().alias('terminal_price'))
ranking = positions.join(terminal, on='Index').with_columns((pl.col('units') * pl.col('terminal_price')).alias('final_value')).with_columns(((pl.col('final_value') / pl.col('contributions') - 1) * 100).alias('return_pct')).sort('return_pct', descending=True)
print(ranking)
ranking.write_csv(OUT / 'monthly_investment_returns.csv')
monthly.write_csv(OUT / 'monthly_purchases.csv')
# Geographic interpretation of the observed index symbols; not a join to Exchange.
countries = {'399001.SZ': 'China', 'HSI': 'Hong Kong (China)', 'NYA': 'United States', 'IXIC': 'United States', '000001.SS': 'China', 'N225': 'Japan', 'N100': 'Europe (multiple countries)', 'NSEI': 'India', 'BSESN': 'India', 'GSPTSE': 'Canada', 'GDAXI': 'Germany', 'SSMI': 'Switzerland', 'TWII': 'Taiwan', 'J203.JO': 'South Africa', 'KS11': 'South Korea'}
top = ranking.head(5).to_dicts()
answer = 'Assuming equal monthly investments at the first trading-day close from January 2000 (or the first available month), valued at each index’s latest available close, the highest cumulative returns were: ' + '; '.join(f"{i}. {r['Index']} — {countries[r['Index']]} ({r['return_pct']:.1f}%)" for i, r in enumerate(top, 1)) + '. Returns are gains divided by total contributions, using CloseUSD; data end in May–June 2021. NSEI history begins in September 2007, so its investment period is shorter.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False))
