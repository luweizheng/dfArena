## Context
We've got sales data from a company selling Halloween costumes around the world, but it certainly needs a little tidying up. With their fiscal year coming to an end on Halloween itself, they want to see how their sales are comparing to last year's. Let's hope the results aren't too scary!

## Requirements

- Input the data
- Each costume is in the language of the country the sales occur in. Group these costumes together by their English translation.
  - You should have 9 costumes once you've finished grouping
- There have been some errors when inputting country names. Identify and correct these country-name errors.
- The fiscal year for this company begins in November each year. We want to compare sales from 2019 fiscal year (01/11/18 - 31/10/19) to sales so far in this fiscal year (01/11/19 - 27/10/20)
- We would like all the sales to be in one column, regardless of their discount.
- The sales should be split into currency and value, removing the fractional part of each individual sales value before aggregating to fiscal-year totals.
  - Careful, some currencies are described by 2 words.
- The column detailing the price discount should only contain the words "Full", "Half" or "Quarter"
- Finally, we would like 2019 FY Sales and 2020 FY Sales to appear in 2 separate columns, for ease of comparing sales by reading across rows.
- Output the data

## Output

Costume uses the English categories Cat, Ghost, Vampire, Pirate, Zombie, Clown, Dinosaur, Devil and Werewolf.

- output_01.csv
  - 6 fields:
    - Costume
    - Country
    - Currency
    - Price
    - 2019 FY Sales
    - 2020 FY Sales
