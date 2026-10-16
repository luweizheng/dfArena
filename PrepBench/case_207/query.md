## Context
Data Source Bank acquires new customers every month. They are stored in separate tabs of an Excel workbook so it's "easy" to see which customers joined in which month. However, it's not so easy to do any comparisons between months. Therefore, we'd like to consolidate all the months into one dataset. There's an extra twist as well. The customer demographics are stored as rows rather than columns, which doesn't make for very easy reading. So we'd also like to restructure the data.

## Requirements

- Input the data
- Stack (union) the monthly input tables on top of one another, aligning corresponding fields.
- Some of the fields aren't matching up as we'd expect, due to differences in spelling. Merge these fields together
- Make a Joining Date field based on the Joining Day, Table Names and the year 2023
  - The monthly tables are supplied as CSV files with anonymized names. Use the following source-file-to-month mapping:
  - `input_01.csv` = April (04)
  - `input_02.csv` = August (08)
  - `input_03.csv` = December (12)
  - `input_04.csv` = February (02)
  - `input_05.csv` = January (01)
  - `input_06.csv` = July (07)
  - `input_07.csv` = June (06)
  - `input_08.csv` = March (03)
  - `input_09.csv` = May (05)
  - `input_10.csv` = November (11)
  - `input_11.csv` = October (10)
  - `input_12.csv` = September (09)
- Now we want to reshape our data so we have a field for each demographic, for each new customer
- Make sure all the data types are correct for each field
- Remove duplicates:
  - If a customer appears multiple times take their earliest joining date
- Output the data

## Output

- output_01.csv
  - 5 fields:
    - ID
    - Joining Date
    - Account Type
    - Date of Birth
    - Ethnicity
