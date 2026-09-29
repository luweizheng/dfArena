import json
import re
from pathlib import Path
import polars as pl

ROOT = Path('/workspace/data')
OUT = Path('/workspace/work')
task = json.loads(Path('/workspace/task.json').read_text())
lead_id = re.search(r'00Q\w+', task['query']).group()
calls = (pl.read_parquet(ROOT / 'activities/VoiceCallTranscript__c.parquet')
    .filter(pl.col('LeadId__c').str.strip_chars().str.strip_chars_start('#') == lead_id)
    .sort('CreatedDate'))
assert calls.height
body = calls.row(-1, named=True)['Body__c']
articles = pl.read_parquet(ROOT / 'support/knowledge__kav.parquet')
relevant = articles.filter(pl.col('title').str.contains('(?i)Volume-Based|Mandatory Bundles'))
# Assess the purchase discussed on the qualification call. Mandatory quote
# configuration is not an agreed additional purchase in this discussion.
budget = float(re.search(r'budget is \$([\d,]+)', body).group(1).replace(',', ''))
quoted_total = float(re.search(r'come to \$([\d,]+)', body).group(1).replace(',', ''))
quantity = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}[re.search(r'interested in (\w+) units', body).group(1)]
policy = articles.filter(pl.col('title').str.contains('Installation Timeline Policy'))['faq_answer__c'][0]
tiers = []
# Extract installation tier thresholds and durations from the knowledge article.
for section in re.split(r'\n\n\d+\. ', policy)[1:]:
    volume = re.search(r'Volume: (\d+)', section)
    duration = re.search(r'(\d+) days', section)
    if volume:
        tiers.append((int(volume.group(1)), int(duration.group(1)) if duration else 1))
installation_days = max((t for t in tiers if t[0] <= quantity), key=lambda t:t[0])[1]
failed = []
if quoted_total > budget:
    failed.append('Budget')
if re.search(r'(?:don.t have the final say|not the decision.maker|lack.*authority)', body, re.I):
    failed.append('Authority')
if re.search(r'(?:no need|do not need|don.t need)', body, re.I):
    failed.append('Need')
if 'within a day' in body and installation_days > 1:
    failed.append('Timeline')
(OUT / 'evidence.json').write_text(json.dumps({'calls': calls.to_dicts(), 'articles': relevant.to_dicts(), 'budget': budget, 'quoted_total': quoted_total, 'installation_days': installation_days}, indent=2))
(OUT / 'answer.json').write_text(json.dumps({'answer': ', '.join(failed)}))
print(json.dumps({'answer': ', '.join(failed)}))
