## Context

Assemble the supplied fixed soap sales figures into a long-format DataFrame. The original random-generation exercise is out of scope; do not generate new random sales or derive replacements from aggregate inputs.

## Requirements

- Use the companies in `input_02.csv` and scents in `input_03.csv`.
- Produce one row for every Company × Soap Scent × Month combination, for March and April only.
- Each row's Sales comes from the matching March Sales or April Sales cell in the supplied table, preserving the supplied numeric precision.
- Keep Company and Soap Scent labels as supplied, and use literal month names March and April.
- The aggregate and random-value files `input_01.csv` and `input_04.csv` are context from the original exercise; they do not override the fixed figures.
- No output row order is required.
- Output exactly the fields listed below.

**Pre-computed Sales Values (use these exact values):**

| Company | Soap Scent | March Sales | April Sales |
|---------|------------|-------------|-------------|
| Sudsie Malone | Watermelon | 16111810.1905113 | 43324732.2378659 |
| Sudsie Malone | Rose | 436189982.659625 | 474305911.129159 |
| Sudsie Malone | Pineapple | 195777011.452937 | 156272517.916588 |
| Sudsie Malone | Orange | 412134370.941974 | 353270582.65706 |
| Sudsie Malone | Lime | 484758850.134914 | 498602247.12946 |
| Sudsie Malone | Jasmine | 137170566.982806 | 205579440.043756 |
| Sudsie Malone | Coconut | 65391004.6495168 | 63112499.5439582 |
| Squeaky Cleanies | Watermelon | 376808030.777165 | 359575271.257045 |
| Squeaky Cleanies | Rose | 129787658.246884 | 128785250.425908 |
| Squeaky Cleanies | Pineapple | 238007425.850963 | 256806998.355096 |
| Squeaky Cleanies | Orange | 139286665.948943 | 151780261.822217 |
| Squeaky Cleanies | Lime | 345003632.458146 | 338907634.437198 |
| Squeaky Cleanies | Jasmine | 206828164.281029 | 224290584.599189 |
| Squeaky Cleanies | Coconut | 354586986.076179 | 357857537.8778 |
| Soap and Splendour | Watermelon | 492435899.503911 | 485419986.399615 |
| Soap and Splendour | Rose | 131704995.121507 | 141954141.481657 |
| Soap and Splendour | Pineapple | 64342384.7679437 | 77305548.196635 |
| Soap and Splendour | Orange | 33058612.1516716 | 35094874.3014569 |
| Soap and Splendour | Lime | 494326797.516198 | 504535845.949119 |
| Soap and Splendour | Jasmine | 433598049.009094 | 433397893.588997 |
| Soap and Splendour | Coconut | 246916246.91089 | 255550442.804023 |
| Chin & Beard Suds Co | Watermelon | 106952309.209599 | 102534810.120234 |
| Chin & Beard Suds Co | Rose | 118151757.969388 | 118050971.181238 |
| Chin & Beard Suds Co | Pineapple | 28306848.2002096 | 29633832.2424581 |
| Chin & Beard Suds Co | Orange | 54309340.7920479 | 67242836.7326192 |
| Chin & Beard Suds Co | Lime | 80521503.2185151 | 77961503.2398676 |
| Chin & Beard Suds Co | Jasmine | 7911885.00493674 | 22508233.9117437 |
| Chin & Beard Suds Co | Coconut | 87351394.1729071 | 90175588.8550569 |
| British Soaps | Watermelon | 115248724.394306 | 127555384.328319 |
| British Soaps | Rose | 31665157.81196 | 57405492.4024066 |
| British Soaps | Pineapple | 5183387.89368681 | 25653263.5002902 |
| British Soaps | Orange | 145897557.064093 | 130879305.934362 |
| British Soaps | Lime | 141726823.817304 | 138643749.678239 |
| British Soaps | Jasmine | 86399975.4890454 | 81225711.2659018 |
| British Soaps | Coconut | 145650549.329192 | 125860028.73346 |

## Output

- output_01.csv
  - 4 fields:
    - Company
    - Soap Scent
    - Month
    - Sales
