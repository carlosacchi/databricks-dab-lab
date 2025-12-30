# Databricks notebook source
# MAGIC %md
# MAGIC # ML Training Pipeline - Model Training
# MAGIC
# MAGIC This notebook trains an ML model with hyperparameter tuning using MLflow.
# MAGIC Managed by Databricks Asset Bundles (DAB).

# COMMAND ----------

from pyspark.sql import SparkSession
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import mlflow
import mlflow.sklearn
import pandas as pd
# dbutils is available in Databricks runtime

# COMMAND ----------

# Get parameters
dbutils.widgets.text("feature_table", "dev_catalog.dab_lab.ml_features")
dbutils.widgets.text("model_name", "dab_lab_model")
dbutils.widgets.text("experiment_path", "/Shared/dab-lab/experiments/dev")
dbutils.widgets.text("max_trials", "10")
dbutils.widgets.text("environment", "dev")

feature_table = dbutils.widgets.get("feature_table")
model_name = dbutils.widgets.get("model_name")
experiment_path = dbutils.widgets.get("experiment_path")
max_trials = int(dbutils.widgets.get("max_trials"))
environment = dbutils.widgets.get("environment")

print(f"Training Configuration:")
print(f"  Feature Table: {feature_table}")
print(f"  Model Name: {model_name}")
print(f"  Experiment Path: {experiment_path}")
print(f"  Max Trials: {max_trials}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup MLflow Experiment

# COMMAND ----------

# Set MLflow experiment (creates if doesn't exist)
mlflow.set_experiment(experiment_path)
print(f"Using MLflow experiment: {experiment_path}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Training Data

# COMMAND ----------

train_table = f"{feature_table}_train"
test_table = f"{feature_table}_test"

df_train_spark = spark.table(train_table)
df_test_spark = spark.table(test_table)

# Convert to Pandas for scikit-learn
df_train = df_train_spark.toPandas()
df_test = df_test_spark.toPandas()

print(f"Train set: {len(df_train)} records")
print(f"Test set: {len(df_test)} records")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Prepare Features and Target

# COMMAND ----------

# Define feature columns (exclude customer_id and target)
feature_cols = [
    "customer_name_length",
    "has_email",
    "has_phone",
    "customer_id_hash",
    "data_quality_score"
]

X_train = df_train[feature_cols]
y_train = df_train["target"]
X_test = df_test[feature_cols]
y_test = df_test["target"]

print(f"Feature columns: {feature_cols}")
print(f"Target distribution in train: {y_train.value_counts().to_dict()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Hyperparameter Tuning

# COMMAND ----------

import itertools
import numpy as np

# Define hyperparameter grid
param_grid = {
    'n_estimators': [50, 100, 150],
    'max_depth': [5, 10, 15, None],
    'min_samples_split': [2, 5, 10]
}

# Generate all combinations (limit to max_trials)
param_combinations = list(itertools.product(*param_grid.values()))
np.random.seed(42)
selected_params = param_combinations[:min(max_trials, len(param_combinations))]

print(f"Testing {len(selected_params)} hyperparameter combinations")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Train Models with MLflow Tracking

# COMMAND ----------

best_model = None
best_score = 0
best_run_id = None

for i, params in enumerate(selected_params):
    param_dict = dict(zip(param_grid.keys(), params))

    with mlflow.start_run(run_name=f"rf_trial_{i+1}") as run:
        # Train model
        clf = RandomForestClassifier(
            n_estimators=param_dict['n_estimators'],
            max_depth=param_dict['max_depth'],
            min_samples_split=param_dict['min_samples_split'],
            random_state=42,
            n_jobs=-1
        )

        clf.fit(X_train, y_train)

        # Make predictions
        y_pred_train = clf.predict(X_train)
        y_pred_test = clf.predict(X_test)

        # Calculate metrics
        train_accuracy = accuracy_score(y_train, y_pred_train)
        test_accuracy = accuracy_score(y_test, y_pred_test)
        precision = precision_score(y_test, y_pred_test, average='weighted')
        recall = recall_score(y_test, y_pred_test, average='weighted')
        f1 = f1_score(y_test, y_pred_test, average='weighted')

        # Log parameters and metrics
        mlflow.log_params(param_dict)
        mlflow.log_metric("train_accuracy", train_accuracy)
        mlflow.log_metric("test_accuracy", test_accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1_score", f1)

        # Log feature importance
        feature_importance = dict(zip(feature_cols, clf.feature_importances_))
        mlflow.log_dict(feature_importance, "feature_importance.json")

        # Log model
        mlflow.sklearn.log_model(clf, "model")

        print(f"Trial {i+1}: Test Accuracy = {test_accuracy:.4f}, F1 = {f1:.4f}")

        # Track best model
        if test_accuracy > best_score:
            best_score = test_accuracy
            best_model = clf
            best_run_id = run.info.run_id

# COMMAND ----------

# MAGIC %md
# MAGIC ## Best Model Summary

# COMMAND ----------

print(f"\n{'='*50}")
print(f"BEST MODEL RESULTS")
print(f"{'='*50}")
print(f"Run ID: {best_run_id}")
print(f"Test Accuracy: {best_score:.4f}")
print(f"Feature Importance:")
for feat, imp in zip(feature_cols, best_model.feature_importances_):
    print(f"  {feat}: {imp:.4f}")
print(f"{'='*50}\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Save Best Run ID for Next Steps

# COMMAND ----------

# Store best run ID for model registration
dbutils.jobs.taskValues.set(key="best_run_id", value=best_run_id)
dbutils.jobs.taskValues.set(key="best_accuracy", value=float(best_score))

print(f"Stored task values:")
print(f"  best_run_id: {best_run_id}")
print(f"  best_accuracy: {best_score}")

# COMMAND ----------

# Return success status
dbutils.notebook.exit(f"Training completed: Best accuracy {best_score:.4f}, Run ID: {best_run_id}")
