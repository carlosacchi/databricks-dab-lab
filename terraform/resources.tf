# Use existing Resource Group (not creating new one)
# The Service Principal has Contributor role on this RG
data "azurerm_resource_group" "main" {
  name = var.resource_group_name
}

# Databricks Workspace
resource "azurerm_databricks_workspace" "main" {
  name                = local.databricks_workspace_name
  resource_group_name = data.azurerm_resource_group.main.name
  location            = data.azurerm_resource_group.main.location
  sku                 = var.databricks_sku

  # Managed Resource Group for Databricks-managed resources
  managed_resource_group_name = local.managed_resource_group_name

  # Security features
  # Note: network_security_group_rules_required is only for VNet-injected workspaces
  public_network_access_enabled = true # Can be set to false for private deployment

  tags = merge(
    local.common_tags,
    {
      ResourceType = "Databricks-Workspace"
    }
  )
}

# Databricks Secret Scope for secure credential management
resource "databricks_secret_scope" "dab_lab" {
  name = "dab-lab-secrets"

  # Backend type: DATABRICKS (encrypted in Databricks control plane)
  # Alternative: AZURE_KEYVAULT for Azure Key Vault backed secrets
}

# Example secret for demonstration (in production, use Azure Key Vault)
resource "databricks_secret" "example" {
  key          = "example-key"
  string_value = "example-secret-value"
  scope        = databricks_secret_scope.dab_lab.name
}

# Databricks Cluster for DAB jobs
resource "databricks_cluster" "shared_cluster" {
  cluster_name            = "shared-dab-cluster"
  spark_version           = data.databricks_spark_version.latest_lts.id
  node_type_id            = data.databricks_node_type.smallest.id
  autotermination_minutes = 20
  num_workers             = 1

  # Cluster configuration
  spark_conf = {
    "spark.databricks.delta.preview.enabled" = "true"
  }

  # Libraries can be added here or managed via DAB
  # library {
  #   pypi {
  #     package = "pandas"
  #   }
  # }

  custom_tags = merge(
    local.common_tags,
    {
      ResourceType = "Databricks-Cluster"
      ClusterUsage = "DAB-Shared"
    }
  )
}

# Create directories for DAB deployments
resource "databricks_directory" "dab_root" {
  path = "/Workspace/dab-deployments"
}

resource "databricks_directory" "etl_pipeline" {
  path = "${databricks_directory.dab_root.path}/etl-pipeline"
}

resource "databricks_directory" "ml_training" {
  path = "${databricks_directory.dab_root.path}/ml-training"
}

# MLflow experiments directory
# Note: This directory will be populated by MLflow during job runs
# IMPORTANT: Before running 'terraform destroy', manually delete this directory
# and its contents from Databricks UI to avoid "directory not empty" errors
resource "databricks_directory" "mlflow_experiments" {
  path = "/Shared/dab-lab/experiments"
}
