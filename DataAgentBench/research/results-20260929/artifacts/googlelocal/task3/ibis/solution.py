import json
from pathlib import Path
import ibis

OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
b = con.read_parquet('/workspace/data/business/business_description.parquet')
r = con.read_parquet('/workspace/data/review/review.parquet')
# Keep recorded review rows, including duplicates, in the arithmetic mean.
avg = r.group_by('gmap_id').aggregate(average_rating=r.rating.mean())
active = b.filter(~b.state.fill_null('').lower().re_search(r'(permanently|temporarily)\s+closed'))
slots = active.mutate(slot=active.hours.cast('json').cast('array<array<string>>').unnest())
slots = slots.mutate(day=slots.slot[0], span=slots.slot[1])
slots = slots.filter(slots.day.isin(['Monday','Tuesday','Wednesday','Thursday','Friday']))
slots = slots.mutate(start_text=slots.span.split('–')[0], end_text=slots.span.split('–')[1])

def minutes(expr, fallback):
    hour = expr.re_extract(r'^(\d{1,2})', 1).nullif('').try_cast('int64')
    minute = expr.re_extract(r':(\d{2})', 1).nullif('').try_cast('int64').fill_null(0)
    meridiem = expr.re_extract(r'(AM|PM)$', 1).nullif('').fill_null(fallback)
    return (hour % 12) * 60 + minute + (meridiem == 'PM').ifelse(720, 0)

end_meridiem = slots.end_text.re_extract(r'(AM|PM)$', 1)
slots = slots.mutate(start_min=minutes(slots.start_text, end_meridiem), end_min=minutes(slots.end_text, end_meridiem))
# A closing time at/before opening denotes an overnight interval.
eligible = slots.filter((slots.span == 'Open 24 hours') | (slots.end_min > 1080) | (slots.end_min <= slots.start_min)).select('gmap_id').distinct()
ranked = active.semi_join(eligible, 'gmap_id').inner_join(avg, 'gmap_id').select('gmap_id','name','hours','average_rating')
ranked = ranked.order_by(ibis.desc('average_rating'), 'name', 'gmap_id')
rows = ranked.limit(5).to_pyarrow().to_pylist()
(OUT / 'top5.json').write_text(json.dumps(rows, indent=2, ensure_ascii=False))
# Format hours only after the final relational materialization.
days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
def format_hours(raw):
    schedule = dict(json.loads(raw))
    groups = []
    for day in days:
        hours = schedule.get(day, 'Unspecified')
        if groups and groups[-1][1] == hours:
            groups[-1][0].append(day)
        else:
            groups.append(([day], hours))
    return '; '.join((ds[0] if len(ds)==1 else ds[0]+'–'+ds[-1])+': '+h for ds,h in groups)
answer = '\n'.join(f"{i}. {row['name']} — average rating {row['average_rating']:.4f}/5; {format_hours(row['hours'])}." for i,row in enumerate(rows,1))
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False, indent=2))
print(answer)
