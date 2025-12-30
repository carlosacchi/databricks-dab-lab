# Databricks notebook source
# MAGIC %md
# MAGIC # ETL Pipeline - Load Phase
# MAGIC
# MAGIC This notebook loads transformed data into final Delta tables with optimizations.
# MAGIC Managed by Databricks Asset Bundles (DAB).

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, date_format, col
# dbutils is available in Databricks runtime

# COMMAND ----------

# Get parameters
dbutils.widgets.text("source_table", "dev_catalog.dab_lab.transformed_data")
dbutils.widgets.text("target_table", "dev_catalog.dab_lab.final_data")
dbutils.widgets.text("environment", "dev")

source_table = dbutils.widgets.get("source_table")
target_table = dbutils.widgets.get("target_table")
environment = dbutils.widgets.get("environment")

print(f"Load Configuration:")
print(f"  Source Table: {source_table}")
print(f"  Target Table: {target_table}")
print(f"  Environment: {environment}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Transformed Data

# COMMAND ----------

df_transformed = spark.table(source_table)
print(f"Loaded {df_transformed.count()} records from {source_table}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Add Business Logic and Final Columns

# COMMAND ----------

# Add final columns for analytics
df_final = df_transformed \
    .withColumn("load_timestamp", current_timestamp()) \
    .withColumn("load_date", date_format(current_timestamp(), "yyyy-MM-dd")) \
    .withColumn("is_active", col("data_quality_score") >= 0.5)

print(f"Prepared {df_final.count()} records for final table")
df_final.show(5)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write to Final Delta Table with Optimization

# COMMAND ----------

# Write with Delta optimizations
df_final.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .option("optimizeWrite", "true") \
    .option("mergeSchema", "false") \
    .saveAsTable(target_table)

print(f"Successfully wrote {df_final.count()} records to {target_table}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Optimize Delta Table

# COMMAND ----------

# Optimize table for query performance
spark.sql(f"OPTIMIZE {target_table}")
print(f"Optimized {target_table}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Collect Statistics

# COMMAND ----------

# Compute statistics for the Catalyst optimizer
spark.sql(f"ANALYZE TABLE {target_table} COMPUTE STATISTICS")
print(f"Computed statistics for {target_table}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Final Verification

# COMMAND ----------

df_verify = spark.table(target_table)
final_count = df_verify.count()

print(f"✅ Load completed successfully:")
print(f"  Records in final table: {final_count}")
print(f"  Table location: {target_table}")

# COMMAND ----------

# Return success status
dbutils.notebook.exit(f"Load completed: {final_count} records in {target_table}")
