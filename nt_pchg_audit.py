# Location 1: DataFrame creation/loading section (where df_pchg_audit is created from source data)
# Assuming df_pchg_audit is created by selecting columns from a source DataFrame named source_df or similar
# Add the NEXT_PRICE column by selecting it from source data or initializing if missing
# Example modification (replace or add this near df_pchg_audit creation):
df_pchg_audit = source_df.select(
    "NEW_PRICE",
    "EFFECTIVE_DATE",
    "OTHER_COLUMNS",
    f.col("NEXT_PRICE")  # [AG-4] Add NEXT_PRICE column from source data
)
# If df_pchg_audit is a pandas DataFrame created from spark DataFrame or other source:
# df_pchg_audit['NEXT_PRICE'] = source_df.select("next_price").toPandas()['next_price']
# Location 2: Column list or schema definition used for processing or validation
# Add 'NEXT_PRICE' to the list of columns wherever columns are defined for df_pchg_audit
columns = [
    "NEW_PRICE",
    "EFFECTIVE_DATE",
    "OTHER_COLUMNS",
    "NEXT_PRICE"  # [AG-4] Include NEXT_PRICE in audit columns
]
# Location 3: JSON serialization or dictionary mapping of audit attributes
# Add 'NEXT_PRICE' to the dictionary or JSON structure that maps DataFrame columns to JSON keys
audit_json_dict = {
    "new_price": row["NEW_PRICE"],
    "effective_date": row["EFFECTIVE_DATE"],
    "other_attributes": row["OTHER_COLUMNS"],
    "next_price": row["NEXT_PRICE"],  # [AG-4] Add NEXT_PRICE to JSON output
}