# Local values for resource naming and configuration
locals {
  # Naming convention: <resource-type>-<project>-<environment>-<region>
  naming_prefix = "${var.project_name}-${var.environment}"

  # Location short codes for naming
  location_short = {
    "northeurope" = "ne"
    "westeurope"  = "we"
    "italynorth"  = "itn"
    "eastus"      = "eus"
    "westus"      = "wus"
  }

  location_code = lookup(local.location_short, var.location, "unk")

  # Resource names following Azure naming conventions
  databricks_workspace_name   = "dbw-${local.naming_prefix}-${local.location_code}"
  managed_resource_group_name = "rg-${local.naming_prefix}-databricks-managed-${local.location_code}"

  # Merge default tags with any additional tags
  common_tags = merge(
    var.tags,
    {
      Location   = var.location
      DeployedAt = timestamp()
      Terraform  = "true"
    }
  )
}
