## Context

Prepare a cleaned game schedule for the San Antonio Spurs using a DataFrame library. The input comes from ESPN-style schedule exports. Hi Points is the most points scored by a single player during the game; Hi Rebounds is the most rebounds recorded by a player; Hi Assists is the most assists recorded by a player. The cleaned table will support analysis of player performance in wins and losses, combinations of game leaders, and home and away games.

## Requirements

- Input the data
- Fix some date issues!
- Split the "Hi-" categories up so player and value is separate
- Determine whether each game was played by the Spurs: Home or Away
- Determine whether the Spurs won or lost each game
- Get rid of unrequired columns
- Output the data

## Output

- Use the exact column names listed below. Parenthetical text is part of the column name: `Opponent (clean)` must not be renamed to `Opponent`.
- Use `W` and `L` as the values of `Win or Loss`, and `Home` and `Away` as the values of `Home or Away`.

- output_01.csv
  - 13 fields:
    - Opponent (clean)
    - HI ASSISTS - Player
    - HI ASSISTS - Value
    - HI REBOUNDS - Player
    - HI REBOUNDS - Value
    - HI POINTS - Player
    - HI POINTS - Value
    - Win or Loss
    - Home or Away
    - True Date
    - OPPONENT
    - RESULT
    - W-L
