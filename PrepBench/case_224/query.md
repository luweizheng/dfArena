## Context
You have been hired to create a dataset for the Prep School that will allow them to analyse the correlation between attendance and test scores.

## Requirements

- Input the data
- First we must join the test score data set and the additional class attendance data set
- Clean Data: there’s a few spelling mistakes in the data set, use the data tool of your choice to correct these mistakes before we proceed. These mistakes are in the “Subject” Column
- Use a calculated field to clean up the test score column, so each number is a rounded to the nearest whole number
- Split the student name column so we can see the first name and surname in two separate columns, named appropriately
- Create `Attendance Flag` from the attendance percentage: use `High Attendance` for 90% or above, `Medium Attendance` for 70% or above but below 90%, and `Low Attendance` for below 70%.
- Output the data

## Output

- output_01.csv
  - 8 fields:
    - Attendance Flag
    - First Name
    - Surname
    - Attendance_Percentage
    - Student_ID
    - Subject
    - Test_score
    - TestScoreInteger
