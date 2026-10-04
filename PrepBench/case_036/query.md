## Context

Prepare reusable transformations that convert imperial measurements to metric measurements for height and weight. The transformations should be reusable across input files.

## Requirements

- Input the data
- Form two reusable steps to automatically convert Height and Weight. Use this file to build the reusable steps.
- Convert the HT (Height) field from Feet and Inches to Meters and Centimeters
  - Conversion rate 1 inch = 2.54 cm
- Convert WT (Weight) from pounds (lbs) to kilograms (kgs)
  - Conversion 1 lb = 0.453592 kg
- Remove the unrequired fields within the Reusable step
- Clean up Name field and create Jersey Number field
- Test your reusable steps on another team's data - use this file
- Create `output_01.csv` from `input_02.csv`, and create `output_02.csv` from `input_01.csv`.
- Output the data

## Output

- output_01.csv
  - 8 fields:
    - Height (m)
    - Weight (KGs)
    - Jersey Number
    - NAME
    - POS
    - AGE
    - COLLEGE
    - SALARY

- output_02.csv
  - 8 fields:
    - Height (m)
    - Weight (KGs)
    - Jersey Number
    - NAME
    - POS
    - AGE
    - COLLEGE
    - SALARY
