## Context
You need to assign each person to either the “Naughty” or “Nice” list based on how often they appear on each list across multiple source files. If a person appears on only one list, they belong to that list. If they appear on both, the list with more occurrences determines the result. If occurrences are tied, the most recent occurrence determines the result.

## Requirements
- Input the data from `input_01.csv`, using the fields `id`, `first_name`, and `File Paths`.
- Treat `first_name` as the person’s name by renaming it to `Name`.
- Split the `File Paths` field into:
  - a list indicator (whether the record comes from the Naughty list or the Nice list), and
  - a file sequence number (`FileNo`) used to determine recency.
- Create an `Index` field that combines the file sequence number and `id` as:
  - `Index = FileNo * 1000 + id`
  - Example rule to preserve: id 7 from Naughty file 1 should create an Index of 1007.
- Create a standardized list label for each record as either `Naughty` or `Nice` based on the list indicator derived from `File Paths`.
- For each `Name`, compute:
  - the count of records labeled `Naughty`, and
  - the count of records labeled `Nice`.
- Determine the final assignment per `Name` as follows:
  - If `naughty_count > nice_count`, assign `Naughty`.
  - If `nice_count > naughty_count`, assign `Nice`.
  - If counts are tied, assign the label from the latest record for that `Name`, where “latest” is defined as the record with the maximum `Index`.
- Remove any unnecessary fields so the final dataset contains exactly one row per person, with only `Name` and the final `Naughty or Nice` assignment.
- Output the data.

## Output

- Output row order is not constrained; sorting by Name is optional.
- Use the categories Naughty and Nice. In the output values of Name and Naughty or Nice, capitalization, surrounding whitespace, and repeated whitespace are presentation differences; they do not change the answer. Preserve spelling and meaningful internal spaces, and do not substitute other category words.
- This output presentation allowance does not change the grouping rule: use each distinct input first_name value as the Name when counting occurrences.

- output_01.csv
  - 2 fields:
    - Naughty or Nice
    - Name