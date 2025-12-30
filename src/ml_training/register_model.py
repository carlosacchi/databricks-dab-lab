# Databricks notebook source
# MAGIC %md
# MAGIC # ML Training Pipeline - Model Registration
# MAGIC
# MAGIC This notebook registers the validated model to MLflow Model Registry.
# MAGIC Managed by Databricks Asset Bundles (DAB).

# COMMAND ----------

import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
# dbutils is available in Databricks runtime

# COMMAND ----------

# Get parameters
dbutils.widgets.text("model_name", "dab_lab_model")
dbutils.widgets.text("environment", "dev")

model_name = dbutils.widgets.get("model_name")
environment = dbutils.widgets.get("environment")

# Determine stage based on environment
stage = "Production" if environment == "prod" else "Staging"

print(f"Model Registration Configuration:")
print(f"  Model Name: {model_name}")
print(f"  Environment: {environment}")
print(f"  Stage: {stage}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Retrieve Model Information from Previous Task

# COMMAND ----------

# Get evaluation results from previous task
try:
    evaluation_status = dbutils.jobs.taskValues.get(taskKey="evaluate_model",
                                                    key="evaluation_status")
    model_run_id = dbutils.jobs.taskValues.get(taskKey="evaluate_model",
                                                key="model_run_id")
    model_accuracy = dbutils.jobs.taskValues.get(taskKey="evaluate_model",
                                                  key="model_accuracy")

    print(f"Retrieved evaluation results:")
    print(f"  Status: {evaluation_status}")
    print(f"  Run ID: {model_run_id}")
    print(f"  Accuracy: {model_accuracy}")

    # Only proceed if evaluation passed
    if evaluation_status != "PASSED":
        raise Exception(f"Model evaluation failed. Cannot register model.")

except Exception as e:
    print(f"Warning: Could not retrieve evaluation results: {e}")
    print("Attempting to find best model from experiment...")

    # Fallback: get latest successful run
    experiment_path = "/Shared/dab-lab/experiments/dev"
    experiment = mlflow.get_experiment_by_name(experiment_path)
    runs = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string="tags.evaluation_status = 'PASSED'",
        order_by=["metrics.test_accuracy DESC"],
        max_results=1
    )

    if len(runs) == 0:
        raise Exception("No models with PASSED evaluation status found")

    model_run_id = runs.iloc[0]["run_id"]
    model_accuracy = runs.iloc[0]["metrics.test_accuracy"]
    print(f"Found model: Run ID {model_run_id}, Accuracy {model_accuracy}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Register Model to MLflow Model Registry

# COMMAND ----------

# Set MLflow registry to use legacy Workspace Model Registry (not Unity Catalog)
mlflow.set_registry_uri("databricks")

# Create MLflow client
client = MlflowClient()

# Register model
model_uri = f"runs:/{model_run_id}/model"

try:
    # Check if model name already exists in registry
    try:
        client.get_registered_model(model_name)
        print(f"Model '{model_name}' already exists in registry")
        model_exists = True
    except:
        print(f"Creating new registered model: {model_name}")
        model_exists = False

    # Register model version
    model_version = mlflow.register_model(
        model_uri=model_uri,
        name=model_name,
        tags={
            "environment": environment,
            "accuracy": str(model_accuracy),
            "source": "dab_pipeline"
        }
    )

    print(f"Registered model version: {model_version.version}")

except Exception as e:
    print(f"Error registering model: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## Update Model Version Description

# COMMAND ----------

# Add description to model version
description = f"""
Model trained using Databricks Asset Bundles (DAB)

**Metrics:**
- Accuracy: {model_accuracy:.4f}
- Environment: {environment}
- Run ID: {model_run_id}

**Training Details:**
- Feature Engineering: customer profile features
- Algorithm: Random Forest Classifier
- Hyperparameter Tuning: Grid search with cross-validation
"""

client.update_model_version(
    name=model_name,
    version=model_version.version,
    description=description
)

print(f"Updated model version description")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Transition Model to Target Stage

# COMMAND ----------

# Transition model to the specified stage (Staging or Production)
if stage in ["Staging", "Production"]:
    client.transition_model_version_stage(
        name=model_name,
        version=model_version.version,
        stage=stage,
        archive_existing_versions=True  # Archive older versions in this stage
    )
    print(f"Transitioned model version {model_version.version} to {stage}")
else:
    print(f"Stage '{stage}' not valid for transition. Keeping in None stage.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Add Model Alias (MLflow 2.0+ feature)

# COMMAND ----------

# Set alias for easy model reference
try:
    alias = f"{environment}_champion"
    client.set_registered_model_alias(
        name=model_name,
        alias=alias,
        version=model_version.version
    )
    print(f"Set model alias: {alias}")
except Exception as e:
    print(f"Note: Could not set alias (requires MLflow 2.0+): {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Model Registry Summary

# COMMAND ----------

# Get all versions of this model
all_versions = client.search_model_versions(f"name='{model_name}'")

print(f"\n{'='*60}")
print(f"MODEL REGISTRY SUMMARY - {model_name}")
print(f"{'='*60}")
print(f"Total versions: {len(all_versions)}")
print(f"Latest version: {model_version.version}")
print(f"Stage: {stage}")
print(f"Accuracy: {model_accuracy:.4f}")
print(f"Run ID: {model_run_id}")
print(f"{'='*60}\n")

# List all versions
print("All model versions:")
for ver in sorted(all_versions, key=lambda x: int(x.version), reverse=True)[:5]:
    print(f"  Version {ver.version}: {ver.current_stage} "
          f"(created: {ver.creation_timestamp})")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Model Card

# COMMAND ----------

model_card = f"""
# Model Card: {model_name}

## Model Details
- **Version:** {model_version.version}
- **Stage:** {stage}
- **Environment:** {environment}
- **Run ID:** {model_run_id}

## Performance Metrics
- **Accuracy:** {model_accuracy:.4f}

## Training Data
- **Source:** {environment} catalog
- **Features:** customer_name_length, has_email, has_phone, customer_id_hash, data_quality_score

## Intended Use
- **Primary Use:** Customer data quality prediction
- **Out of Scope:** Production predictions without proper validation

## Training Procedure
- **Algorithm:** Random Forest Classifier
- **Framework:** scikit-learn
- **Hyperparameter Tuning:** Grid search

## Evaluation
- **Test Set Performance:** {model_accuracy:.4f} accuracy
- **Quality Gate:** PASSED

## Deployment
- **Registry:** MLflow Model Registry
- **Stage:** {stage}
- **Managed by:** Databricks Asset Bundles
"""

# Save model card
with open('/tmp/model_card.md', 'w') as f:
    f.write(model_card)

print("Generated model card")

# COMMAND ----------

# Store registration info for downstream tasks
dbutils.jobs.taskValues.set(key="model_version", value=int(model_version.version))
dbutils.jobs.taskValues.set(key="model_stage", value=stage)

# COMMAND ----------

# Return success status
dbutils.notebook.exit(f"Model registered: {model_name} v{model_version.version} in {stage}")
