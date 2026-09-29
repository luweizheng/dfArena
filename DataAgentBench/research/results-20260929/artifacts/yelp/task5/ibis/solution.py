import json
from pathlib import Path
import ibis


def main():
    con = ibis.duckdb.connect()
    business = con.read_parquet('/workspace/data/businessinfo/business.parquet')
    reviews = con.read_parquet('/workspace/data/user/review.parquet')
    states = dict(item.split(':', 1) for item in (
        'AL:Alabama|AK:Alaska|AZ:Arizona|AR:Arkansas|CA:California|CO:Colorado|CT:Connecticut|DE:Delaware|FL:Florida|GA:Georgia|HI:Hawaii|ID:Idaho|IL:Illinois|IN:Indiana|IA:Iowa|KS:Kansas|KY:Kentucky|LA:Louisiana|ME:Maine|MD:Maryland|MA:Massachusetts|MI:Michigan|MN:Minnesota|MS:Mississippi|MO:Missouri|MT:Montana|NE:Nebraska|NV:Nevada|NH:New Hampshire|NJ:New Jersey|NM:New Mexico|NY:New York|NC:North Carolina|ND:North Dakota|OH:Ohio|OK:Oklahoma|OR:Oregon|PA:Pennsylvania|RI:Rhode Island|SC:South Carolina|SD:South Dakota|TN:Tennessee|TX:Texas|UT:Utah|VT:Vermont|VA:Virginia|WA:Washington|WV:West Virginia|WI:Wisconsin|WY:Wyoming'
    ).split('|'))
    # DuckDB's JSON parser preserves the string-valued WiFi dictionary entry.
    enriched = business.mutate(
        wifi=business.attributes.cast('json')['WiFi'].str,
        state=business.description.re_extract(r', ([A-Z]{2}),', 1),
        business_ref=business.business_id.replace('businessid_', 'businessref_'),
    )
    eligible = enriched.filter(
        enriched.wifi.isin(["u'free'", "'free'", "u'paid'", "'paid'", 'free', 'paid']),
        enriched.state.isin(list(states)),
    )
    counts = eligible.group_by('state').aggregate(business_count=eligible.business_id.nunique())
    winners = counts.filter(counts.business_count == counts.business_count.max())
    selected = eligible.semi_join(winners, 'state').select('state', 'business_ref').distinct()
    joined = reviews.inner_join(selected, 'business_ref')
    ratings = joined.group_by('state').aggregate(average_rating=joined.rating.mean(), review_count=joined.count())
    result = winners.join(ratings, 'state').order_by('state').to_pyarrow().to_pylist()
    answer = '; '.join(
        f"{states[row['state']]} has {row['business_count']} businesses offering WiFi, with an average review rating of {row['average_rating']:.2f} out of 5."
        for row in result
    )
    Path('/workspace/work/answer.json').write_text(json.dumps({'answer': answer}) + '\n')
    print(json.dumps(result, indent=2))
    print(answer)


if __name__ == '__main__':
    main()
