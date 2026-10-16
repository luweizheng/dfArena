## Context

Analyse AllChains store performance over the last financial year by calculating quarter-on-quarter sales changes and classifying each store's performance.

## Input month information

Each CSV corresponds to one monthly worksheet in the original source. The worksheet months are:

| Input file | Source month |
|---|---|
| `input_01.csv` | April |
| `input_02.csv` | August |
| `input_03.csv` | December |
| `input_04.csv` | February |
| `input_05.csv` | January |
| `input_06.csv` | July |
| `input_07.csv` | June |
| `input_08.csv` | March |
| `input_09.csv` | May |
| `input_10.csv` | November |
| `input_11.csv` | October |
| `input_12.csv` | September |

The weekday labels in the source date strings are unreliable. Construct Order Date using the source month listed below and the day and year from each date string; ignore the weekday label.

## Requirements

- Input the data
- Bring all the Months together into a single table
- Merge together misaligned fields
- Create an Order Date field
- The financial year for Allchains starts in July. Convert the dates to Fiscal Quarters
- Aggregate the data to a Quarterly level for each Store, ignoring the product details
- Calculate the % Difference in Sales from the Previous Quarter
  - Multiply this value by 100 and round to 1 decimal place
- Compare the quarter-on-quarter percentage changes for each Store across quarters in a single row
- Evaluate each Store's performance by categorising them in the following way:
  - If a Store has seen consistent growth - "Going from strength to strength"
  - If a Store has seen consistent decline - "Going from bad to worse"
  - If a Store has 1 negative Quarter:
    - In Q2 - "Good growth in last half"
    - In Q3 - "Some good growth, but concerns in Q3"
    - In Q4 - "Good growth, until Q4"
  - If a Store has only 1 positive Quarter:
    - In Q2 - "Concerning performance in last half"
    - In Q3 - "Concerning performance, excluding Q3"
    - In Q4 - "Concerning performance, but improving in Q4"
- Output the data

## Output

- output_01.csv
  - 5 fields:
    - Store
    - Quarter
    - Sales
    - % Difference Q on Q
    - Store Evaluation
