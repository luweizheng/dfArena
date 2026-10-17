## Requirements

- Input the data
- Combine the files
- Keep only relevant fields
- Extract the Report years from the file paths
- Create a Year field based on the the first year in the Report name
- Some companies have changed names over the years. For each EmployerId, find the most recent report they submitted and apply this EmployerName across all reports they've submitted
- Create a Pay Gap field to explain the pay gap in plain English
- You may encounter floating point inaccuracies. Find out more about how to resolve them
- In this dataset, a positive DiffMedianHourlyPercent means the women's pay is lower than the men's pay, whilst a negative value indicates the other way around
- The phrasing should be as follows:
  - In this organisation, women's median hourly pay is X% higher/lower than men's.
  - In this organisation, men's and women's median hourly pay is equal.
- Output the data，deduplicate records to avoid duplicate rows affecting evaluation


Input reporting periods: `input_01.csv` = 2017 to 2018; `input_02.csv` = 2018 to 2019; `input_03.csv` = 2019 to 2020; `input_04.csv` = 2020 to 2021; `input_05.csv` = 2021 to 2022.

## Output

- output_01.csv
  - 7 fields:
    - Year
    - Report
    - EmployerName
    - EmployerId
    - EmployerSize
    - DiffMedianHourlyPercent
    - Pay Gap
