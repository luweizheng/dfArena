## Context
The dataset contains clients attending training sessions and historical account ownership. Prepare a deduplicated attendance dataset in which every attendee retains the client's latest account ownership details.

## Requirements
- Input the data from `input_01.csv`.
- Treat each row as a training-attendance record identified by the combination of the output fields (Training, contact details, client details, and From Date).
- Determine the "most recent" account ownership per Client:
  - Parse `From Date` as a date using the day/month/year format (`%d/%m/%Y`) for comparison.
  - For each `Client`, identify the record with the maximum parsed `From Date`.
  - If multiple records for the same `Client` share the same maximum date, use the first such record encountered **in the input file order** (i.e., the record that appears earliest in `input_01.csv`) as the most recent.
- Update all records to retain attendees while standardizing client ownership:
  - For every record belonging to a given `Client`, overwrite `Client ID`, `Account Manager`, and `From Date` with the values from that Client's most recent record.
  - Do not filter out attendance records; the result must preserve all training attendees, with ownership fields updated to the latest values for their Client.
- Remove exact duplicate rows after updating ownership; retain every distinct training attendance record.
- Ensure that when a Client's ID has changed along with account ownership, only the most recent `Client ID` remains by applying the same "most recent per Client" rule above.
- Output `Client ID` as exact text (preserve digits and leading zeros if any).
- Output the data exactly as specified below.

### Ambiguity Resolution
- Client name matching:
  - Client names are matched exactly as they appear in the `Client` field, case-sensitive and including any surrounding quotes or special characters.
  - No normalization is applied to Client names for matching purposes (e.g., `"Braun Inc"` and `Braun Inc` are treated as different Clients if they appear differently in the data).
- Training and Contact Email formatting:
  - Output `Training` and `Contact Email` exactly as they appear in the input (case, spacing, and punctuation preserved).

## Output

- output_01.csv — distinct training attendances with the latest client ownership details
  - 7 fields:
    - Training
    - Contact Email
    - Contact Name
    - Client
    - Client ID
    - Account Manager
    - From Date
  - Training and Contact Email must be output exactly as in the input (case, spacing, and punctuation preserved).
  - Client ID and From Date must be output as exact text.
  - From Date must use DD/MM/YYYY format (preserve day/month/year with leading zeros).
