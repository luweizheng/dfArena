## Context

Last night one of our order takers at C&B Suds Co decided to scribble down the last orders of the day rather than actually input them on the system before they left for the night. They wrote down a series of notes to help them remember the order details but unfortunately they've been quarantined with the coorslightavirus and now we have to figure out who ordered what and what their order priority was. We have all the titles, last names, products, and order priorities but not how these match up. Using the clues below help us figure this out! 1. Only the customer with the highest priority has a title and last name that begin with the same letter. 2. Bevens' priority is directly after Dimmadome. Neither of these people ordered the Chamomile Bar or the Hibiscus Soap-on-a-Rope. 3. The Sergeant and the person who ordered Lemon Gel are either 1st priority or 3rd priority. 4. The Reverend didn't order the Rose Bar and isn't 2nd priority. 5. The Sergeant either ordered Hibiscus Soap-on-a-Rope or is 4th priority. 6. The priority of the person who ordered the Rose Bar is directly after the person who ordered the Lemon Gel. 7. Dimmadome is not a Doctor and the Baroness didn't order the Hibiscus Soap-on-a-Rope.

## Requirements

- Input the data. Two alternative starting points are supplied:
  - `input_01.csv`: all possible combinations of Title, LastName, Product, and Priority.
  - `input_02.csv`: the four raw attribute lists. Values on the same input row are not known matches.
  Use either starting point; do not append the two inputs as orders.
- If the data hasn't been prepared then prepare it so there is a row for every [Title], [Last Name], [Product], and [Priority] combination.
- Filter the candidate combinations using the clues above.
- You do not need to make any guesses - the final outcome can be arrived at using logical deduction and the clues above!
- Output the data

## Output

Each output row is one customer order. Use the exact column names below.

- output_01.csv
  - 4 fields:
    - Title
    - LastName
    - Product
    - Priority
