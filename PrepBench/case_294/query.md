## Requirements

- Input the data
- Create a row for each day a consultant is on the engagement, including both the start and end dates for the revenue calculation
- Remove weekend days
- Calculate Calendar Days as the whole-day difference between Engagement End Date and Engagement Start Date, including weekends; do not add 1.
- Aggregate the data to:
  - Retain the calculated Calendar Days value for each consultant engagement
  - The total earned by each individual per engagement
  - Retain the engagement number, initials and grade
- Rank the consultants by day rate earned, per engagement:
  - Overall rank
  - Grade rank
- Output the data

## Output

`inputs/input_01.csv` contains consultant engagements. `output_01.csv` contains one row per Initials / Engagement Order / Grade Name combination with retained working days. The output Day Rate column contains total earned revenue for that engagement.

- output_01.csv
  - 7 fields:
    - Calendar Days
    - Initials
    - Engagement Order
    - Grade Name
    - Day Rate
    - Overall Rank
    - Grade Rank
