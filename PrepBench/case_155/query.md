## Requirements

- Input the data
- Use the single provided pupil travel table.
- Remove any fields you don't need for the challenge
- Change the weekdays from separate columns to one column of weekdays and one of the pupil's travel choice
- Group the travel choices together to remove spelling mistakes
- Create a Sustainable (non-motorised) vs Non-Sustainable (motorised) data field
  - Scooters are the child type rather than the motorised type
- Total up the number of pupil's travelling by each method of travel
- Work out the % of trips taken by each method of travel each day
  - Round to 2 decimal places
- Output the data

## Output

- output_01.csv
  - 6 fields:
    - Sustainable?
    - % of trips per day
    - Trips per day
    - Number of Trips
    - Weekday
    - Method of Travel

- `Sustainable?` uses `Sustainable` or `Non-Sustainable`.
- Weekday labels are `M`, `Tu`, `W`, `Th`, and `F`.
- Standardized travel labels are `Bicycle`, `Car`, `Scooter`, `Walk`, `Van`, `Aeroplane`, `Helicopter`, `Mum's Shoulders`, `Dad's Shoulders`, `Hopped`, `Skipped`, and `Jumped`, where present.
