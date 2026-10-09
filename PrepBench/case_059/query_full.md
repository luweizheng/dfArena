## Context
The IT support team at Chin & Beard Suds Co tracks ticket progress via status-change events. Each time a ticket’s status changes, a new record is created with a sequential “Status No.”, allowing reconstruction of each ticket’s history. The goal is to summarize current ticket statuses and evaluate SLA performance for closed tickets, including department-level SLA achievement rankings.

## Requirements
- Input the data.
- Ticket event data is provided across multiple files and must be combined into a single event table before analysis:
  - Load `input_01.csv` as the SLA lookup by Department.
  - Load ticket status-change events from `input_02.csv`, `input_03.csv`, and `input_04.csv`, and append/union them into one dataset with consistent columns.
- Clean Ticket ID/Names:
  - The ticket identifier, department, and requester name are embedded in a single `Ticket` field. Split `Ticket` into exactly three fields using the delimiter ` / `:
    - `Ticket ID` (left part)
    - `Department` (middle part)
    - `Name` (right part)
- Parse `Timestamp` as a datetime for all ticket events.
- Determine the current status per ticket:
  - For each `Ticket ID`, select the record with the maximum `Status No.`; this record defines the ticket’s current status and department attribution used downstream.
- What is the current ticket status?
  - Produce a count of tickets by their current status (based on the current-status record per ticket).
- SLA and business-day logic (used for SLA compliance outputs; closed tickets only):
  - Define each ticket’s start as the earliest (`min`) event `Timestamp` for that `Ticket ID`.
  - Define each ticket’s end for closed tickets as the latest (`max`) `Timestamp` among events where `Status Name` equals `Closed`. Tickets without a closed event have no end date and are excluded from SLA compliance calculations.
  - Business days are Monday–Friday (ignore bank holidays).
  - Weekend timestamp adjustment rules:
    - If a ticket is logged (start) on Saturday or Sunday, roll the start forward to Monday at 00:00:00.
    - If a ticket is closed (end) on Saturday or Sunday, roll the end back to Friday at 23:59:59.
  - Business days are calculated at minute-level precision as a fractional number of days between the adjusted start and end:
    - Use the count of weekdays between the start date and end date, and add fractional contributions for the partial start day and partial end day.
    - If the start and end occur on the same date, compute the duration as the exact elapsed time in days between the two timestamps.
- Answer the following questions:
  - How many cases are in each status? (use current status per ticket)
  - How many closed tickets have missed their SLA? How many are on track to meet their SLA?
    - Join closed-ticket durations to the SLA agreement by matching on `Department`.
    - A closed ticket “meets SLA” if `Business Days Open` is less than or equal to `SLA Agreement`; otherwise it “missed SLA”.
    - “On Track to Meet SLA” is the count of closed tickets that meet SLA. These two counts include all departments with a matching SLA agreement; they are not restricted to SLA Agreement = 18.
  - What departments have the best SLA achieved %?
    - Closed cases only.
    - Restrict this department ranking to departments whose `SLA Agreement` equals 18.
    - For each included department, compute:
      - `Achieved %` = (number of closed tickets that meet SLA / total closed tickets) × 100.
    - Exclude departments with `Achieved %` equal to 0.
    - Rank from highest unrounded % to lowest %; break ties by sorting department name ascending. Output the department table in rank order.
    - Round `Achieved %` to 2 decimal places and assign sequential ranks starting at 1 after sorting.
- Output the data.

## Output

Use the exact column names below. `output_01.csv` counts tickets per current status; `output_02.csv` contains the metrics `Missed SLA` and `On Track to Meet SLA`; `output_03.csv` gives one row per included department with its SLA achievement percentage and rank.

- output_01.csv
  - 2 fields:
    - Current Status
    - Ticket Count

- output_02.csv
  - 2 fields:
    - Metric
    - Total

- output_03.csv
  - 3 fields:
    - Department Rank
    - Department
    - Achieved %
