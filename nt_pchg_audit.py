# Location 1: SQL query fetching price change audit data (around the code block where latest_audit_df is defined)
# Modify the SQL query to include NEXT_PRICE column
latest_audit_df = spark.sql(f"""
    SELECT uploaded_time, new_price, effective_date, next_price  -- [AG-4] Added next_price column
    FROM {delta_schema}.stg_file_check
    WHERE file_name='pchg_audit'
""")
# Location 2: DataFrame creation/loading section where df_pchg_audit is created from query results
# Assuming df_pchg_audit is created from a Spark DataFrame or pandas DataFrame conversion, add NEXT_PRICE column mapping
df_pchg_audit = latest_audit_df.toPandas()
# [AG-4] Ensure NEXT_PRICE column exists in df_pchg_audit
if 'next_price' in df_pchg_audit.columns:
    df_pchg_audit.rename(columns={'next_price': 'NEXT_PRICE'}, inplace=True)
else:
    df_pchg_audit['NEXT_PRICE'] = None
# Location 3: JSON serialization or dictionary mapping of audit attributes (where audit attributes are prepared for JSON or DB insert)
# Add NEXT_PRICE field to the dictionary or JSON structure
def audit_row_to_dict(row):
    return {
        'uploaded_time': row['uploaded_time'],
        'new_price': row['new_price'],
        'effective_date': row['effective_date'],
        'NEXT_PRICE': row.get('NEXT_PRICE', None),  # [AG-4] Added NEXT_PRICE field
        # ... other fields ...
    }