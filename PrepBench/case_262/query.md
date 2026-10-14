## Context
The goal is to count the number of Valentine's Days each couple has been together to assign gift ideas based on the length of their relationship (gift ideas referenced from https://www.theknot.com/content/milestone-anniversary-gift-ideas).

## Requirements
- Input the data
- Fix the Relationship Start field so that it has a Date data type
- Create a field for today's date (14/02/2024)
- To count the number of Valentine's days, use a method other than simple datediff (e.g., scaffolding rows per day and filtering Valentine's days, or a logical calculation considering if the relationship start date is before or after Valentine's Day)
- Make the Year field match the data type of the Number of Valentine's field to prepare for joining with the Gift ideas dataset
- Join the two datasets together
- Remove unnecessary fields
- Sort the final output ascending by:
  1) `Number of Valentine's Days as a Couple`
  2) `Couple`
- Output the data

## Output

`inputs/input_01.csv` contains couples and relationship dates; `input_02.csv` provides the gift lookup. `output_01.csv` reports couple names, the number of Valentine's Days together, and the corresponding gift.

- output_01.csv
  - 3 fields:
    - Couple
    - Number of Valentine's Days as a Couple
    - Gift
