# Databricks notebook source
# MAGIC %md
# MAGIC # Setup Sample Data for DAB Lab
# MAGIC
# MAGIC This notebook creates sample data for testing the DAB pipelines.
# MAGIC Run this once after Terraform deployment to initialize the environment.

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, expr, current_timestamp, rand
from datetime import datetime, timedelta
import random

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

# Get parameters or use defaults
dbutils.widgets.text("catalog", "hive_metastore")
dbutils.widgets.text("schema", "dab_lab")

catalog = dbutils.widgets.get("catalog")
schema_name = dbutils.widgets.get("schema")

print(f"Creating sample data in: {catalog}.{schema_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Schema

# COMMAND ----------

# Create schema if not exists
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema_name}")
spark.sql(f"USE {catalog}.{schema_name}")

print(f"Schema {catalog}.{schema_name} ready")

# Note: MLflow experiments directory is created by Terraform
# Path: /Shared/dab-lab/experiments

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Sample Source Data for ETL Pipeline

# COMMAND ----------

# Generate sample customer data
sample_size = 1000

# Create sample data with realistic patterns
data = []
for i in range(sample_size):
    customer_id = f"CUST_{i:06d}"

    # 80% of records have name, 90% have email, 85% have phone
    customer_name = f"Customer {i}" if random.random() < 0.8 else None
    email = f"customer{i}@example.com" if random.random() < 0.9 else None
    phone = f"+1-555-{random.randint(1000000, 9999999)}" if random.random() < 0.85 else None

    # Random amounts
    amount = round(random.uniform(10, 5000), 2)

    # Random timestamp in last 30 days
    days_ago = random.randint(0, 30)
    created_at = (datetime.now() - timedelta(days=days_ago)).isoformat()

    data.append((customer_id, customer_name, email, phone, amount, created_at))

# Create DataFrame
df_source = spark.createDataFrame(
    data,
    ["customer_id", "customer_name", "email", "phone", "amount", "created_at"]
)

# Write to Delta table
source_table = f"{catalog}.{schema_name}.raw_customer_data"
df_source.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(source_table)

print(f"✅ Created source table: {source_table}")
print(f"   Records: {df_source.count()}")
df_source.show(5)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify ETL Pipeline Tables

# COMMAND ----------

# Show table info
spark.sql(f"DESCRIBE TABLE {source_table}").show()

# Show sample records
print(f"\nSample data from {source_table}:")
spark.table(source_table).show(10, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup Summary

# COMMAND ----------

summary = f"""
{'='*60}
SAMPLE DATA SETUP COMPLETE
{'='*60}

Schema: {catalog}.{schema_name}

Tables Created:
1. {source_table}
   - {df_source.count()} sample records
   - Ready for ETL pipeline

ETL Pipeline Flow:
1. Extract: Reads from {source_table}
2. Transform: Cleans and enriches data
3. Load: Writes to transformed_data and final_data
4. Validate: Checks data quality

ML Training Pipeline Flow:
1. Prepare: Uses final_data from ETL pipeline
2. Train: Builds ML model
3. Evaluate: Tests model performance
4. Register: Saves to MLflow Model Registry

Next Steps:
1. Run ETL pipeline first to create final_data table
2. Then run ML Training pipeline

To run pipelines via DAB:
  databricks bundle run etl_pipeline --target dev
  databricks bundle run ml_training --target dev

{'='*60}
"""

print(summary)

# COMMAND ----------

# Store setup info
dbutils.jobs.taskValues.set(key="source_table", value=source_table)
dbutils.jobs.taskValues.set(key="record_count", value=df_source.count())

# COMMAND ----------

dbutils.notebook.exit(f"Sample data created: {df_source.count()} records in {source_table}")
