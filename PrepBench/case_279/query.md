## Context
Manager salaries at SuperBytes are paid weekly. Salaries are consistent throughout a given manager’s employment, but may change when a manager is replaced. SuperBytes wants to know two things:
1. How much have they been spending on manager salaries each week since the company’s founding?
2. What percentage of annual expenses is going to manager salaries?

## Requirements
- Input the data
- Set the end date for current employees as 12th June 2024
- Calculate the weekly salary of each manager (assuming 52 weeks in the year)
- For each manager, create a row for every week they receive their salary
- For the first output:
  - Total up the amount SuperBytes pays Manager Salaries each week
  - Round this value to 2 decimal places
- For the second output:
  - Workout how much SuperBytes spends on Manager Salaries each year
  - Compare this to the total expenses for the company each year
  - Calculate the % Spent on Manager Salaries rounded to 1 decimal place
- Sort the weekly output by Week ascending and the annual output by Year ascending.
- Output the data

## Output

`inputs/input_01.csv` contains manager tenure and annual salary; `input_02.csv` annual company expenses. `output_01.csv` contains one row per weekly payment date; `output_02.csv` one row per overlapping calendar year.

- output_01.csv
  - 2 fields:
    - Week
    - Salary Payments

- output_02.csv
  - 2 fields:
    - Year
    - % Spent on Manager Salaries
