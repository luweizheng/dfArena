import json
import re
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


def minutes(value, fallback=None):
    match = re.fullmatch(r'(\d{1,2})(?::(\d{2}))?(AM|PM)?', value.strip())
    if not match:
        raise ValueError(f'Unrecognized time: {value}')
    hour, minute, period = match.groups()
    period = period or fallback
    if period is None:
        raise ValueError(f'Missing AM/PM: {value}')
    return (int(hour) % 12 + (12 if period == 'PM' else 0)) * 60 + int(minute or 0)


def after_six(hours):
    if hours.lower() == 'closed':
        return False
    if hours.lower() == 'open 24 hours':
        return True
    for interval in hours.split(','):
        start, end = re.split('[–—-]', interval.strip())
        period = re.search('(AM|PM)$', end).group(1)
        opening = minutes(start, period)
        closing = minutes(end)
        if closing <= opening:
            closing += 24 * 60
        if closing > 18 * 60:
            return True
    return False


def format_hours(schedule):
    groups = {}
    for day in DAYS:
        if day in schedule:
            groups.setdefault(schedule[day], []).append(day[:3])
    return '; '.join(f'{", ".join(days)}: {hours}' for hours, days in groups.items())


def main():
    businesses = pd.read_parquet(DATA / 'business/business_description.parquet')
    reviews = pd.read_parquet(DATA / 'review/review.parquet', columns=['gmap_id', 'rating'])
    businesses['schedule'] = businesses.hours.map(lambda h: dict(json.loads(h)) if pd.notna(h) else {})
    closed = businesses.state.fillna('').str.contains(r'permanently\s+closed|temporarily\s+closed', case=False, regex=True)
    eligible = businesses.schedule.map(lambda s: any(after_six(s[d]) for d in DAYS[:5] if d in s))
    averages = reviews.groupby('gmap_id', as_index=False).agg(average_rating=('rating', 'mean'), review_count=('rating', 'count'))
    ranked = businesses.loc[~closed & eligible].merge(averages, on='gmap_id', validate='one_to_one').dropna(subset=['average_rating']).sort_values(['average_rating', 'name', 'gmap_id'], ascending=[False, True, True])
    top = ranked.head(5)
    assert len(top) == 5
    ranked.drop(columns='schedule').to_csv(OUT / 'ranked_businesses.csv', index=False)
    lines = ['Top 5 (average review rating out of 5; ties listed alphabetically):']
    for i, row in enumerate(top.itertuples(), 1):
        lines.append(f'{i}. {row.name} — {row.average_rating:.2f}/5. Hours: {format_hours(row.schedule)}.')
    answer = '\n'.join(lines)
    (OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False, indent=2) + '\n')
    print(answer)


if __name__ == '__main__':
    main()
