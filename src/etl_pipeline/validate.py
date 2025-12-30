# Databricks notebook source
# MAGIC %md
# MAGIC # ETL Pipeline - Validation Phase
# MAGIC
# MAGIC This notebook runs data quality checks on the final data.
# MAGIC Managed by Databricks Asset Bundles (DAB).

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when, isnan, isnull
# dbutils is available in Databricks runtime

# COMMAND ----------

# Get parameters
dbutils.widgets.text("target_table", "dev_catalog.dab_lab.final_data")
dbutils.widgets.text("min_row_count", "100")
dbutils.widgets.text("environment", "dev")

target_table = dbutils.widgets.get("target_table")
min_row_count = int(dbutils.widgets.get("min_row_count"))
environment = dbutils.widgets.get("environment")

print(f"Validation Configuration:")
print(f"  Target Table: {target_table}")
print(f"  Minimum Row Count: {min_row_count}")
print(f"  Environment: {environment}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Data for Validation

# COMMAND ----------

df = spark.table(target_table)
total_rows = df.count()
print(f"Total rows in {target_table}: {total_rows}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Quality Checks

# COMMAND ----------

# Check 1: Minimum row count
assert total_rows >= min_row_count, f"Row count {total_rows} is below minimum {min_row_count}"
print(f"✅ Row count check passed: {total_rows} >= {min_row_count}")

# COMMAND ----------

# Check 2: No null customer IDs
null_customer_ids = df.filter(col("customer_id").isNull()).count()
assert null_customer_ids == 0, f"Found {null_customer_ids} null customer IDs"
print(f"✅ Customer ID check passed: No null values")

# COMMAND ----------

# Check 3: Data quality score distribution
quality_distribution = df.groupBy("data_quality_score").count().orderBy("data_quality_score")
print("Quality Score Distribution:")
quality_distribution.show()

avg_quality_score = df.agg({"data_quality_score": "avg"}).collect()[0][0]
assert avg_quality_score >= 0.5, f"Average quality score {avg_quality_score} is below 0.5"
print(f"✅ Quality score check passed: {avg_quality_score:.2f} >= 0.5")

# COMMAND ----------

# Check 4: Check for duplicate customer IDs
duplicate_count = df.groupBy("customer_id").count().filter(col("count") > 1).count()
assert duplicate_count == 0, f"Found {duplicate_count} duplicate customer IDs"
print(f"✅ Duplicate check passed: No duplicates found")

# COMMAND ----------

# Check 5: Active records percentage
active_count = df.filter(col("is_active") == True).count()
active_percentage = (active_count / total_rows) * 100
print(f"Active records: {active_count} ({active_percentage:.2f}%)")

assert active_percentage >= 50, f"Active records percentage {active_percentage}% is below 50%"
print(f"✅ Active records check passed: {active_percentage:.2f}% >= 50%")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Column Completeness Analysis

# COMMAND ----------

# Check null percentages for all columns
print("Column Completeness Analysis:")
for column in df.columns:
    null_count = df.filter(col(column).isNull()).count()
    null_percentage = (null_count / total_rows) * 100
    print(f"  {column}: {null_percentage:.2f}% null values")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Validation Summary

# COMMAND ----------

validation_results = {
    "total_rows": total_rows,
    "avg_quality_score": avg_quality_score,
    "active_percentage": active_percentage,
    "validation_status": "PASSED",
    "timestamp": spark.sql("SELECT current_timestamp()").collect()[0][0]
}

print("\n" + "="*50)
print("VALIDATION SUMMARY")
print("="*50)
for key, value in validation_results.items():
    print(f"  {key}: {value}")
print("="*50)

# COMMAND ----------

# Return success status
dbutils.notebook.exit(f"Validation PASSED: {total_rows} rows, quality {avg_quality_score:.2f}")
