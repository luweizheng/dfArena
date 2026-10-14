## Context
You are given yearly tables from Wikipedia’s “Forbes list of the world's highest-paid athletes” (one table per year) plus a separate source table. The objective is to standardize the schema across all yearly tables, convert earnings fields to numeric values, attach the source information to every row, and combine everything into one dataset suitable for time-based analysis.

## Requirements
- Input the data.
  - Use the 13 yearly input files as the year tables and the remaining input file as the source table.
- Bring all the year tables together into a single table.
  - Treat each input year table as having one row per athlete for that year.
  - Append (union/concatenate) the year tables into one combined table after standardizing their columns.
- Merge any mismatched fields.
  - Standardize column names across all year tables so the combined output has a consistent set of fields: Rank, Name, Sport, Country, Total earnings, Salary/Winnings, Endorsements.
  - Where different year tables use different headers for the same concept, map them into the same standardized output field before combining.
- Create a numeric Year field.
  - Add a Year column to each year table prior to combining, using the year associated with that table.
  - Ensure Year is numeric in the final output.
- Clean up the fields with the monetary amounts.
  - Convert the three earnings fields (Total earnings, Salary/Winnings, Endorsements) to numeric values.
  - Remove non-numeric symbols used as formatting (such as currency symbols and separators) before parsing.
  - Make sure that any value expressed in millions is translated to the full amount (e.g. “$6 million” becomes 6,000,000).
  - If a monetary value cannot be parsed into a number, leave it as null rather than inventing a value.
- Bring in the source information so that it is associated with each row.
  - Read the source value from the source input file and attach it to every row in the combined dataset as the Source field (i.e., the same Source value is repeated for all rows).
- Remove unnecessary fields.
  - Keep only the nine required output fields and drop everything else.
- Output the data.

## Output

`inputs/input_01.csv` through `inputs/input_13.csv` are the year tables for 2012 through 2024 respectively, in ascending year order. `inputs/input_14.csv` contains the source URL. `output_01.csv` contains one athlete-year record per input year-table row.

- output_01.csv
  - 9 fields:
    - Year
    - Rank
    - Name
    - Sport
    - Country
    - Total earnings
    - Salary/Winnings
    - Endorsements
    - Source

No particular final output row or column order is required. Numeric trailing zero padding is not required.
The supplied year-table monetary values are all parseable; schema unification must not introduce missing cells. Preserve each supplied amount independently, even if Total earnings differs from Salary/Winnings plus Endorsements. Do not silently correct source numbers.

Monetary outputs allow absolute floating-point serialization differences up to 0.000001 dollar, with no relative tolerance. This does not permit cent-level errors.
