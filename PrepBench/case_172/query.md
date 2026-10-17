## Requirements

- Input the data
- Bring together the Key Metrics tables from each Shop
- You'll notice that we have fields which report the quarter in addition to the monthly values. We only wish to keep the monthly values
- Reshape the data so that we have a Date field
- For Orders and Returns, we are only interested in reporting % values, whilst for Complaints we are only interested in the # Received
- We wish to update the Breakdown field to include the Department to make the Measure Name easier to interpret
- We wish to have a field for each of the measures rather than a row per measure
- We wish to have the targets for each measure as field that we can compare each measure to
- Output the data


Input file identities: `input_01.csv` = Bath; `input_02.csv` = Bristol; `input_03.csv` = Exmouth; `input_04.csv` = Hastings; `input_05.csv` = Leicester; `input_06.csv` = Newcastle; `input_07.csv` = Nottingham; `input_08.csv` = Plymouth; `input_09.csv` = Portsmouth; `input_10.csv` = Reading; `input_11.csv` = Southampton; `input_12.csv` = Torquay.

## Output

- output_01.csv
  - 12 fields:
    - Shop
    - Date
    - % Orders Shipped in 3 days
    - Target - % Orders Shipped in 3 days
    - % Orders Shipped in 5 days
    - Target - % Orders Shipped in 5 days
    - % Returns Processed in 3 days
    - Target - % Returns Processed in 3 days
    - % Returns Processed in 5 days
    - Target - % Returns Processed in 5 days
    - # Complaints Received
    - Target - # Complaints Received
