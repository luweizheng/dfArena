## Context
The goal is to identify the worst-selling items within each product category (with particular focus on home, groceries, beauty, electronics, and clothes) by comparing each item’s sales contribution against the total sales for its category. The result should retain only those items that collectively account for the bottom 15% of sales within each category.

## Requirements
- Input the data from `input_01.csv`.
- Treat each input record as an individual product sales record and compute its sales value:
  - Create a `Sales` field as `Price * Quantity`.
- Trim incidental surrounding whitespace from Category before grouping.
- Calculate total sales at the category level:
  - Group by `Category` and compute `Category Total Sales` as the sum of `Sales` within each category.
  - Attach (join/merge) `Category Total Sales` back onto each original record by matching on `Category` (left join so all original records are retained prior to filtering).
- Work out the percentage of total for each record within its category:
  - Compute `% of Total` as `Sales / Category Total Sales` (a decimal proportion, not multiplied by 100).
- Identify the records that make up the bottom 15% of each category’s sales:
  - Within each `Category`, sort records by `Sales` ascending (worst sellers first).
  - Compute `Cumulative %` within each `Category` as the cumulative sum of `% of Total` following that ascending-`Sales` order, without rounding the proportions first.
  - Filter to records where `Cumulative % <= 0.15` (inclusive).
- Remove unnecessary fields and format for output:
  - Keep only: `Category`, `Product`, `Product ID`, `Price`, `Sales`, `% of Total`.
  - The original request does not require output rounding: `% of Total` may be given to two decimal places or at higher precision. Differences up to 0.005 from the two-decimal reference output are accepted; keep the fraction scale.
  - No particular final output row or column order is required; the calculation order above is still necessary.
- Output the data to the required file.

## Output

`inputs/input_01.csv` contains product sales records. `output_01.csv` contains the selected worst-selling product records within each category.

- output_01.csv
  - 6 fields:
    - Category
    - Product
    - Product ID
    - Price
    - Sales
    - % of Total

Equivalent numeric notation is accepted. Sales comparisons allow only 1e-12 of floating-point serialization error. Incidental output Category capitalization and surrounding/repeated whitespace are equivalent; preserve meaningful category distinctions and product names.
