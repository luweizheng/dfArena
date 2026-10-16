## Context
You have three input datasets related to the Olympic Games: (1) a host cities/countries table, (2) a historical medallists table, and (3) a country-to-code lookup. The goal is to produce three standardized outputs: a cleaned medallists extract, a host cities extract with a derived host-country field, and a country-by-year medal summary.

## Requirements
- Input the data.
  - Parse slash-separated host dates as `MM/DD/YYYY` and year-first host dates as `YYYY-DD-MM`, ignoring any time component. Output dates as `DD/MM/YYYY` and derive Year from Start Date.
  - Use the country-code lookup as the authoritative mapping between country names and 3-letter country codes.
  - Use the hosts table as the authoritative source for host metadata (including the combined host string and the start/end dates).
  - Use the medallists table as the authoritative source for individual medal records.

- Make sure every medal has both a Country and Country Code associated with it.
  - If a medal record is missing `Country`, fill it using the lookup via the record’s country code.
  - If a medal record is missing the country code, fill it using the lookup via the record’s country name.
  - After attempting to fill, remove any medal records that still do not have both fields populated (since they cannot be reliably attributed to a country).

- Group together Canoe/Kayak and Canoeing Sports.
  - Standardize `Sport` so that any value representing Canoeing is labeled exactly as `Canoe / Kayak`.
  - Specifically, replace `Canoeing` with `Canoe / Kayak` in the `Sport` field.

- Change Sport from Swimming to Aquatics.
  - Standardize `Sport` so that Swimming is labeled exactly as `Aquatics`.

- Replace the word "metres"/"metre" in Events with an "m" abbreviation.
  - In the `Event` field, replace whole-word occurrences of “metres” and “metre” with `m`.
  - For Athletics events, use exactly one space between a numeric distance and the metre unit m in every year, including already abbreviated values and relay distances: 100 metres → 100 m, 100m → 100 m, and 4×100m relay → 4×100 m relay. This rule concerns the metre unit only; existing kilometre rules and relay x/× conventions remain separate.

- Use ` x ` between swimming relay distances, e.g. `4×100m` → `4 x 100m`.
- Standardize metre spacing in Shooting events, e.g. `50m pistol` → `50 m pistol`.

- Replace the word "kilometres" in Events with an "km" abbreviation.
  - In the `Event` field, replace whole-word occurrences of “kilometres” with `km`.
  - Also handle cases where a distance number is directly followed by “kilometres” so that it becomes `<number>km`.

- Standardize km-walk Event formatting in Athletics:
  - For **Athletics events in Year 2016 only**: Format walking events with a space: `20 km walk`, `50 km walk`.
  - For **Athletics events in all other years**: Format walking events without a space: `20km walk`, `50km walk`.
  - Apply similar normalization for related distance events (e.g., `marathon 10 km` → `marathon 10km`, `20 km race walk` → `20km race walk`).

- Group together sensible Disciplines.
  - Standardize `Discipline` using consistent labels. Apply the following deterministic renames (only these listed mappings should be applied):
    - Normalize Greco-Roman wrestling variants to `Greco-Roman`.
    - Normalize modern pentathlon variants to `Modern Pentathalon`.
    - Normalize synchronized swimming variants to `Synchronized Swimming`.
    - Normalize beach volleyball, mountain bike, and gymnastics discipline labels to their standardized forms (`Beach volleyball`, `Mountain Bike`, `Artistic G.`, `Rhythmic G.`).
  - For rows where Sport is `Cycling`, set Discipline to `Cycling Track` if any of these conditions holds:
    - Discipline contains `Track cycling`, `Cycling Track`, `Road cycling`, or `Cycling Road`.
    - Year ≤ 1992.
    - Event contains `road race` or `time trial`.
  - Match these text patterns case-insensitively. Otherwise, retain Discipline after applying the other specified renames.

- Output cleaned Medallists Dataset.
  - Produce `output_03.csv` at the medal-record level (one row per medal record retained after validation), containing the required fields only.
  - Remove fully duplicate rows so that exact duplicate records are not repeated in the output.

- Aggregate to a row for each Event medal (i.e. we know longer need the Athlete names Level of Detail).
  - When preparing country medal counts, de-duplicate medal records down to a unique "event medal" grain before counting.
  - Use the following event-medal uniqueness rules:
    - For `Canoe / Kayak`, treat medals as unique by (`Country`, `Year`, `Medal`, `Event`, `Sport`, `Event_Gender`) excluding `Discipline` from the uniqueness key. This is because Canoe/Kayak discipline variants (such as `Canoe / Kayak F`, `Flatwater`, `Slalom`, `Sprint`) represent different ways of categorizing the same competitive events, and the same event medal should not be double-counted across these discipline variants.
    - For all other sports, treat medals as unique by (`Country`, `Year`, `Medal`, `Event`, `Sport`, `Event_Gender`, `Discipline`) so distinct disciplines remain distinct when relevant.

- Create a table showing total Gold, Silver and Bronze medals from each country for each year.
  - Starting from the de-duplicated event-medal grain above, count medals by `Country` and `Year`, separately for `Gold`, `Silver`, and `Bronze`.
  - The output grain for `output_01.csv` must be one row per (`Country`, `Year`).
  - If a country-year has no medals of a given type, output an empty value (blank) for that medal-type column rather than `0`.

- Output Country Medals Dataset.
  - Write the aggregated country-by-year medal summary to `output_01.csv` with exactly the specified fields.

- Using the Hosts dataset, create a field for the Host Country.
  - Derive `Host City` and `Host Country` by splitting the host descriptor into city and country components (city first, country second).
  - Standardize host dates so `Start Date` and `End Date` are formatted as `DD/MM/YYYY`.
  - Derive `Year` from the (standardized) `Start Date`.

- Change the United Kingdom to Great Britain.
  - In the derived `Host Country` field, replace `United Kingdom` with `Great Britain`.

- Output Host Cities Dataset.
  - Write the cleaned/derived hosts table to `output_02.csv` with exactly the specified fields.

- Output the data.
  - Remove exact duplicate records from the cleaned Medallists Dataset before writing `output_03.csv`.

## Output

- output_01.csv
  - 5 fields:
    - Country
    - Gold
    - Silver
    - Bronze
    - Year

- output_02.csv
  - 9 fields:
    - Year
    - Host City
    - Host Country
    - Start Date
    - End Date
    - Games
    - Nations
    - Sports
    - Events

- output_03.csv
  - 9 fields:
    - Country
    - Code
    - Sport
    - Medal
    - Event
    - Athlete
    - Year
    - Event_Gender
    - Discipline
