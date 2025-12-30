terraform {
  required_version = "~> 1.14"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.85"
    }
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.35"
    }
  }

  # Azure Storage backend for remote state management
  # Backend configuration will be provided during init via -backend-config flags
  backend "azurerm" {
    key = "databricks-dab-lab.tfstate"
  }
}

# Configure Azure Provider
provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }

  subscription_id = var.azure_subscription_id
  client_id       = var.azure_client_id
  client_secret   = var.azure_client_secret
  tenant_id       = var.azure_tenant_id
}

# Configure Databricks Provider
provider "databricks" {
  host                        = azurerm_databricks_workspace.main.workspace_url
  azure_workspace_resource_id = azurerm_databricks_workspace.main.id
  azure_client_id             = var.azure_client_id
  azure_client_secret         = var.azure_client_secret
  azure_tenant_id             = var.azure_tenant_id
}
