## Requirements

You aim is to build a data set that is one row per item sold for each order made at the Book Shop.

- Input the 13 provided CSV files. `input_09.csv` through `input_12.csv` are the sales extracts; the other CSV files contain the related tables.
- Union all the Sales data together to form one row per item in a sale
  - This is the granularity of the data set throughout the whole challenge (56,350 rows)
- Join the other provided CSV datasets onto this data
  - Never let the number of rows change
    - You may need to disregard incomplete records or summarise useful data into a metric instead of including all the detail
- Remove any duplicate fields
- Exclude any temporary source-file metadata from the final output.
- Output the data

## Output

- output_01.csv
  - 38 fields:
    - Book ID
    - Sale Date
    - ISBN
    - Discount
    - ItemID
    - OrderID
    - First Name
    - Last Name
    - Birthday
    - Country of Residence
    - Hrs Writing per Day
    - Title
    - AuthID
    - Format
    - PubID
    - Publication Date
    - Pages
    - Print Run Size (k)
    - Price
    - Publishing House
    - City
    - State
    - Country
    - Year Established
    - Marketing Spend
    - Number of Awards Won (avg only)
    - Number of Months Checked Out
    - Total Checkouts
    - Genre
    - SeriesID
    - Volume Number
    - Staff Comment
    - Series Name
    - Planned Volumes
    - Book Tour Events
    - Average Rating
    - Number of Reviewers
    - Number of Reviews
  - Sale Date, Birthday, and Publication Date must be formatted exactly as `DD/MM/YYYY` (zero-padded); blank if missing.
  - The following fields must be integer strings with no decimals; blank if missing: Pages, Print Run Size (k), Year Established, Marketing Spend, Number of Awards Won (avg only), Number of Months Checked Out, Total Checkouts, Volume Number, Planned Volumes, Book Tour Events, Number of Reviewers, Number of Reviews.
  - Average Rating must be output with 9 decimal places (zero-padded); blank if missing.
