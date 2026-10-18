## Context

Produce Excel-style conditional sums and averages of flight ticket sales, grouped by flight and class and split by the time remaining before departure.

## Requirements

- Input the data
- Form Flight name
- Workout how many days between the sale and the flight departing
- Classify daily sales of a flight as:
  - Less than7 days before departure
  - 7 or more days before departure
- Mimic the SUMIFS and AverageIFS functions by aggregating the previous requirements fields by each Flight and Class
- Round all data to zero decimal places
- Output the data

## Output

- output_01.csv
  - 6 fields:
    - Flight
    - Class
    - Avg. daily sales 7 days or more until the flight
    - Avg. daily sales less than 7 days until the flight
    - Sales less than 7 days until the flight
    - Sales 7 days or more until the flight
