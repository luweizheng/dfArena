# stockindex

This dataset contains two Parquet tables: stock-exchange metadata and daily historical prices for stock-market indices. Paths below are relative to the dataset root.

## Table: `index_info`

Metadata about stock market exchanges from major markets around the world, including the United States, China, Canada, Germany, Japan, and more.

File: `data/indexinfo/index_info.parquet`

| Column | Parquet / Arrow type | Description |
|---|---|---|
| `Exchange` | `string` | Full name of the stock exchange. |
| `Currency` | `string` | Trading currency of the exchange. |

## Table: `index_trade`

Daily price data for indices tracking stock exchanges across countries and regions.

File: `data/indextrade/index_trade.parquet`

| Column | Parquet / Arrow type | Description |
|---|---|---|
| `Index` | `string` | Abbreviated index symbol. |
| `Date` | `string` | Trading date represented using mixed textual formats. |
| `Open` | `double` | Opening price. |
| `High` | `double` | Highest price during the day. |
| `Low` | `double` | Lowest price during the day. |
| `Close` | `double` | Closing price. |
| `Adj Close` | `double` | Adjusted closing price. |
| `CloseUSD` | `double` | Closing price in US dollars. |

## Relationships and interpretation

`index_info.Exchange` stores full exchange names, whereas `index_trade.Index` stores index symbols. The tables do not expose a shared join key. Geographic regions are not stored as explicit columns.

`Date` remains a string column; parse its textual values when performing date-based analysis. No date normalization or new mapping columns were introduced during this layout migration.

Additional domain and calculation guidance is available in `context/hints.md` when enabled by the experiment configuration.
