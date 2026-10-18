## Context
If you've spent as long as I have in the data world, you will inevitably have had moments when your sophisticated tools are actually a lot harder to solve a challenge with than Excel. The people you work with are likely to describe challenges to you in Excel terms and expect your solutions to be able to follow the same process as their logic. It's not always that easy though.
Last week when working with some client data (I've converted this to an Allchains example), my team was challenged to look at Orders captured in a weekly snapshot that was then exported into Excel.
Each week the file would show any order that was still opened that hadn't been fulfilled (ie delivered to the customer). The challenge is to classify when an order is new (the first report it has appeared in), unfulfilled (when it appears in any subsequent reports) or completed (the week after the order last appears in a report). But what if we needed to know whether the order was fulfilled and when?
Combine the weekly snapshots and generate the additional fulfilled-order records required by the rules below.

## Requirements

- Input the data
- Create one complete data set
- Use the source file to create the Reporting Date: input_01.csv = 1 January 2021, input_02.csv = 8 January 2021, input_03.csv = 15 January 2021, input_04.csv = 22 January 2021, and input_05.csv = 29 January 2021.
- Find the Minimum and Maximum date where an order appeared in the reports
- Add one week on to the maximum date to show when an order was fulfilled by
- Apply this logic:
  - The first time an order appears it should be classified as a 'New Order'
  - The week after the last time an order appears in a report (the maximum date) is when the order is classed as 'Fulfilled'
  - Any week between 'New Order' and 'Fulfilled' status is classed as an 'Unfulfilled Order'
- Pull of the data sets together
- Remove any unnecessary fields
- Output the data

## Output

- output_01.csv
  - 4 fields:
    - Order Status
    - Orders
    - Sale Date
    - Reporting Date
