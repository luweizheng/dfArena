## Context
This week's challenge involves picking up some more of the fundamental skills and gives you some chances to practice some of the skills you've picked up over the last few weeks. The new technique for you to learn this week is Joins. Joins allow us to bring two data sources together. This allows for much easier, richer and deeper analysis as data is often in many different locations. The store sales files are `input_01.csv` (Manchester), `input_02.csv` (London), `input_03.csv` (Leeds), `input_04.csv` (York), and `input_05.csv` (Birmingham). Quarterly targets are supplied in `input_06.csv`.

## Requirements

- Input the data
- Union the Stores data together
- Add a Store field using the file-to-store mapping above and remove unnecessary fields
- Pivot the product columns
- Split the 'Customer Type - Product' field to create:
  - Customer Type
  - Product
  - Also rename the Values column resulting from you pivot as 'Products Sold'
- Turn the date into a 'Quarter' number
- Sum up the products sold by Store and Quarter
- Add the Targets data
- Join the Targets data with the aggregated Stores data
  - Note: this should give you 20 rows of data
- Remove any duplicate fields formed by the Join
- Calculate the Variance between each Store's Quarterly actual sales and the target. Call this field 'Variance to Target'
- Rank the Store's based on the Variance to Target in each quarter
  - The greater the variance the better the rank
- Output the data

## Output

- output_01.csv — sales, targets, variance and rank for each store and quarter
  - 6 fields:
    - Quarter
    - Rank
    - Store
    - Products Sold
    - Target
    - Variance to Target
