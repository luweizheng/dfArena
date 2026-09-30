# Hints

- Projects have two types: "capital" and "disaster".
- Projects have four statuses: "design", "construction", "completed", and "not started".
- A project's status is the status category of the report section in which it appears. If the narrative update describes a different stage, use the section's status category.
- The same project may appear under different names, so entity resolution is required.
  - Two names likely refer to the same project if their names or agenda descriptions are semantically similar.
  - Two names listed separately in the same agenda are likely distinct projects, as a project usually appears once per agenda.
- For Annual Street Maintenance, the year in the name identifies an annual cycle of the same ongoing project rather than a separate project. Combine this project's records across years, then apply the time range specified in each question to determine status changes and aggregate funding.
- For Storm Drain Trash Screens, treat "Storm Drain Trash Screens" and "Storm Drain Trash Screens Phase Two" as phases of the same project rather than separate projects. Combine their records, then determine status and aggregate funding using the dates specified in each question.
- Some Funding records have a project_name that is not a real civic project; treat these as noise.
- An agenda's stated meeting date may be wrong, so cross-check it against the dates its own text mentions.
- According to the official complete meeting agenda, the meeting date for report rid_0010 is January 26, 2022; the date in the report header is incorrect.
