## Context
The dataset contains clients attending training sessions and historical account ownership. Prepare a deduplicated attendance dataset in which every attendee retains the client's latest account ownership details.

## Requirements

- Input the data
- For each Client, work out who the most recent Account Manager is
- Filter the data so that only the most recent Account Manager remains
  - Be careful not to lose any attendees from the training sessions!
- In some instances, the Client ID has changed along with the Account Manager. Ensure only the most recent Client ID remains
- Output the data

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
  - From Date must be output as exact text.
  - From Date must use DD/MM/YYYY format (preserve day/month/year with leading zeros).
