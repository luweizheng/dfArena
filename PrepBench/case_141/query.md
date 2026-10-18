## Context
Allchains Bike Stores have been fund raising in one of their stores. Customers are given the option of donating to charity when they buy a new bike. Sadly, the team haven't been recording the data accurately and the donations only get totalled up at sporadic points throughout the month. We need to understand roughly how much is being raised each day. Also, are our customers more generous on a certain day of the week?

## Requirements

- Input the data
- Create new rows for any date missing between the first and last date in the data set provided
- Calculate how many days of fundraising there has been by the date in each row (1st Jan would be 0)
- Calculate the amount raised per day of fundraising for each row
- Workout the weekday for each date
- Average the amount raised per day of fundraising for each weekday
- Output the data

## Output

- output_01.csv
  - 5 fields:
    - Avg raised per weekday
    - Value raised per day
    - Days into fund raising
    - Date (the weekday name, e.g. Friday, rather than the calendar date)
    - Total Raised to date
