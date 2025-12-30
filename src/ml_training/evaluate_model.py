# Databricks notebook source
# MAGIC %md
# MAGIC # ML Training Pipeline - Model Evaluation
# MAGIC
# MAGIC This notebook evaluates the trained model and generates performance reports.
# MAGIC Managed by Databricks Asset Bundles (DAB).

# COMMAND ----------

from pyspark.sql import SparkSession
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)
import mlflow
import mlflow.sklearn
import pandas as pd
import matplotlib.pyplot as plt
# dbutils is available in Databricks runtime

# COMMAND ----------

# Get parameters
dbutils.widgets.text("model_name", "dab_lab_model")
dbutils.widgets.text("feature_table", "dev_catalog.dab_lab.ml_features")
dbutils.widgets.text("min_accuracy", "0.75")
dbutils.widgets.text("environment", "dev")

model_name = dbutils.widgets.get("model_name")
feature_table = dbutils.widgets.get("feature_table")
min_accuracy = float(dbutils.widgets.get("min_accuracy"))
environment = dbutils.widgets.get("environment")

print(f"Evaluation Configuration:")
print(f"  Model Name: {model_name}")
print(f"  Feature Table: {feature_table}")
print(f"  Minimum Accuracy: {min_accuracy}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Retrieve Best Model from Previous Task

# COMMAND ----------

# Get best run ID from previous task
try:
    best_run_id = dbutils.jobs.taskValues.get(taskKey="train_model", key="best_run_id")
    best_accuracy = dbutils.jobs.taskValues.get(taskKey="train_model", key="best_accuracy")
    print(f"Retrieved best model from training:")
    print(f"  Run ID: {best_run_id}")
    print(f"  Accuracy: {best_accuracy}")
except Exception as e:
    print(f"Warning: Could not retrieve task values: {e}")
    print("Using latest run from experiment instead")
    # Fallback: get latest run from experiment
    experiment_path = "/Shared/dab-lab/experiments/dev"
    experiment = mlflow.get_experiment_by_name(experiment_path)
    runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id],
                              order_by=["metrics.test_accuracy DESC"],
                              max_results=1)
    best_run_id = runs.iloc[0]["run_id"]
    best_accuracy = runs.iloc[0]["metrics.test_accuracy"]

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Model and Test Data

# COMMAND ----------

# Load the best model
model_uri = f"runs:/{best_run_id}/model"
model = mlflow.sklearn.load_model(model_uri)
print(f"Loaded model from: {model_uri}")

# Load test data
test_table = f"{feature_table}_test"
df_test = spark.table(test_table).toPandas()

feature_cols = [
    "customer_name_length",
    "has_email",
    "has_phone",
    "customer_id_hash",
    "data_quality_score"
]

X_test = df_test[feature_cols]
y_test = df_test["target"]

print(f"Test set size: {len(df_test)} records")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Predictions

# COMMAND ----------

y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)

print(f"Generated predictions for {len(y_pred)} samples")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Calculate Comprehensive Metrics

# COMMAND ----------

# Calculate metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

# Try to calculate AUC (might fail for single-class predictions)
try:
    auc = roc_auc_score(y_test, y_pred_proba[:, 1])
except Exception as e:
    print(f"Could not calculate AUC: {e}")
    auc = None

print(f"\n{'='*50}")
print(f"MODEL EVALUATION METRICS")
print(f"{'='*50}")
print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1 Score:  {f1:.4f}")
if auc:
    print(f"AUC-ROC:   {auc:.4f}")
print(f"{'='*50}\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Confusion Matrix

# COMMAND ----------

cm = confusion_matrix(y_test, y_pred)
print("Confusion Matrix:")
print(cm)
print()

# Calculate confusion matrix percentages
cm_percent = cm.astype('float') / cm.sum(axis=1)[:, None] * 100
print("Confusion Matrix (%):")
print(cm_percent)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Classification Report

# COMMAND ----------

print("Classification Report:")
print(classification_report(y_test, y_pred))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Visualize Performance

# COMMAND ----------

# Create confusion matrix heatmap
fig, ax = plt.subplots(figsize=(8, 6))
import seaborn as sns
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
ax.set_xlabel('Predicted')
ax.set_ylabel('Actual')
ax.set_title('Confusion Matrix')
plt.tight_layout()

# Save plot
plt.savefig('/tmp/confusion_matrix.png')
print("Confusion matrix plot saved")
plt.close()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Feature Importance Analysis

# COMMAND ----------

if hasattr(model, 'feature_importances_'):
    feature_importance_df = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    print("Feature Importance:")
    print(feature_importance_df)

    # Visualize feature importance
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(feature_importance_df['feature'], feature_importance_df['importance'])
    ax.set_xlabel('Importance')
    ax.set_title('Feature Importance')
    plt.tight_layout()
    plt.savefig('/tmp/feature_importance.png')
    print("Feature importance plot saved")
    plt.close()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Model Quality Gate

# COMMAND ----------

# Check if model meets minimum quality threshold
if accuracy >= min_accuracy:
    print(f"✅ Model PASSED quality gate: {accuracy:.4f} >= {min_accuracy}")
    evaluation_status = "PASSED"
else:
    print(f"❌ Model FAILED quality gate: {accuracy:.4f} < {min_accuracy}")
    evaluation_status = "FAILED"
    raise Exception(f"Model accuracy {accuracy:.4f} is below threshold {min_accuracy}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Log Evaluation Results to MLflow

# COMMAND ----------

with mlflow.start_run(run_id=best_run_id):
    # Log additional evaluation metrics
    mlflow.log_metric("eval_accuracy", accuracy)
    mlflow.log_metric("eval_precision", precision)
    mlflow.log_metric("eval_recall", recall)
    mlflow.log_metric("eval_f1_score", f1)
    if auc:
        mlflow.log_metric("eval_auc", auc)

    # Log confusion matrix
    mlflow.log_artifact('/tmp/confusion_matrix.png')
    if hasattr(model, 'feature_importances_'):
        mlflow.log_artifact('/tmp/feature_importance.png')

    # Log evaluation status
    mlflow.set_tag("evaluation_status", evaluation_status)
    mlflow.set_tag("environment", environment)

print("Logged evaluation results to MLflow")

# COMMAND ----------

# Store evaluation results for next task
dbutils.jobs.taskValues.set(key="evaluation_status", value=evaluation_status)
dbutils.jobs.taskValues.set(key="model_run_id", value=best_run_id)
dbutils.jobs.taskValues.set(key="model_accuracy", value=float(accuracy))

# COMMAND ----------

# Return success status
dbutils.notebook.exit(f"Evaluation {evaluation_status}: Accuracy {accuracy:.4f}")
