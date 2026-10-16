## Requirements

- Input the data
- Join both datasets on the Student ID
- Group Values by Spelling to get rid of spelling mistakes in the Nationality field
- Aggregate the dataset to get a count of students within each Nationality and classroom
- Create a calculated field to output the Rank of each Nationality by classroom in descending order
- Filter the Dataset to keep the first-ranking Nationality in each classroom
- Remove unnecessary fields
- Output the data

## Output

`inputs/input_01.csv` contains nationality and classroom; `input_02.csv` student names. `output_01.csv` has one row per classroom. The field `Name` means the count of distinct students, not a personal name.

- output_01.csv
  - 3 fields:
    - Nationality
    - Classroom
    - Name
