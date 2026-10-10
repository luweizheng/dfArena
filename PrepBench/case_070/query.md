## Context

There has been many a battle fought on British soil across the years and this website provides a lot of information about many of the battlefields. It's a great website to practice our webscraping skills, but webscraping doesn't always lead to the cleanest of datasets. So this week's focus will be on cleaning up a subset of our webscraped data.

## Requirements

- Input the data
- Find a natural way to split the data into different fields.
- Remove rows which are incomplete.
  - i.e. if they do not have information in each field.
- Clean battle names.
  - Ensure each row has a unique battle name.
- Clean the dates.
  - For those dates with a date range, just use the start date.
  - Parse the extracted date into a date value.
- Output the data

## Output

Each row describes one complete battle record. Use the exact column names below.

- output_01.csv
  - 5 fields:
    - Date
    - Battle
    - War
    - Victors
    - Description
