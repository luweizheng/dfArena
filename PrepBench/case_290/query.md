## Requirements

- Input the data
- Add in a row number as at source (this will help for next week's challenge)
- Create a column to show which Matchday (ie which game in the 38 game season) each game occurred in
- Remove any rows of the data set that don't contain game information
- It's helpful to put all the match information in one column rather than the two columns in the input
- Replace the new row character (\n) with a different character(s) (I use two pipe characters: ||)
- Form separate columns for:
  - Date
  - Home Score
  - Home Team
  - Away Score
  - Away Team
- Output the data

## Output

`inputs/input_01.csv` contains two columns of raw match text, including an initial matchday announcement. `output_01.csv` contains one row per match.

- output_01.csv
  - 7 fields:
    - Away Score
    - Away Team
    - Home Score
    - Home Team
    - Matchday
    - Source Row Number
    - Date
