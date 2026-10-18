## Context
With the Prep Air - New Trolley Inventory project finally delivered at the end of May, we want to analyse what are the products that we are now selling for a much higher amount than we did before the project. We want to analyse the top five ranked purchase records based on price rise per destination.

## Requirements

- Input the data
- Combine all ten monthly input files. `input_01.csv` through `input_10.csv` correspond to January through October 2021, respectively.
- Use Day of Month and the input file's month and year to form the purchase date field 'Date'.
- Create 'New Trolley Inventory?' field to show whether the purchase was made on or after 1st June 2021 (the first date with the revised inventory after the project closed)
- Remove lots of the detail of the product name:
  - Only return any names before the '-' (hyphen)
  - If a product doesn't have a hyphen return the full product name
- Make price a numeric field
- Work out the average selling price per product
- Workout the Variance (difference) between the selling price and the average selling price
- Rank the Variances (1 being the largest positive variance) per destination and whether the product was sold before or after the new trolley inventory project delivery
- Return only ranks 1-5
- Output the data

## Output

- output_01.csv
  - 11 fields:
    - New Trolley Inventory?
    - Variance Rank by Destination
    - Variance
    - Avg Price per Product
    - Date
    - Product
    - first_name
    - last_name
    - email
    - Price
    - Destination
