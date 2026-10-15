## Context
It's the final week of beginner month, focusing on joins, calculations, and multiple outputs. Prep Air wants a workflow with outputs addressing:
- Details of customers who booked flights and their routes
- Customers yet to book in 2024
- Flights yet to be booked in 2024
Datasets are large; decide which tables to join (and when) for efficiency.

## Requirements
- Input the data
- For the first output: Create a dataset that gives all the customer details for booked flights in 2024, including flight origin and destination
- For the first output: Write the data to `output_01.csv`.
- Output date fields as YYYY-MM-DD text where applicable (Date, Last Date Flown, and the datestamp field)
- For the second output: Create a dataset that allows Prep Air to identify which flights have not yet been booked in 2024
- For the second output: Add a datestamp field to this dataset for 31/01/2024
- For the second output: Write the data to `output_02.csv`.
- For the third output: Create a dataset that shows which customers have yet to book a flight with Prep Air in 2024
- For the third output: Create a "Days Since Last Flown" field (compared to 31/01/2024)
- For the third output: Categorize customers into the following groups:
  - Recent fliers - 90 days or less since last flight
  - Taking a break - 91-180 days since last flight (inclusive)
  - Been away a while - 181-270 days since last flight (inclusive)
  - Lapsed Customers - more than 270 days since last flight
- Output the data

## Output

- output_01.csv
  - 11 fields:
    - Date
    - From
    - To
    - Flight Number
    - Customer ID
    - Last Date Flown
    - first_name
    - last_name
    - email
    - gender
    - Ticket Price

- output_02.csv
  - 5 fields:
    - Flights unbooked as of
    - Date
    - Flight Number
    - From
    - To

- output_03.csv
  - 8 fields:
    - Customer ID
    - Customer Category
    - Days Since Last Flown
    - Last Date Flown
    - first_name
    - last_name
    - email
    - gender
