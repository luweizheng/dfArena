import polars as pl
import csv, io, re, json
from datetime import datetime
from pathlib import Path

base=Path('/workspace/data')
docs=pl.read_parquet(base/'domain_docs/files.parquet')
rows=[]
formats=['%y-%m%d','%y/%m%d','%Y%m%d','%Y/%m%d','%Y-%m%d','%m%d/%Y','%d%m/%Y','%d%b-%Y','%B%d,%Y','%b%d,%Y','%m%d/%y','%d%m/%y','%d%b-%y','%B%d,%y','%b%d,%y','%y%m%d']
def get_date(line):
    if '(reported ' in line: s=line.rsplit('(reported ',1)[1].rstrip(') .')
    elif line.startswith('As of '): s=line[6:].split(':',1)[0]
    elif line.startswith('Date: '): s=line[6:].split('.',1)[0]
    elif line.startswith('['): s=line[1:].split(']',1)[0]
    elif line.startswith('('): s=line[1:].split(')',1)[0]
    elif ' — ' in line: s=line.split(' — ',1)[0]
    else: return None
    for fmt in formats:
        try: return datetime.strptime(s.strip(),fmt).date()
        except ValueError: pass
    return None
bad=[]
for content in docs['content']:
    if 'Area\tReport' not in content: continue
    for row in csv.DictReader(io.StringIO(content[content.index('Area\tReport'):]),delimiter='\t'):
        for line in (row.get('Report') or '').splitlines():
            d=get_date(line)
            if d is None: bad.append(line)
            elif 2020<=d.year<=2023: rows.append((row['Area'],d,d.year,line))
df=pl.DataFrame(rows,schema=['area','date','year','line'],orient='row')
latest=df.filter(pl.col('date')==pl.col('date').max().over(['area','year']))
latest.write_csv('/workspace/work/latest_reports.csv')
print('Unparsed dated report lines:',len(bad)); assert not bad, bad[:5]
Path('/workspace/work/latest_lines.txt').write_text('\n'.join(f'{a} | {d} | {l}' for a,d,y,l in latest.iter_rows()))
# Extract each human-acre observation, including paired 'respectively' prose.
metric=r'(?:human-caused acres burned|human-source acres consumed|human-ignited burn acreage|acreage from human-caused fires|acres burned by human-caused wildfires)'
number=r'(?:N/A|\d+(?:[, ]\d{3})*)'
observations=[]
for area,d,year,line in df.iter_rows():
    m=re.search(metric,line,re.I)
    if not m: continue
    val=None
    if 'respectively' in line:
        values=re.search(r'were (.*?)\s*,? respectively',line)
        if values:
            nums=re.findall(number,values.group(1))
            before=line[:values.start()]
            # Human acreage is first or second metric in these paired sentences.
            idx=0 if re.match(metric,before,re.I) or re.match(r'.*?[:\]—)]\s*'+metric,before,re.I) else 1
            if idx<len(nums): val=nums[idx]
    if val is None:
        tail=line[m.end():]
        hit=re.match(r'\s*(?:(?:in .*? (?:stood at|were))|(?:totaled|reached|stood at|at|=))?\s*\(?('+number+r')',tail,re.I)
        if hit: val=hit.group(1)
        else:
            hit=re.search('('+number+r')\s*$',line[:m.start()])
            if hit: val=hit.group(1)
    if val and val!='N/A': observations.append((area,d,year,int(re.sub('[, ]','',val)),line))
obs=pl.DataFrame(observations,schema=['area','date','year','acres','line'],orient='row')
annual=obs.sort('date').group_by('area','year').last()
annual.write_csv('/workspace/work/annual_acres.csv')
# Match region names against the GACC descriptions, allowing the singular Rocky Mountain name.
gacc=pl.read_parquet(base/'geo/gacc_2025.parquet').select('GACCUnitID','GACCDescription')
mapping=[]
for area in obs['area'].unique():
    needle=area.replace('Rocky Mountains','Rocky Mountain')
    matches=gacc.filter(pl.col('GACCDescription').str.contains('(?i)'+re.escape(needle)))
    if matches.height:
        abbreviations=re.findall(r'\b[A-Z]{2,5}CC\b',' '.join(matches['GACCDescription']))
        if abbreviations: mapping.append((area,max(set(abbreviations),key=abbreviations.count)))
ranked=annual.join(pl.DataFrame(mapping,schema=['area','gacc'],orient='row'),on='area').group_by('gacc').agg(pl.col('acres').sum()).sort('acres',descending=True)
print(ranked)
ranked.write_csv('/workspace/work/totals.csv')
Path('/workspace/work/answer.json').write_text(json.dumps({'answer':ranked['gacc'][0]}))
