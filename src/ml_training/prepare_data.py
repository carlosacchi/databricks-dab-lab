# Databricks notebook source
# MAGIC %md
# MAGIC # ML Training Pipeline - Data Preparation
# MAGIC
# MAGIC This notebook prepares training data and creates features for ML model training.
# MAGIC Managed by Databricks Asset Bundles (DAB).

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, hash, abs as spark_abs, length
from sklearn.model_selection import train_test_split
import pandas as pd
# dbutils is available in Databricks runtime

# COMMAND ----------

# Get parameters
dbutils.widgets.text("source_table", "dev_catalog.dab_lab.final_data")
dbutils.widgets.text("feature_table", "dev_catalog.dab_lab.ml_features")
dbutils.widgets.text("test_size", "0.2")
dbutils.widgets.text("random_seed", "42")
dbutils.widgets.text("environment", "dev")

source_table = dbutils.widgets.get("source_table")
feature_table = dbutils.widgets.get("feature_table")
test_size = float(dbutils.widgets.get("test_size"))
random_seed = int(dbutils.widgets.get("random_seed"))
environment = dbutils.widgets.get("environment")

print(f"Data Preparation Configuration:")
print(f"  Source Table: {source_table}")
print(f"  Feature Table: {feature_table}")
print(f"  Test Size: {test_size}")
print(f"  Random Seed: {random_seed}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Source Data

# COMMAND ----------

df_source = spark.table(source_table)
print(f"Loaded {df_source.count()} records from {source_table}")
df_source.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Feature Engineering

# COMMAND ----------

# Create features for ML training
# For this example, we'll create a simple binary classification target
# based on data quality score

df_features = df_source \
    .withColumn("target",
                when(col("data_quality_score") >= 0.8, 1).otherwise(0)) \
    .withColumn("customer_name_length",
                when(col("customer_name").isNotNull(),
                     length(col("customer_name"))).otherwise(0)) \
    .withColumn("has_email",
                when(col("email").isNotNull(), 1).otherwise(0)) \
    .withColumn("has_phone",
                when(col("phone").isNotNull(), 1).otherwise(0)) \
    .withColumn("customer_id_hash",
                spark_abs(hash(col("customer_id"))) % 1000)

# Select relevant columns for ML
feature_columns = [
    "customer_id",
    "customer_name_length",
    "has_email",
    "has_phone",
    "customer_id_hash",
    "data_quality_score",
    "target"
]

df_ml = df_features.select(feature_columns)

print(f"Created {len(feature_columns)} features")
df_ml.show(5)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Train/Test Split

# COMMAND ----------

# Add random split column for train/test
df_ml = df_ml.withColumn("random_value",
                         (spark_abs(hash(col("customer_id"))) % 100) / 100.0)

df_train = df_ml.filter(col("random_value") >= test_size)
df_test = df_ml.filter(col("random_value") < test_size)

train_count = df_train.count()
test_count = df_test.count()

print(f"Train set: {train_count} records ({(train_count/(train_count+test_count)*100):.1f}%)")
print(f"Test set: {test_count} records ({(test_count/(train_count+test_count)*100):.1f}%)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Class Distribution Analysis

# COMMAND ----------

print("Train set target distribution:")
df_train.groupBy("target").count().show()

print("Test set target distribution:")
df_test.groupBy("target").count().show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Save Feature Tables

# COMMAND ----------

# Save complete feature table
df_ml.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(feature_table)

print(f"Saved feature table: {feature_table}")

# Save train and test splits
train_table = f"{feature_table}_train"
test_table = f"{feature_table}_test"

df_train.drop("random_value").write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable(train_table)

df_test.drop("random_value").write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable(test_table)

print(f"Saved train table: {train_table}")
print(f"Saved test table: {test_table}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Feature Statistics

# COMMAND ----------

print("Feature Statistics:")
df_ml.describe().show()

# COMMAND ----------

# Return success status
dbutils.notebook.exit(f"Data preparation completed: {train_count} train, {test_count} test records")
