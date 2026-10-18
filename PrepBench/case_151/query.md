## Context
Two CSV input files: input_01.csv contains Complaints, and input_02.csv contains Department Responsible.

## Requirements

- Input the data
- Count the number of complaints per customer
- Join the 'Department Responsible' data set to allocate the complaints to the correct department
- Create a comma-separated field for all the keywords found in the complaint for each department
- For any complaint that isn't classified, class the department as 'Unknown' and the complaint cause as 'other'
- Output the data

## Output

- output_01.csv
  - 5 fields:
    - Complaint
    - Complaints per Person
    - Complaint causes
    - Department
    - Name
