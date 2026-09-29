import json
import re
from pathlib import Path
import ibis

OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
calls = con.read_parquet('/workspace/data/activities/VoiceCallTranscript__c.parquet')
articles = con.read_parquet('/workspace/data/support/knowledge__kav.parquet')
latest = (calls.filter(calls.LeadId__c.strip().re_replace(r'^#', '') == '00QWt0000089AekMAE')
          .order_by(calls.CreatedDate.cast('timestamp').desc()).limit(1)
          .to_pyarrow().to_pylist())
policy = articles.filter(articles.title.lower().contains('installation timeline')).to_pyarrow().to_pylist()
assert latest and policy
body = latest[0]['Body__c']
text = body.lower().replace('’', "'")
failed = []
# Assess the quoted purchase against the explicitly stated available budget.
budget = re.search(r'your budget is \$([\d,]+)', text)
cost = re.search(r'will come to \$([\d,]+)', text)
assert budget and cost
if float(cost[1].replace(',', '')) > float(budget[1].replace(',', '')):
    failed.append('Budget')
# Explicit lack of final say overrides willingness to move forward.
if re.search(r"(?:don’t|don't|do not) have the final say|not the decision.maker|lack.*authority", text):
    failed.append('Authority')
if re.search(r"(?:no need|do not need|don't need|not a.*fit)", text):
    failed.append('Need')
# The policy's next volume threshold is five units (three days).
# Four units do not reach that threshold; there is no explicit missed
# deadline in this discussion, and installation within a day is accepted.
if re.search(r"(?:cannot|can't|unable to) meet.*(?:timeline|deadline)", text):
    failed.append('Timeline')
(OUT / 'evidence.json').write_text(json.dumps({'latest_call': latest, 'installation_policy': policy}, indent=2))
(OUT / 'answer.json').write_text(json.dumps({'answer': ', '.join(failed)}))
