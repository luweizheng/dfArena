## Requirements

- Input the data
- Union the files together
- Convert the Date field to a Quarter Number instead; name this field Quarter
- Aggregate the data in the following ways:
  - Median price per Quarter, Flow Card? and Class
  - Minimum price per Quarter, Flow Card? and Class
  - Maximum price per Quarter, Flow Card? and Class
- Create three separate flows where each has only one aggregated measure:
  - One for the minimum price
  - One for the median price
  - One for the maximum price
- Pivot the data to have a column per class for each quarter and Flow Card? status
- Union these three flows back together by stacking rows in this block order: median first, maximum second, minimum third.
- Within each block, use this exact (Flow Card?, Quarter) row order: (Yes, 2), (No, 1), (No, 4), (Yes, 3), (Yes, 1), (No, 2), (No, 3), (Yes, 4).
- Keep the six output columns below; do not add an aggregation-label column. The block position identifies the aggregation measure.
- Change the column names due to incorrect classification:
  - Economy → First
  - First Class → Economy
  - Business Class → Premium
  - Premium Economy → Business
- Output the data

## Output

- output_01.csv
  - 6 fields:
    - Flow Card?
    - Quarter
    - Economy
    - Premium
    - Business
    - First
