# Data sources for Databricks configuration

# Get the latest LTS (Long Term Support) Spark version
data "databricks_spark_version" "latest_lts" {
  long_term_support = true
  depends_on        = [azurerm_databricks_workspace.main]
}

# Get the smallest available node type for cost optimization
data "databricks_node_type" "smallest" {
  local_disk = true
  depends_on = [azurerm_databricks_workspace.main]
}

# Get current Databricks workspace information
data "azurerm_databricks_workspace" "main" {
  name                = azurerm_databricks_workspace.main.name
  resource_group_name = data.azurerm_resource_group.main.name
  depends_on          = [azurerm_databricks_workspace.main]
}
