# Location 1: Data extraction SQL query (where price change audit data is fetched)
# Find the SQL query that fetches price change audit data and add NEXT_PRICE column to SELECT
# Example modification inside a function or code block that runs the query:
# Original snippet (example):
# pchg_audit_query = """
# SELECT ITEM_ID, OLD_PRICE, NEW_PRICE, EFFECTIVE_DATE, ...
# FROM price_change_audit_table
# WHERE ...
# """
# Modified snippet with NEXT_PRICE added:
pchg_audit_query = """
SELECT ITEM_ID,
       OLD_PRICE,
       NEW_PRICE,
       NEXT_PRICE,  -- [AG-4] Added NEXT_PRICE column to fetch next price
       EFFECTIVE_DATE,
       ...
FROM price_change_audit_table
WHERE ...
"""
# Location 2: DataFrame creation/loading from source data (after query execution)
# Assuming df_pchg_audit is created from the query result, add NEXT_PRICE column assignment
# Example:
df_pchg_audit = spark.sql(pchg_audit_query).toPandas()
# [AG-4] Ensure NEXT_PRICE column exists and is properly typed
if 'NEXT_PRICE' not in df_pchg_audit.columns:
    df_pchg_audit['NEXT_PRICE'] = None
else:
    df_pchg_audit['NEXT_PRICE'] = df_pchg_audit['NEXT_PRICE'].astype(float)
# Location 3: JSON/dictionary defining audit attributes (e.g., for serialization or export)
# Find dictionary or JSON structure mapping DataFrame columns to JSON keys or export fields
# Example dictionary before:
audit_attributes = {
    'ITEM_ID': 'itemId',
    'OLD_PRICE': 'oldPrice',
    'NEW_PRICE': 'newPrice',
    'EFFECTIVE_DATE': 'effectiveDate',
    # ...
}
# Add NEXT_PRICE mapping:
audit_attributes['NEXT_PRICE'] = 'nextPrice'  # [AG-4] Added NEXT_PRICE attribute
# Location 4: Serialization or export function that converts DataFrame rows to JSON/dict
# Add NEXT_PRICE field to the output dict
# Example inside a function that converts a row to dict/json:
def row_to_dict(row):
    return {
        'itemId': row['ITEM_ID'],
        'oldPrice': row['OLD_PRICE'],
        'newPrice': row['NEW_PRICE'],
        'nextPrice': row['NEXT_PRICE'],  # [AG-4] Include NEXT_PRICE in export
        'effectiveDate': row['EFFECTIVE_DATE'],
        # ...
    }