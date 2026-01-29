# Location 1: DataFrame creation / transformation section where df_pchg_audit is defined or populated
# Add the NEXT_PRICE column by extracting it from source data or computing it
# Assuming df_pchg_audit is a pandas DataFrame and source data has 'next_price' field
# Example snippet to add after df_pchg_audit is created or loaded:
df_pchg_audit['NEXT_PRICE'] = df_pchg_audit.apply(
    lambda row: row.get('next_price') if 'next_price' in row else None, axis=1
)  # [AG-4] Add NEXT_PRICE column for price change audit integration
# Location 2: JSON serialization or dictionary defining audit attributes
# Assuming there is a dictionary or JSON object mapping column names for export or schema definition,
# add 'NEXT_PRICE' field to it.
# For example, if there is a dictionary like audit_fields or json structure:
if 'audit_fields' in globals():
    audit_fields['NEXT_PRICE'] = 'next_price'  # [AG-4] Include NEXT_PRICE in audit fields
# Or if JSON serialization is done by selecting columns explicitly:
# Add 'NEXT_PRICE' to the list of columns to be serialized/exported
if 'audit_columns' in globals():
    if 'NEXT_PRICE' not in audit_columns:
        audit_columns.append('NEXT_PRICE')  # [AG-4] Add NEXT_PRICE to export columns