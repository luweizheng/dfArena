## Requirements

- Input the data
- Input the Overview data from `inputs/input_04.csv`
- Each SDG is represented by two adjacent CSV columns: a colour indicator followed by its arrow/trend. Rename the arrow fields so it is clear which goals they are associated with.
- Reshape the data so that for each Country there is a row per SDG, containing information about the colour indicator and the arrow on the same row
- Rename the colour indicator field to SDG Value
- Rename the arrow field to be SDG Trend
- Update the SDG Values field:
  - Green - Goal Achieved
  - Yellow - Challenges Remaining
  - Orange - Significant Challenges
  - Red - Major Challenges
  - Grey - Insufficient
- Update the SDG Trend field:
  - ↑ - On Track
  - ➚ - Moderately Increasing
  - → - Stagnating
  - ↓ - Decreasing
- Output the data

## Output

- output_01.csv
  - 7 fields:
    - Country
    - 2023 SDG Index Score
    - 2023 SDG Index Rank
    - Regions used for the SDR
    - SDG Name
    - SDG Value
    - SDG Trend
