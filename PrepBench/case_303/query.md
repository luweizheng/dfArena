## Requirements

- Input the data
- Name the field used to rank each league table 'Ranking Field'
  - Wins for NBA and NFL
  - Points for Rugby Aviva Premiership and Premier League
- Name and / or calculate First and Second Tie Breaking Fields For each sport.
  - Premier League: Tie Breaker 1 = Wins, Tie Breaker 2 = Goals Scored
  - NFL: Tie Breaker 1 = Points Differential, Tie Breaker 2 = Points For
    - Points Differential = Points For - Points Against
  - NBA: Tie Breaker 1 = Conference Wins, Tie Breaker 2 = Games Behind
    - The Conference Record Field is structured Wins-Losses
  - Rugby: Tie Breaker 1 = Wins (W), Tie Breaker 2 = Points Differential (PD)
- Make sure all the data types are accurate
- Bring all the tables together into one dataset
- Use the source-to-sport mapping: `inputs/input_01.csv` = `NBA`, `inputs/input_02.csv` = `NFL`, `inputs/input_03.csv` = `Premier League`, and `inputs/input_04.csv` = `Rugby Aviva Premiership`.
- Calculate the Rank of each team within their own sport using the specified tie breaking fields. If all ranking fields are equal, teams share the same rank and subsequent ranks skip tied positions (for example, 1, 2, 2, 4).
- Calculate the z-score for each team within their sport
    $$z=\cfrac{x-u}{o}$$
  - x=Ranking Field
  - u=Mean of Ranking Field within sport
  - o=Standard Deviation of Ranking Field within sport
- Calculate a Sport Specific Percentile Rank
    $$\text{Sport Specific Percentile Rank}=1-\cfrac{\text{Sport Specific Rank}}{\text{Number of Team in Sport}}$$
- Create a Cross Sport Rank based on the z-scores and using the Sport Specific Percentile Rank to break ties
- Remove unnecessary fields
- Output the data

## Output

Use the sport labels `NBA`, `NFL`, `Premier League`, and `Rugby Aviva Premiership`. `output_01.csv` contains one row per team and sport. `output_02.csv` contains one row per sport with the arithmetic mean of its teams’ Cross Sport Rank.

- output_01.csv
  - 6 fields:
    - Sport
    - Cross Sport Rank
    - Team
    - z-score
    - Ranking Field
    - Sport Specific Percentile Rank

- output_02.csv
  - 2 fields:
    - Sport
    - Avg Cross Sport Rank
