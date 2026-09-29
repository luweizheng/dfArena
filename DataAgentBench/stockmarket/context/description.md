# stockmarket

This dataset exposes the original two database groups as local Parquet tables.

Original group names below are retained to interpret the original hints. All file paths are relative to the dataset root.

1. stockinfo_database
   - This table group is stored in Parquet files and contains metadata about publicly traded stocks and ETFs listed on U.S. exchanges, including ticker symbols, market categories, trading venues, and company descriptions.
   - This database consists of one table: 
    - stockinfo:
      - Fields:
        - Nasdaq Traded (str): Whether stock is traded on NASDAQ
        - Symbol (str): Stock ticker symbol
        - Listing Exchange (str): Exchange where stock is listed
        - Market Category (str): Market category classification
        - ETF (str): Whether security is an ETF
        - Round Lot Size (float): Standard trading unit size
        - Test Issue (str): Whether this is a test issue
        - Financial Status (str or null): Financial status (delinquent, deficient, etc.)
        - NextShares (str): NextShares designation
        - Company Description (str): Company name and description

2. stocktrade_database
   - This table group is stored in Parquet files and contains daily price data for 2,753 individual stocks and ETFs listed on U.S. exchanges. Each original table is named after a stock's ticker symbol and contains the historical daily trading data for that stock.
   - Fields (for each table):
     - Date (str): Trading date
     - Open (float): Opening price
     - High (float): Highest price during the day
     - Low (float): Lowest price during the day
     - Close (float): Closing price
     - Adj Close (float): Adjusted closing price
     - Volume (int64 or double, depending on table): Number of shares traded

## Files and physical types

The stock metadata table is `data/stockinfo/stockinfo.parquet`. Price tables are `data/stocktrade/<original-table-name>.parquet`. The sole reserved-filename exception is original table `PRN`, stored in `data/stocktrade/PRN__table.parquet` for Windows compatibility. Its original table name remains `PRN` in metadata.yaml.

Each price table retains its original columns and types: Date is string; price columns are double. Volume is double in the following tables and int64 in all other price tables: `ADP`, `BPOPN`, `CAE`, `CMA`, `CMI`, `EDOW`, `EINC`, `EV`, `FTFT`, `FTR`, `GLT`, `GOGL`, `GTY`, `JBHT`, `JKL`, `KLR`, `LB`, `MFSF`, `MS`, `NICK`, `NIU`, `PGR`, `PSM`, `REGL`, `RETL`, `RHS`, `RPV`, `SBR`, `SDOW`, `SHAG`, `SJT`, `SYBT`, `TDV`, `UBOH`, `UHT`, `VHI`, `WOR`, `XRAY`.

The Round Lot Size column in stockinfo is double; its other columns are strings. There are 2,752 metadata rows and 2,753 price tables. The original `CARR#` price table has no matching stockinfo Symbol; it is retained under `data/stocktrade/CARR#.parquet` without guessing a replacement symbol.

## Preservation

All original records, duplicates, nulls, empty strings, and text formatting are retained. Dates remain strings; numeric values are not rounded. No joins, deduplication, missing-value imputation, or ground-truth computation are performed. metadata.yaml lists every table with its original name, exact local path, physical column types, row count, and checksum. Additional original hints are in context/hints.md when enabled by the experiment.
