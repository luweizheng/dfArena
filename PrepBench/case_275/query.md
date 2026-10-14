## Context
This week's challenge focuses on SuperBytes customers, specifically identifying which customers spent the most on different days of the week last year. The input data contains two sheets: one with transaction details and another with customer names and IDs.

## Requirements
- Input the data
- Join sheets then remove names and maintain privacy
- Group Online and In Person into one field
- Add a field for the day of the week the transaction was completed
- Rank sales for each weekday
- Create a parameter to output a data set for each day of the week
- Include the selected weekday in the Weekday output field
- Sort the final output by Sales descending, then Receipt Number ascending.
- Output the data for Monday

## Output

`inputs/input_01.csv` contains customer identifiers; `input_02.csv` transactions. `output_01.csv` has one row per Monday transaction. Channel labels are `Online` and `In-Person`; the Weekday label is `Monday`.

- output_01.csv
  - 7 fields:
    - Rank
    - Customer ID
    - Receipt Number
    - Gender
    - Online or In Person
    - Sales
    - Weekday
