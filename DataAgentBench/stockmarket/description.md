# stockmarket

The original two database groups are provided as local Parquet tables. Original group names are retained for interpreting the original hints. All file paths are relative to this dataset root.

## stockinfo_database

### stockinfo

Metadata about publicly traded stocks and ETFs listed on U.S. exchanges, including ticker symbols, market categories, trading venues, and company descriptions. This table contains 2,752 rows.

File: `data/stockinfo/stockinfo.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `Nasdaq Traded` | string | Whether stock is traded on NASDAQ |
| `Symbol` | string | Stock ticker symbol |
| `Listing Exchange` | string | Exchange where stock is listed |
| `Market Category` | string | Market category classification |
| `ETF` | string | Whether security is an ETF |
| `Round Lot Size` | double | Standard trading unit size |
| `Test Issue` | string | Whether this is a test issue |
| `Financial Status` | string | Financial status (delinquent, deficient, etc.); may be null |
| `NextShares` | string | NextShares designation |
| `Company Description` | string | Company name and description |

## stocktrade_database

### Price tables

Daily price data for 2,753 individual stocks and ETFs listed on U.S. exchanges. Each original table is named after a stock's ticker symbol and contains its historical daily trading data. All price tables use the schema below.

File: `data/stocktrade/<original-table-name>.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `Date` | string | Trading date |
| `Open` | double | Opening price |
| `High` | double | Highest price during the day |
| `Low` | double | Lowest price during the day |
| `Close` | double | Closing price |
| `Adj Close` | double | Adjusted closing price |
| `Volume` | int64 or double (see exceptions below) | Number of shares traded |

Volume is double in the following tables and int64 in all other price tables: `ADP`, `BPOPN`, `CAE`, `CMA`, `CMI`, `EDOW`, `EINC`, `EV`, `FTFT`, `FTR`, `GLT`, `GOGL`, `GTY`, `JBHT`, `JKL`, `KLR`, `LB`, `MFSF`, `MS`, `NICK`, `NIU`, `PGR`, `PSM`, `REGL`, `RETL`, `RHS`, `RPV`, `SBR`, `SDOW`, `SHAG`, `SJT`, `SYBT`, `TDV`, `UBOH`, `UHT`, `VHI`, `WOR`, `XRAY`.

The sole reserved-filename exception is original table `PRN`, stored in `data/stocktrade/PRN__table.parquet` for Windows compatibility. The original `CARR#` price table has no matching stockinfo Symbol; it is retained under `data/stocktrade/CARR#.parquet` without guessing a replacement symbol.

Additional hints are in hints.md when enabled by the experiment.
