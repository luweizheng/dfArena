## Requirements

- Input the data
- Pull a list of clients purchases together across all their regions
- Treat each input file as a separate region source:
  - `input_01.csv` -> `Central`
  - `input_02.csv` -> `East`
  - `input_03.csv` -> `North`
  - `input_04.csv` -> `South`
  - `input_05.csv` -> `West`
- Parse `Order Date` using day/month/year (`%d/%m/%Y`).
- Determine the % of total sales each transaction makes up:
  - In Region, for the same Stock
  - Across the whole firm, for the same Stock
- The final file should only contain sales that are not the only purchase of that share.
- Output the data

## Output formatting

- Round `% of Regional Sales` and `% of Total Sales` to 9 decimal places.
- Round `Sales`, `Total Regional Sales`, and `Total Sales` to 2 decimal places.
- Output `Order Date` in `DD/MM/YYYY` format.

## Output

- output_01.csv
  - 11 fields:
    - % of Regional Sales
    - % of Total Sales
    - Region
    - Customer ID
    - First Name
    - Last Name
    - Sales
    - Order Date
    - Stock
    - Total Regional Sales
    - Total Sales
