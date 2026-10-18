## Context
This week's challenge sees us looking at the Accessory Sales at our Bike Store.
Input: Five CSV files share the same structure. The store sales files are `input_01.csv` (Manchester), `input_02.csv` (London), `input_03.csv` (Leeds), `input_04.csv` (York), and `input_05.csv` (Birmingham).

## Requirements

- Input the data
- Pivot 'New' columns and 'Existing' columns
- Split the former column headers to form:
  - Customer Type
  - Product
- Rename the measure created by the Pivot as 'Products Sold'
- Create a Store column from the data
- Remove any unnecessary data fields
- Turn Date into Quarter
- Aggregate to form two separate outputs of the number of products sold by:
  - Product, Quarter
  - Store, Customer Type, Product
- Output the data

## Output

- output_01.csv — products sold by Product and Quarter
  - 3 fields:
    - Product
    - Quarter
    - Products Sold

- output_02.csv — products sold by Store, Customer Types and Product
  - 4 fields:
    - Store
    - Customer Types
    - Product
    - Products Sold
