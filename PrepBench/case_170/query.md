## Context
This week's challenge brings back every Preppers' favourite retailer, Chin & Beard Suds Co (C&BSCo). The data team have raised an issue that sales are being made but the products sold are being recorded poorly. Each product sold is recorded but it seems the sales team in each store has been wrongly recording the size of the product. Each product in our range has a set size. Can you help prepare the data to show how bad the issue is? The input consists of three CSV files: `input_01.csv` contains the Product Set (full list of all products sold), `input_02.csv` contains Sales (sales recorded by Product, Store and Size ID), and `input_03.csv` contains the Size Table (lookup table for the Sales Size column).

## Requirements
- Input the data
- Change the Size ID to an actual Size value in the Sales table
- Link the Product Code to the Sales Table to provide the Scent information
- Create an Output that contains the products sold that have the sizes recorded correctly (Output1)
  - Deduplicate records to avoid duplicate rows affecting evaluation
- Create another data set that contains all the Products sold with the incorrect sizes and what the sizes should have been
  - Aggregate this data to show each Product Sold, the Scent and the Size it should be with how many sales have incorrectly been recorded for each.
  - Output this data (Output2)
- Output the data

## Output

- output_01.csv
  - 4 fields:
    - Product Size
    - Scent
    - Product
    - Store

- output_02.csv
  - 4 fields:
    - Sales with the wrong size
    - Product Code
    - Product Size
    - Scent
