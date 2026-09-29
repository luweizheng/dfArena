import json
import re
from pathlib import Path
import pandas as pd

ROOT = Path('/workspace/data')
task = json.loads(Path('/workspace/task.json').read_text())
lead_id = re.search(r'Lead Id to be considered is:\s*(\w+)', task['query']).group(1)
calls = pd.read_parquet(ROOT / 'activities/VoiceCallTranscript__c.parquet')
calls = calls[calls['LeadId__c'].str.strip().str.lstrip('#').eq(lead_id)].copy()
calls['date'] = pd.to_datetime(calls['CreatedDate'], utc=True)
latest = calls.sort_values('date').iloc[-1]
body = latest['Body__c'].replace('’', "'")
knowledge = pd.read_parquet(ROOT / 'support/knowledge__kav.parquet')
policy = knowledge.loc[knowledge['title'].str.strip().eq('TechPulse Solution Volume-Based Installation Timeline Policy'), 'faq_answer__c'].iloc[0]

# Interpret the installation schedule as volume tiers, beginning at one unit.
tiers = []
for volume, paragraph in re.findall(r'Volume: (\d+)\)\*\*\s*(.*?)(?=\n\n|$)', policy, re.S):
    days = re.search(r'(\d+) days', paragraph)
    tiers.append((int(volume), int(days.group(1)) if days else 1))
number_words = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}
quantity_text = re.search(r'interested in (\w+) units', body, re.I).group(1).lower()
quantity = number_words.get(quantity_text) or int(quantity_text)
budget = float(re.search(r'budget is \$([\d,]+)', body).group(1).replace(',', ''))
unit_price = float(re.search(r'unit is priced at \$([\d,]+)', body).group(1).replace(',', ''))
installation_days = max((x for x in tiers if x[0] <= quantity), key=lambda x: x[0])[1]
failures = {
    'Budget': quantity * unit_price > budget,
    'Authority': bool(re.search(r"don't have the final say|not the decision.maker|need.*approval", body, re.I)),
    'Need': not bool(re.search(r'enhance our simulation capabilities|great fit', body, re.I)),
    'Timeline': bool(re.search(r'within a day', body, re.I)) and installation_days > 1,
}
answer = ', '.join(factor for factor, failed in failures.items() if failed)
Path('/workspace/work/answer.json').write_text(json.dumps({'answer': answer}))
