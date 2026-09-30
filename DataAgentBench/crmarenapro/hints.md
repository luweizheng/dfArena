# Hints
 
- ~25% of ID-like fields may include a leading # (e.g., #001Wt00000PFj4zIAD).
- ~20% of text fields may contain trailing whitespace (e.g., "Company Name ").
- Corruption may appear in: Id, AccountId, ContactId, Name, FirstName, LastName, Email, Subject, Status.
- Corruption handling is needed for reliable joins
- Domain-specific CRM knowledge is required
- When comparing case closure speed across states, use the arithmetic mean closure time of each state's closed cases, weighting each case equally. A case's closure time is its closed date/time minus its created date/time.
- When determining eligibility for having handled more than one case, include cases that have not yet been closed.
- When comparing agents' average sales cycles in April 2023, include opportunities whose corresponding contracts have a company signed date in that month, rather than filtering by the opportunity creation date or the opportunity's own close date.
- When comparing agents' order sales amounts, attribute each order's sales amount to that order's owner.
