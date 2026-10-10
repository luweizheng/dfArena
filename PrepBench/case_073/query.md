## Requirements

- Input the data
- Find a way to join all three tables together
- Identify which locations would be suitable for each person
- Watch out for any duplicated person & site combinations
- Rank the top sites in terms of rating for each person. If there is a tie, then use the reliability metric where:
  - Rarely Breaks (Worst)
  - Inconsistent
  - Fairly Inconsistent
  - Fairly Consistent
  - Very Consistent (Best)
- Output the data

## Output

Each output row is a person–site recommendation, containing the person’s Name and the site attributes listed below.

- output_01.csv
  - 10 fields:
    - Name
    - Surf Site
    - Swell Direction
    - Reliability
    - Wind Direction
    - Type
    - Boards
    - Skill Level
    - Surf Season
    - Rating
