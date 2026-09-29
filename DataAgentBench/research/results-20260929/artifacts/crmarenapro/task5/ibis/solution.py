import json
from pathlib import Path
import ibis


def clean_id(col):
    return col.strip().re_replace(r'^#+', '')


def main():
    con = ibis.duckdb.connect()
    cases = con.read_parquet('/workspace/data/support/Case.parquet')
    items = con.read_parquet('/workspace/data/products_orders/OrderItem.parquet')
    cases = cases.select(
        case_id=clean_id(cases.id),
        item_id=clean_id(cases.orderitemid__c),
        issue_id=clean_id(cases.issueid__c),
        created=cases.createddate.cast('timestamp').date(),
    )
    items = items.select(item_id=clean_id(items.Id), product_id=clean_id(items.Product2Id))
    today = ibis.date('2023-01-16')
    start = today - ibis.interval(months=5)
    cases = cases.filter(
        cases.created >= start,
        cases.created <= today,
        cases.issue_id.notnull(),
        cases.issue_id != '',
    )
    product_items = items.filter(items.product_id == '01tWt000006hV8LIAU')
    matched = cases.semi_join(product_items, 'item_id')
    ranked = matched.group_by('issue_id').aggregate(reports=matched.count()).order_by(
        ibis.desc('reports'), 'issue_id'
    )
    rows = ranked.to_pyarrow().to_pylist()
    if not rows:
        raise ValueError('No matching cases')
    if len(rows) > 1 and rows[0]['reports'] == rows[1]['reports']:
        raise ValueError('Most reported issue is tied')
    Path('/workspace/work/answer.json').write_text(json.dumps({'answer': rows[0]['issue_id']}))
    print(json.dumps(rows, indent=2))


if __name__ == '__main__':
    main()
