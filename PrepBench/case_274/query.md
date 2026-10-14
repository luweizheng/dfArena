## Context
The input data is a single spreadsheet containing 5 sheets (corresponding to years 2018-2022), each sheet includes sales and profit by quarter of the year.

## Requirements

- Input the data
- Union tables together
- Remove the units from the sales field to convert the data type to the whole number
- Repeat this process for the profits field
- Aggregate sales and profits by year
- Output the data

## Output

The five CSV inputs `inputs/input_01.csv` through `input_05.csv` correspond to 2018 through 2022, respectively. `output_01.csv` contains one row per year with annual totals.

- output_01.csv
  - 3 fields:
    - Year
    - Sales
    - Profits
