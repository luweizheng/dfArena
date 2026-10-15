## Requirements

- Input the data
- Separate the Project Name from the financial transactions in the Project Field
  - Financial Transactions have either *Invoice* or *Expense* in the name
- Fill in the field if there are any nulls
- Remove any Project Name rows that don't contain any Cost or Invoiced Amounts
- Total Expense and Invoiced Amounts per Project
- Work out Profit per project (Invoiced Amounts minus Expenses)
- Output the data

## Output

`inputs/input_01.csv` mixes project headers and transaction lines. `output_01.csv` has one row per project with total invoiced amount, cost and profit.

- output_01.csv
  - 4 fields:
    - Project Name
    - Invoiced Amount
    - Cost
    - Profit
