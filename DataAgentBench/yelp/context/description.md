# yelp

The original two data groups are exposed as local Parquet tables. Original group names are retained for interpreting the original hints. All file paths are relative to this dataset root.

## businessinfo_database

Business metadata and user check-in records for Yelp businesses, covering business attributes, service descriptions, operating hours, and user visit timestamps.

### business

Metadata for businesses listed on Yelp, including names, identifiers, operational status, attributes, business hours, and service/location descriptions.

File: `data/businessinfo/business.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `_id` | string | Original MongoDB ObjectId encoded reversibly as 24 lowercase hexadecimal characters |
| `business_id` | string | Unique business identifier |
| `name` | string | Business name |
| `review_count` | int32 | Total number of reviews |
| `is_open` | int32 | Whether business is currently open (1=open, 0=closed) |
| `attributes` | string | Business attributes (parking, WiFi, etc.); may be null; stored as JSON object text |
| `hours` | string | Operating hours; may be null; stored as JSON object text |
| `description` | string | Business description including location information |

### checkin

Timestamped log of user presence at Yelp businesses.

File: `data/businessinfo/checkin.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `_id` | string | Original MongoDB ObjectId encoded reversibly as 24 lowercase hexadecimal characters |
| `business_id` | string | Business identifier linking to business collection |
| `date` | string | Original comma-separated check-in timestamp text; it is not a BSON list in this snapshot |

## user_database

User profiles and user-generated content from Yelp, including written reviews, tips, and engagement statistics such as review counts, votes, and elite status.

### review

User-generated reviews of businesses on Yelp, including rating scores, review content, and user and business reference identifiers.

File: `data/user/review.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `review_id` | string | Unique review identifier |
| `user_id` | string | User identifier; may be null |
| `business_ref` | string | Business identifier linking to the business collection |
| `rating` | int64 | Rating score (1-5) |
| `useful` | int64 | Useful votes received |
| `funny` | int64 | Funny votes received |
| `cool` | int64 | Cool votes received |
| `text` | string | Review text content |
| `date` | string | Review date |

### tip

Short user tips about Yelp businesses, usually concise suggestions or comments, with optional compliments and timestamps.

File: `data/user/tip.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `user_id` | string | User identifier; may be null |
| `business_ref` | string | Business identifier linking to the business collection |
| `text` | string | Tip text content |
| `date` | string | Tip date |
| `compliment_count` | int64 | Number of compliments received |

### user

User profile information, including activity statistics and membership history.

File: `data/user/user.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `user_id` | string | Unique user identifier |
| `name` | string | User name |
| `review_count` | int64 | Total reviews written by user |
| `yelping_since` | string | Registration date |
| `useful` | int64 | Total useful votes received |
| `funny` | int64 | Total funny votes received |
| `cool` | int64 | Total cool votes received |
| `elite` | string | Elite status years |

## Dictionary representation

`attributes` and `hours` preserve their original dictionaries as JSON object text. A source null remains a Parquet null; an empty object, when present, is JSON `{}`. An absent dictionary key is not added with a null value. The original key order and string values are retained. Decode non-null cells with a JSON parser when dictionary access is needed. All attribute values in this snapshot are strings: text such as `True`, `False`, `None`, `u'no'`, and parking descriptions is not converted to booleans, nulls, or nested objects. Do not treat these strings as executable code.

## Representation

Dates are strings. Interpret business identifier prefixes and reference fields using the optional hints.
