# Databricks notebook source
# MAGIC %md
# MAGIC # ETL Pipeline - Extract Phase
# MAGIC
# MAGIC This notebook extracts raw data from source systems and loads it into a Delta table.
# MAGIC Managed by Databricks Asset Bundles (DAB).

# COMMAND ----------

# Import required libraries
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit
# dbutils is available in Databricks runtime

# COMMAND ----------

# Get parameters from DAB job configuration
dbutils.widgets.text("source_table", "hive_metastore.dab_lab.raw_customer_data")
dbutils.widgets.text("target_table", "hive_metastore.dab_lab.raw_data")
dbutils.widgets.text("environment", "dev")

source_table = dbutils.widgets.get("source_table")
target_table = dbutils.widgets.get("target_table")
environment = dbutils.widgets.get("environment")

print(f"Extract Configuration:")
print(f"  Source Table: {source_table}")
print(f"  Target Table: {target_table}")
print(f"  Environment: {environment}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Extract Data from Source

# COMMAND ----------

# Read from source table created by setup job
df_source = spark.table(source_table)

print(f"Extracted {df_source.count()} records from {source_table}")
df_source.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Add Metadata Columns

# COMMAND ----------

# Add metadata for data lineage and auditing
df_enriched = df_source \
    .withColumn("extraction_timestamp", current_timestamp()) \
    .withColumn("source_system", lit("sample_dataset")) \
    .withColumn("environment", lit(environment))

print(f"Added metadata columns")
df_enriched.show(5)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write to Delta Table

# COMMAND ----------

# Write data to Delta table with overwrite mode
df_enriched.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(target_table)

print(f"Successfully wrote {df_enriched.count()} records to {target_table}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Data Quality

# COMMAND ----------

# Basic data quality check
df_verify = spark.table(target_table)
record_count = df_verify.count()

assert record_count > 0, "No records found in target table"
print(f"✅ Data quality check passed: {record_count} records in {target_table}")

# COMMAND ----------

# Return success status for DAB job monitoring
dbutils.notebook.exit(f"Extract completed: {record_count} records")
