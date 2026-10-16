## Requirements

- Input the data
- We only want to consider complete months so filter values up to June 2023
- The values after July 2023 are forecasted values
- Aggregated the data to a monthly level for each Store and Bike Type
- Notice how not every Bike Type has a sale in every Store each Month. We need to scaffold the data:
  - Find the Next Sale Month for each Store and Bike Type
  - You will have nulls for the most recent Month. Replace these nulls with the most recent date in the dataset (June 2023)
  - Fill in the missing Months without introducing duplicate rows.
  - For the months which have been filled in, make sure the value for the Sales and Profit is 0
- Calculate the 3 month Moving Average for the Profit for each Store and Bike Type
- Output the data to `output_01.csv`.

## Output

- output_01.csv
  - 6 fields:
    - Month
    - Store
    - Bike Type
    - Sales
    - Profit
    - 3 Month Moving Average Profit
