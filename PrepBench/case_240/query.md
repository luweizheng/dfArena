## Requirements

- Input the data but add a Row ID
- Try not to type in order in Excel as this is part of the challenge
- Pull the two tables together
- Use the file names to create a date
  - The input files have been renamed: `input_02.csv` corresponds to 1 July 2023, and `input_01.csv` corresponds to 1 August 2023. Use the corresponding date for every row from each file.
- Create a sequence ID for the first order through to the last
- Create a field to determine how the current order differed to the previous order
- Call this field 'Bigger Order?'
  - Compare each order only with the previous order for the same `Customer` and `Book`.
  - `Bigger Order?` is the numeric difference: the current `Quantity` minus that previous order's `Quantity`.
- Output the data

## Output

- output_01.csv
  - 6 fields:
    - Customer
    - Book
    - Date
    - Sequence ID
    - Quantity
    - Bigger Order?
