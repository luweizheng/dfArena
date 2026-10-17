## Context

You are preparing a guest-by-guest list of selected dishes from an orders layout where each guest’s choices appear in paired columns (a dish/course text column plus an adjacent selection indicator column). You must reshape this structure into a normalized table, infer each dish’s course from course header rows, and then attach the corresponding Recipe ID from a separate lookup table.

## Requirements

- Input the data.
- Read `input_01.csv` (Orders) as a headerless table where:
  - Row 0 contains guest names in the “dish text” columns.
  - The layout consists of guest blocks. For each guest, there is a column for the dish/course text and an immediately following column for the selection marker.
  - **Note**: There may be empty columns between these guest blocks (e.g., Guest 1 at col 0, Selection at col 1, Empty at col 2, Guest 2 at col 3...). You must dynamically identify the guest columns.
  - Data rows begin on row 1.
- Reshape the Orders table into a long format at the grain of one row per *(Guest, original row item)*, producing the equivalent of:
  - Guest name
  - Dish/value text (the original cell content from the guest’s dish text column)
  - Selections (the original cell content from the adjacent selection column; expected to contain `🗸` when selected, otherwise blank/null)
- Extract the course name from the Dish/value text:
  - Treat “Starter” and “Starters” as the same course, and similarly for “Main(s)” and “Dessert(s)”.
  - Determine the course marker by checking whether the trimmed dish/value text starts with the course word (case-insensitive): starter → `Starters`, main → `Mains`, dessert → `Dessert`. If it does not start with one of these, the course marker is null.
- Fill down the course name for each Guest:
  - Within each Guest’s reshaped rows, forward-fill the most recent non-null course marker into a `Course` field so that every dish row inherits the course that precedes it for that guest.
- Filter out where the Dish/value text is itself a course header row:
  - Keep only rows where the course marker is null (i.e., the row is not a course label).
- Filter out dishes which have not been selected:
  - Keep only rows where `Selections` equals `🗸`.
  - Also exclude rows where the dish/value text is null.
- Bring in Recipe ID from the Lookup Table:
  - Read `input_02.csv` (Lookup) containing at least `Dish` and `Recipe ID`.
  - Left-join the selected dish rows to the lookup on exact `Dish` text to add `Recipe ID`.
  - Ensure `Recipe ID` is an integer in the final output.
- **Output Formatting**:
  - Preserve the dish name. For `Duck a l'orange` / `Duck a l’orange`, either straight or smart apostrophe is acceptable.
- Output the data.

Final output row order is unrestricted.

## Output

- output_01.csv
  - 4 fields:
    - Guest
    - Course
    - Recipe ID
    - Dish