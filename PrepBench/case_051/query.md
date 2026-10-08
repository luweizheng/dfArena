## Context

We want to understand at which venues England have been most dominant in the supplied rugby match results. The winner scores more points (For) than the opposition (Aga, short for against). Use Standard Competition ranking: for values 10, 9, 9, 8, the ranks are 1, 2, 2, 4 (rather than Modified Competition ranks 1, 3, 3, 4). Find each venue's best game rank, worst game rank and average rank based on the margin of victory / defeat.

## Requirements

- Input the data
- Remove the games that have null scores at halftime
- Determine the Standard Competition rank based on Diff (ie margin of victory - the larger the better)
- Using that rank give four statistics per venue:
  - Best game Rank per Venue
  - Worst game Rank per Venue
  - Average Rank per Venue
  - Number of Games played at that venue
- Output the data

## Output

- output_01.csv
  - 5 fields:
    - Venue
    - Number of Games
    - Best Rank (Standard Competition)
    - Worst Rank (Standard Competition)
    - Avg. Rank (Standard Competition)
