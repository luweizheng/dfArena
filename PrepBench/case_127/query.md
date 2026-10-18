## Context
The challenge this week is to analyse the all of the penalty shootouts in the World Cup and European Championships (Euro's) since 1976.

## Requirements

- Input the data: `input_01.csv` contains World Cup shootouts; `input_02.csv` contains Euros shootouts.
- Determine what competition each penalty was taken in
- Clean any fields, correctly format the date the penalty was taken, & group the two German countries (eg, West Germany & Germany)
- Rank the countries on the following:
  - Shootout win % (exclude teams who have never won a shootout)
  - Penalties scored %
- What is the most and least successful time to take a penalty? (What penalty number are you most likely to score or miss?)
- For all three outputs, round percentages to the nearest whole percent before ranking. Rank the rounded percentages in descending order using dense ranks: equal percentages share a rank, and the next distinct percentage receives the next rank (for example, 1, 1, 2).
- Output the data

## Output

- output_01.csv — country shootout win statistics
  - 5 fields:
    - Win % Rank
    - Shootout Win %
    - Total Shootouts
    - Shootouts
    - Team

- output_02.csv — statistics by penalty number
  - 6 fields:
    - Rank
    - Penalty Scored %
    - Penalties Scored
    - Penalties Missed
    - Total Penalties
    - Penalty Number

- output_03.csv — country penalty conversion statistics
  - 5 fields:
    - Penalties Scored %Rank
    - % Total Penalties Scored
    - Penalties Missed
    - Penalties Scored
    - Team
