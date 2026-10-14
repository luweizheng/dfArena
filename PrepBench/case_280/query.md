## Requirements

- Input the data
- Split the Complaint Description field into:
  - Product ID
  - Issue Type
  - Complaint Description (the text the customer wrote to describe the complaint)
- Extract the first 2 letters of the Product ID as this represents the Category Code
- Use this Category Code to join on the Product Category from the lookup table
- Filter the dataset to only contain rows where the Date Resolved happens after the Date Received
- Remove unnecessary fields
- Output the data

## Output

`inputs/input_01.csv` contains product categories; `inputs/input_02.csv` contains complaints. `output_01.csv` contains cleaned complaint records.

- output_01.csv
  - 11 fields:
    - Complaint ID
    - Receipt Number
    - Customer ID
    - Date Received
    - Date Resolved
    - Timely Response
    - Response to Consumer
    - Issue Type
    - Product Category
    - Product ID
    - Complaint Description
