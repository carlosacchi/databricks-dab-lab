# Terraform outputs for use in CI/CD and documentation

output "resource_group_name" {
  description = "Name of the main resource group"
  value       = data.azurerm_resource_group.main.name
}

output "resource_group_id" {
  description = "ID of the main resource group"
  value       = data.azurerm_resource_group.main.id
}

output "databricks_workspace_name" {
  description = "Name of the Databricks workspace"
  value       = azurerm_databricks_workspace.main.name
}

output "databricks_workspace_id" {
  description = "ID of the Databricks workspace"
  value       = azurerm_databricks_workspace.main.id
}

output "databricks_workspace_url" {
  description = "URL of the Databricks workspace"
  value       = "https://${azurerm_databricks_workspace.main.workspace_url}"
}

output "databricks_workspace_resource_id" {
  description = "Azure Resource ID of the Databricks workspace"
  value       = azurerm_databricks_workspace.main.id
  sensitive   = false
}

output "managed_resource_group_name" {
  description = "Name of the managed resource group for Databricks"
  value       = azurerm_databricks_workspace.main.managed_resource_group_name
}

output "managed_resource_group_id" {
  description = "ID of the managed resource group for Databricks"
  value       = azurerm_databricks_workspace.main.managed_resource_group_id
}

output "databricks_cluster_id" {
  description = "ID of the shared Databricks cluster"
  value       = databricks_cluster.shared_cluster.id
}

output "databricks_cluster_name" {
  description = "Name of the shared Databricks cluster"
  value       = databricks_cluster.shared_cluster.cluster_name
}

output "secret_scope_name" {
  description = "Name of the Databricks secret scope"
  value       = databricks_secret_scope.dab_lab.name
}

output "dab_deployment_path" {
  description = "Root path for DAB deployments in workspace"
  value       = databricks_directory.dab_root.path
}

# Environment variables for DAB deployment
output "databricks_host" {
  description = "Databricks host for DAB CLI (without https://)"
  value       = azurerm_databricks_workspace.main.workspace_url
  sensitive   = false
}
