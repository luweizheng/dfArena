import json
from pathlib import Path
import ibis

OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
recipients = con.read_parquet('/workspace/data/recipients_db/recipients.parquet')
# Strip only trailing corporate designators and their separating comma/space.
# Punctuation elsewhere in the recipient's name is intentionally retained.
suffix = r'(?:incorporated|inc\.?|corporation|corp\.?|company|co\.?|limited|ltd\.?|l\.?l\.?c\.?|l\.?l\.?p\.?|l\.?p\.?|p\.?c\.?|p\.?a\.?|pbc|gmbh|s\.?r\.?l\.?|s\.?p\.?a\.?)'
name = recipients.name.strip().upper()
pattern = r'(?i)(?:[,\s]+' + suffix + r')+$'
name = name.re_replace(pattern, '').strip()
# The supplied UEIs use case and wrapper variants; remove these wrappers only.
uei = recipients.uei.strip().upper().re_replace(r'^UEI:', '').re_replace(r'-UEI$', '')
normalized = recipients.mutate(recipient=name, canonical_uei=uei)
groups = normalized.filter(normalized.recipient.notnull(), normalized.recipient != '').group_by('recipient').aggregate(uei_count=ibis._.canonical_uei.nunique())
multiple = groups.filter(groups.uei_count > 1)
count = int(multiple.count().execute())
(OUT / 'answer.json').write_text(json.dumps({'answer': str(count)}) + '\n')
(OUT / 'recipient_counts.json').write_text(json.dumps(multiple.order_by('recipient').to_pyarrow().to_pylist(), indent=2) + '\n')
print(count)
