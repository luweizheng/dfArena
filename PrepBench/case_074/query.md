## Context
This challenge uses a messy version of a Summer Olympics dataset from Sports Viz Sunday. Two CSV input files are supplied:
1. `inputs/input_01.csv`: Summer Olympics host cities, the main table.
2. `inputs/input_02.csv`: a scaffold of positions that can help with the task.

## Requirements

- Input the data
- Convert the Roman numerals to numerical values
- Determine the Year of the Olympics
  - Each Roman numeral is four years apart even if the games wasn't held
- Create a Start Date for the Games (in M/D/YYYY format)
- Create an End Date for the Games (in M/D/YYYY format)
- Remove unnecessary fields
- Remove the null dates
- Output the data

## Output

Each row represents one Olympics edition with both dates present. Use the exact column names below.

- output_01.csv
  - 7 fields:
    - Start Date
    - End Date
    - Games
    - Host
    - Nations
    - Sports
    - Events
