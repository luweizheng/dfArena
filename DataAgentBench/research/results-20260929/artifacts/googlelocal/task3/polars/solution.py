import json
import re
from pathlib import Path
import polars as pl

OUT = Path('/workspace/work')
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

def minutes(value, fallback=None):
    m = re.fullmatch(r'(\d{1,2})(?::(\d{2}))?(AM|PM)?', value.strip())
    if not m:
        raise ValueError(value)
    hour, minute, suffix = m.groups()
    suffix = suffix or fallback
    if suffix is None:
        raise ValueError(value)
    return (int(hour) % 12 + (12 if suffix == 'PM' else 0)) * 60 + int(minute or 0)

def late_weekday(raw):
    if not raw:
        return False
    for day, hours in json.loads(raw):
        if day not in DAYS[:5] or hours == 'Closed':
            continue
        if hours == 'Open 24 hours':
            return True
        for interval in hours.split(','):
            start, end = re.split('[–—-]', interval.strip())
            end_minutes = minutes(end)
            start_minutes = minutes(start, re.search('(AM|PM)$', end).group(1))
            if end_minutes <= start_minutes:
                end_minutes += 24 * 60
            if end_minutes > 18 * 60:
                return True
    return False

def format_hours(raw):
    schedule = dict(json.loads(raw))
    groups = []
    for day in DAYS:
        hours = schedule.get(day, 'Not listed')
        if groups and groups[-1][1] == hours:
            groups[-1][0].append(day[:3])
        else:
            groups.append(([day[:3]], hours))
    return '; '.join((days[0] if len(days) == 1 else days[0] + '–' + days[-1]) + ': ' + hours for days, hours in groups)

businesses = pl.scan_parquet('/workspace/data/business/business_description.parquet')
ratings = (pl.scan_parquet('/workspace/data/review/review.parquet')
           .group_by('gmap_id').agg(pl.col('rating').mean().alias('average_rating'), pl.col('rating').count().alias('rating_count')))
eligible = businesses.filter(
    ~pl.col('state').fill_null('').str.to_lowercase().str.contains(r'permanently closed|temporarily closed'),
    pl.col('hours').map_elements(late_weekday, return_dtype=pl.Boolean).fill_null(False)
)
ranked = (eligible.join(ratings, on='gmap_id', how='inner')
          .filter(pl.col('average_rating').is_not_null())
          .sort(['average_rating', 'name', 'gmap_id'], descending=[True, False, False]).collect())
ranked.write_json(OUT / 'eligible_ranked.json')
top = ranked.head(5)
lines = [f"{i}. {row['name']} — {row['average_rating']:.2f}/5; {format_hours(row['hours'])}." for i, row in enumerate(top.to_dicts(), 1)]
answer = 'Top 5 by mean review rating (weekdays = Monday–Friday; permanently or temporarily closed businesses excluded):\n' + '\n'.join(lines)
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False, indent=2) + '\n')
print(answer)
print('\nRanking audit:')
print(ranked.select('name', 'average_rating', 'rating_count').head(10))
