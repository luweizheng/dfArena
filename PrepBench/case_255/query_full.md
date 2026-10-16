## Context
You need to analyse historical challenge metadata to understand which techniques/themes have been used most often, and how usage varies by challenge level. The goal is to standardise inconsistent free-text theme labels into a consolidated set of techniques, then produce a priority view to guide future challenge creation.

## Requirements
- Input the data from `input_01.csv`.
- Treat each input record as a single challenge that includes:
  - `Level` (the challenge difficulty/category used for the level breakdown), and
  - `Themes` (a comma-separated list of themes/techniques applied in that challenge).
- Split the `Themes` field on commas so that each theme/technique becomes its own value.
  - After splitting, reshape the data to a long format so there is one row per (challenge, theme) combination.
  - Exclude rows where the resulting theme value is missing or empty.
- Group the themes together to account for inaccuracies by standardising theme values into consolidated technique names.
  - Apply a predefined, two-pass normalisation using mapping tables that convert known variants (e.g., plural vs singular, minor wording differences, and other inconsistencies) into canonical technique labels.
  - Any theme value not present in the mapping tables must remain unchanged.
- Aggregate to determine how many challenges each canonical `Technique` appears in, broken down by `Level`.
  - Count occurrences after the split/long reshape (i.e., count rows in the long data for each Technique–Level combination).
- Reshape to a wide format with one row per `Technique` and separate columns for the four levels:
  - `Beginner`, `Intermediate`, `Advanced`, and `3-in-1`.
  - If a level does not occur for a technique, leave that level column as null/missing (do not force it to zero).
- Create a `Total` field for each `Technique` equal to the sum of the four level columns, treating missing values as 0 for the purpose of this sum, and store `Total` as an integer.
- Rank techniques using `Priority` based on `Total` using a dense rank in ascending order (smallest `Total` gets `Priority` 1; ties share the same priority), and store `Priority` as an integer.
- Sort the final output by `Priority` ascending.
- Output the data.

## Theme classification rules

Trim surrounding whitespace from each split theme before normalization. Apply Pass 1 once, then apply Pass 2 once to the result of Pass 1. Each pass uses exact label matching; labels absent from that pass remain unchanged. These are the task's classification conventions, not claims that the underlying techniques are interchangeable. Do not make additional merges.

### Pass 1

| Source label | Replacement label |
| --- | --- |
| `Aggregate to deduplicate` | `Aggregate to Deduplicate` |
| `Merge Fields` | `Merge fields` |
| `Date calcs` | `Date Calcs` |
| `Date Calc` | `Date Calcs` |
| `String calculations` | `String Calculations` |
| `Moving average` | `Moving Average` |
| `% of total` | `% of Total` |
| `Fill Down` | `Fill down` |
| `Date Calculation` | `Date Calculations` |
| `Simple join` | `Simple Join` |
| `Simple Joins` | `Simple Join` |
| `Simple joins` | `Simple Join` |
| `Logical calcs` | `Logical Calcs` |
| `Logical calc` | `Logical Calcs` |
| `Pivot rows to cols` | `Pivot Rows to Cols` |
| `Pivot Rows to cols` | `Pivot Rows to Cols` |
| `Left Joins` | `Left Join` |
| `% Difference From` | `Difference From` |
| `<= Join clause` | `>= Join Clause` |
| `<= Join Clause` | `>= Join Clause` |
| `Wildcard union` | `Wildcard Union` |
| `Full Outer Join` | `Full outer join` |
| `Numeric calcs` | `Numeric Calcs` |
| `Numeric Calc` | `Numeric Calcs` |
| `Non-equal join clause` | `Non equal join clause` |
| `Non equal Join Clause` | `Non equal join clause` |
| `Non-equal Join Clause` | `Non equal join clause` |
| `Right only Join` | `Right Only Join` |
| `Joins` | `Join` |
| `Mutliptle Join Clause` | `Multiple Join Clause` |
| `Multiple join clause` | `Multiple Join Clause` |
| `Mutliple Join Clause` | `Multiple Join Clause` |
| `multiple join clause` | `Multiple Join Clause` |
| `Clean Step Only` | `Clean step only` |
| `Ranks` | `Rank` |
| `Multiple pivot` | `Multiple Pivot` |
| `Mutliple Pivot` | `Multiple Pivot` |
| `Date Conversions` | `Date Conversion` |
| `Data Interpretor` | `Data Interpreter` |
| `Data interpreter` | `Data Interpreter` |
| `IF Statements` | `IF statements` |
| `IF Statement` | `IF statements` |
| `IF statement` | `IF statements` |
| `ID statment` | `IF statements` |
| `IF Statments` | `IF statements` |
| `Appends` | `Append` |
| `String calcs` | `String Calcs` |
| `Parameters` | `Parameter` |
| `Left Only Join` | `Left only join` |
| `Left only Join` | `Left only join` |
| `Aggregates` | `Aggregate` |
| `Aggrgegate` | `Aggregate` |
| `Aggrgeate` | `Aggregate` |
| `Splits` | `Split` |
| `Right Joins` | `Right Join` |
| `Multiple clause Join` | `Multiple Clause Join` |
| `Multiple clause join` | `Multiple Clause Join` |
| `Mutiple Clause Join` | `Multiple Clause Join` |

### Pass 2

| Source label | Replacement label |
| --- | --- |
| `Pivot Cols` | `Pivot Cols to Rows` |
| `Wildcard Input` | `Wildcard Union` |
| `String functions` | `String Calcs` |
| `String Calculations` | `String Calcs` |
| `Scaffold` | `Scaffolding` |
| `Scaffolding (through all dimension combinations)` | `Scaffolding` |
| `Moving Calc` | `Moving Calculation` |
| `Moving Average` | `Moving Calculation` |
| `>= Join Clause` | `Non Equal Join Clause` |
| `Non equal join clause` | `Non Equal Join Clause` |
| `Non-equal Join Clause` | `Non Equal Join Clause` |
| `Non-equal Join Clause/Scaffolding` | `Non Equal Join Clause` |
| `Aggregation` | `Aggregate` |
| `Clean functions` | `Cleaning calcs` |
| `Convert Dates` | `Date Calcs` |
| `Create Date Field` | `Date Calcs` |
| `Date Calculations` | `Date Calcs` |
| `Date Conversion` | `Date Calcs` |
| `Date Functions` | `Date Calcs` |
| `Date Part` | `Date Calcs` |
| `Date Time Conversion` | `Date Calcs` |
| `Make Date` | `Date Calcs` |
| `Filling in blanks` | `Fill down` |
| `Fill down 2 fields` | `Fill down` |
| `Filter Duplicates` | `Filters` |
| `Filtering` | `Filters` |
| `Multi Clause Join` | `Multiple Join Clause` |
| `Multiple Clause Join` | `Multiple Join Clause` |
| `Join Practice` | `Join` |
| `Simple Join` | `Join` |
| `Right Join` | `Left Join` |
| `Right Only Join` | `Left only join` |
| `Lookup (but circular)` | `Lookup` |
| `Mathematical Calculations` | `Numeric Calcs` |
| `Merge` | `Merge fields` |
| `Multiple parameters` | `Parameter` |
| `Parameter in Output Name` | `Parameter` |
| `Parameter to Name Output` | `Parameter` |
| `Using Parameter in Output name` | `Parameter` |
| `Running Sum` | `Running Total` |
| `Updating a workflow` | `Update a workflow` |
| `Rename Values` | `Group Values` |

## Output

- output_01.csv
  - 7 fields:
    - Priority
    - Technique
    - Beginner
    - Intermediate
    - Advanced
    - 3-in-1
    - Total