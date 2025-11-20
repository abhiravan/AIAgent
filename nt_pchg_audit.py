@@ -1,10 +1,20 @@
from pyspark.sql import Window
from pyspark.sql.functions import lead, col

# Existing imports and code
 
def process_price_changes(df):
    # existing processing logic here

    # Add NEXT_PRICE column using window function lead to get next price ordered by some key and timestamp
    # Assuming df has columns 'price' and 'timestamp' and some partition key 'product_id'
    window_spec = Window.partitionBy("product_id").orderBy("timestamp")
    df = df.withColumn("NEXT_PRICE", lead(col("price")).over(window_spec))

    return df
