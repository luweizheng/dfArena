# yelp

The original two data groups are exposed as local Parquet tables.

Original group names remain below for interpreting the original hints. File paths are relative to this dataset root.

1. businessinfo_database
   - This database is provided as Parquet tables and contains metadata and user check-in records for Yelp businesses. It captures business attributes, service descriptions, operating hours, and user visit timestamps.
   - This database consists of two collections:
     - business
       - This collection contains metadata for businesses listed on Yelp, including names, identifiers, operational status, attributes, business hours, and service/location descriptions.
       - Fields:
         - _id (string): Original MongoDB ObjectId encoded reversibly as 24 lowercase hexadecimal characters
         - business_id (str): Unique business identifier
         - name (str): Business name
         - review_count (int): Total number of reviews
         - is_open (int): Whether business is currently open (1=open, 0=closed)
         - attributes (JSON object text or null): Business attributes (parking, WiFi, etc.)
         - hours (JSON object text or null): Operating hours
         - description (str): Business description including location information

     - checkin
       - This collection records the check-in behavior of Yelp users at various businesses, capturing the timestamped log of user presence.
       - Fields:
         - _id (string): Original MongoDB ObjectId encoded reversibly as 24 lowercase hexadecimal characters
         - business_id (str): Business identifier linking to business collection
         - date (str): Original comma-separated check-in timestamp text; it is not a BSON list in this snapshot

2. user_database
   - This database is provided as Parquet tables and contains user profiles and user-generated content from Yelp, including written reviews, tips, and engagement statistics such as review counts, votes, and elite status.
   - This database consists of three tables:
     - review
       - This table contains user-generated reviews of businesses on Yelp, including rating scores, review content, and metadata such as user and business reference identifiers.
       - Fields:
         - review_id (str): Unique review identifier
         - user_id (str or null): User identifier
         - business_ref (str): Business identifier linking to the business collection
         - rating (int): Rating score (1-5)
         - useful (int): Useful votes received
         - funny (int): Funny votes received
         - cool (int): Cool votes received
         - text (str): Review text content
         - date (str): Review date

     - tip
       - This table contains short user tips about Yelp businesses, usually concise suggestions or comments, along with optional compliments and timestamps.
       - Fields:
         - user_id (str or null): User identifier
         - business_ref (str): Business identifier linking to the business collection
         - text (str): Tip text content
         - date (str): Tip date
         - compliment_count (int): Number of compliments received

     - user
       - This table contains user profile information from Yelp, including activity statistics and membership history.
       - Fields:
         - user_id (str): Unique user identifier
         - name (str): User name
         - review_count (int): Total reviews written by user
         - yelping_since (str): Registration date
         - useful (int): Total useful votes received
         - funny (int): Total funny votes received
         - cool (int): Total cool votes received
         - elite (str): Elite status years
## Dictionary representation

`attributes` and `hours` preserve their original dictionaries as JSON object text. A source null remains a Parquet null; an empty object, when present, is JSON `{}`. An absent dictionary key is not added with a null value. The original key order and string values are retained. Decode non-null cells with a JSON parser when dictionary access is needed. All attribute values in this snapshot are strings: text such as `True`, `False`, `None`, `u'no'`, and parking descriptions is not converted to booleans, nulls, or nested objects. Do not treat these strings as executable code.

## Files and measured physical types

### business

File: `data/businessinfo/business.parquet`

| Column | Arrow type |
|---|---|
| `_id` | string |
| `business_id` | string |
| `name` | string |
| `review_count` | int32 |
| `is_open` | int32 |
| `attributes` | string |
| `hours` | string |
| `description` | string |

### checkin

File: `data/businessinfo/checkin.parquet`

| Column | Arrow type |
|---|---|
| `_id` | string |
| `business_id` | string |
| `date` | string |

### review

File: `data/user/review.parquet`

| Column | Arrow type |
|---|---|
| `review_id` | string |
| `user_id` | string |
| `business_ref` | string |
| `rating` | int64 |
| `useful` | int64 |
| `funny` | int64 |
| `cool` | int64 |
| `text` | string |
| `date` | string |

### tip

File: `data/user/tip.parquet`

| Column | Arrow type |
|---|---|
| `user_id` | string |
| `business_ref` | string |
| `text` | string |
| `date` | string |
| `compliment_count` | int64 |

### user

File: `data/user/user.parquet`

| Column | Arrow type |
|---|---|
| `user_id` | string |
| `name` | string |
| `review_count` | int64 |
| `yelping_since` | string |
| `useful` | int64 |
| `funny` | int64 |
| `cool` | int64 |
| `elite` | string |

## Preservation

Every original record, repeated row, null, empty string, and text character is retained. Check-in timestamps remain one string per source document. Business identifier prefixes and reference fields remain unchanged; interpret their relationship using the original optional hints. No location/category extraction, joins, cleaning, deduplication, rating aggregation, attribute truth-value inference, or answer computation has been performed. Dates remain strings; BSON integers remain int32 and DuckDB BIGINT remains int64.
