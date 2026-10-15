## Context
- The input data is a single spreadsheet containing three sheets: salaries, tenure, and amount paid.
- All managers have received paychecks up to 5th June 2024 (present date).

## Requirements
- Input the data
- Clean the manager names in the Salaries and Tenures sheets so they match
- Bring together the Salaries and Tenures datasets
- Calculate the tenure (number of days) of each manager’s employment
  - Hint: For current employees, see what happens when you change the datatype of “End Date”
  - For the output, the End Date for current employees is set to 5th June 2024
- Using salary and tenure, calculate the Expected Total Salary of each manager (rounded to the nearest whole number)
  - Use half-to-even rounding: an exact midpoint rounds to the nearest even integer (for example, 100.5 becomes 100 and 101.5 becomes 102).
- Join the data from the Amount Paid sheet
- Filter the output table to include only current managers whose pay received does not match their expected pay. A manager is current when the original End Date is "current", ignoring letter case and surrounding whitespace. Exclude former managers, even when their pay received differs from expected pay.
- Remove unnecessary fields
- Output the data

## Output

- output_01.csv
  - 4 fields:
    - Name
    - Salary
    - Expected Total Salary
    - Amount Paid
