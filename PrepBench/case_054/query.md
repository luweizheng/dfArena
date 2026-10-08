## Context
The supplied CSV input files contain multiple weeks of sales data and a separate planning table from our Financial Planner, Jules. Consolidate the weekly sales and clean the planning data to compare actual performance with profit minimums and budgets.

## Requirements
- Input the data
- Pull all the weekly sales input files together
- Form weekly sales volume and value figures per product
- Prepare the data in the Profit table for comparison against the actual volumes and values
- Join the tables but only bring back those that have exceeded their Profit Min points for both Value and Volume
- Prepare the Budget Volumes and Values for comparison against the actual volumes and values
- Join the tables but only return those that haven't reached the budget expected for either Value or Volume
- Prepare the outputs
- Output the data. Make sure to remove duplicates.

## Output

- output_01.csv
  - 6 fields:
    - Type
    - Week
    - Sales Volume
    - Budget Volume
    - Sales Value
    - Budget Value

- output_02.csv
  - 6 fields:
    - Type
    - Week
    - Sales Volume
    - Sales Value
    - Profit Min Sales Volume
    - Profit Min Sales Value
