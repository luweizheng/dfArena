## Context
There are 3 inputs this week: Host Countries, the history of all the medallists for each Olympics, a country codes lookup table.

## Requirements

- Input the data
  - Parse slash-separated host dates as `MM/DD/YYYY` and year-first host dates as `YYYY-DD-MM`, ignoring any time component. Output dates as `DD/MM/YYYY` and derive Year from Start Date.
- Make sure every medal has both a Country and Country Code associated with it
- Group together Canoe/Kayak and Canoeing Sports
- Group together sensible Disciplines
  - For rows where Sport is `Cycling`, set Discipline to `Cycling Track` if any of these conditions holds:
    - Discipline contains `Track cycling`, `Cycling Track`, `Road cycling`, or `Cycling Road`.
    - Year ≤ 1992.
    - Event contains `road race` or `time trial`.
  - Match these text patterns case-insensitively. Otherwise, retain Discipline after applying the other specified renames.
- Replace the word "metres"/"metre" in Events with an "m" abbreviation
  - For Athletics events, use exactly one space between a numeric distance and the metre unit m in every year, including already abbreviated values and relay distances: 100 metres → 100 m, 100m → 100 m, and 4×100m relay → 4×100 m relay. This rule concerns the metre unit only; existing kilometre rules and relay x/× conventions remain separate.
- Use ` x ` between swimming relay distances, e.g. `4×100m` → `4 x 100m`.
- Standardize metre spacing in Shooting events, e.g. `50m pistol` → `50 m pistol`.

- Replace the word "kilometres" in Events with an "km" abbreviation
- Change Sport from Swimming to Aquatics
- Output cleaned Medallists Dataset
- Aggregate to a row for each Event medal (i.e. we know longer need the Athlete names Level of Detail)
- Create a table showing total Gold, Silver and Bronze medals from each country for each year
- Output Country Medals Dataset
- Using the Hosts dataset, create a field for the Host Country
- Change the United Kingdom to Great Britain
- Output Host Cities Dataset
- Output the data
  - Remove exact duplicate records from the cleaned Medallists Dataset.

## Output

- output_01.csv
  - 5 fields:
    - Country
    - Gold
    - Silver
    - Bronze
    - Year

- output_02.csv
  - 9 fields:
    - Year
    - Host City
    - Host Country
    - Start Date
    - End Date
    - Games
    - Nations
    - Sports
    - Events

- output_03.csv
  - 9 fields:
    - Country
    - Code
    - Sport
    - Medal
    - Event
    - Athlete
    - Year
    - Event_Gender
    - Discipline
