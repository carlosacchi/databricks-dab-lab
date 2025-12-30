# Databricks notebook source
# MAGIC %md
# MAGIC # ETL Pipeline - Transform Phase
# MAGIC
# MAGIC This notebook transforms and cleans raw data.
# MAGIC Managed by Databricks Asset Bundles (DAB).

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, when, trim, upper, regexp_replace,
    current_timestamp, coalesce, lit
)
# dbutils is available in Databricks runtime

# COMMAND ----------

# Get parameters
dbutils.widgets.text("source_table", "dev_catalog.dab_lab.raw_data")
dbutils.widgets.text("target_table", "dev_catalog.dab_lab.transformed_data")
dbutils.widgets.text("environment", "dev")

source_table = dbutils.widgets.get("source_table")
target_table = dbutils.widgets.get("target_table")
environment = dbutils.widgets.get("environment")

print(f"Transform Configuration:")
print(f"  Source Table: {source_table}")
print(f"  Target Table: {target_table}")
print(f"  Environment: {environment}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Raw Data

# COMMAND ----------

df_raw = spark.table(source_table)
print(f"Loaded {df_raw.count()} records from {source_table}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Cleansing and Transformation

# COMMAND ----------

# Apply transformations
df_transformed = df_raw \
    .withColumn("customer_name",
                when(col("customer_name").isNotNull(),
                     trim(upper(col("customer_name"))))
                .otherwise("UNKNOWN")) \
    .withColumn("email",
                when(col("email").isNotNull(),
                     trim(col("email").cast("string")))
                .otherwise(None)) \
    .withColumn("phone",
                regexp_replace(col("phone").cast("string"), "[^0-9]", "")) \
    .withColumn("transformation_timestamp", current_timestamp()) \
    .withColumn("data_quality_score",
                when((col("customer_name") != "UNKNOWN") &
                     col("email").isNotNull(), lit(1.0))
                .when((col("customer_name") != "UNKNOWN") |
                      col("email").isNotNull(), lit(0.5))
                .otherwise(lit(0.0)))

# Remove duplicates based on customer_id
df_transformed = df_transformed.dropDuplicates(["customer_id"])

print(f"Transformed {df_transformed.count()} records")
df_transformed.show(5)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Quality Statistics

# COMMAND ----------

# Calculate and display quality metrics
quality_stats = df_transformed.agg({
    "data_quality_score": "avg",
    "customer_id": "count"
}).collect()[0]

avg_quality = quality_stats["avg(data_quality_score)"]
total_records = quality_stats["count(customer_id)"]

print(f"Data Quality Metrics:")
print(f"  Total Records: {total_records}")
print(f"  Average Quality Score: {avg_quality:.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write Transformed Data

# COMMAND ----------

df_transformed.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(target_table)

print(f"Successfully wrote {df_transformed.count()} records to {target_table}")

# COMMAND ----------

# Return success status
dbutils.notebook.exit(f"Transform completed: {df_transformed.count()} records, quality score: {avg_quality:.2f}")
