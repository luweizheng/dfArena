## Context
The data comes from Our World in Data and is stored in 2 tables: Life Expectancy and List of Countries - Continents.

## Requirements
- Input the data
- Reshape the data so there is a field for the Country Life Expectancy for each Year, as well as a Continent Avg Life Expectancy field for each Year
- Filter the data to include only years from 1950 to 2020
- Determine the percentage of years (between 1950 and 2020) when a country’s life expectancy was higher than its continent’s average
- Compute the percentage change in life expectancy for each country between 1950 and 2020
- Show the top three countries in each continent with the highest percentage increase in life expectancy
- Round the results to the nearest one decimal place.
- Output the data

## Output

Each output row represents one selected country within its continent, together with its rank and two percentage metrics. The input files are `inputs/input_01.csv` (life expectancy) and `inputs/input_02.csv` (country-to-continent lookup).

- output_01.csv
  - 5 fields:
    - Continent
    - Rank
    - Country
    - % Years Above Continent Avg
    - % Change
