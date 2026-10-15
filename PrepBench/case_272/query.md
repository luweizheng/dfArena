## Requirements

- Input the data
- Combine the Monthly sheets into a single table
- Exclude any area that is below budget at an annual level
- For the remaining areas, work out the difference between forecasted and actual expenditure on a monthly basis:
  - Spread the available budget numbers evenly across the year (since budget estimates were not prepared monthly)
  - Round both the monthly budget and monthly Actual Spending to the nearest whole number using round half to even: exact midpoints round to the nearest even integer (for example, 100.5 becomes 100 and 101.5 becomes 102). Calculate Difference by subtracting the rounded monthly budget from the rounded Actual Spending.
- For each month, find the category which has the highest overspending
  - If multiple categories tie for the highest overspending in a month, output only the first one in the combined input processing order (monthly-file processing order, then category order within each month).
- Output the data

## Output

- output_01.csv
  - 5 fields:
    - Month
    - Category
    - Actual Spending
    - Budget
    - Difference
