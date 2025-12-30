# Azure Authentication Variables
variable "azure_subscription_id" {
  description = "Azure Subscription ID"
  type        = string
  sensitive   = true
}

variable "azure_client_id" {
  description = "Azure Service Principal Client ID (Application ID)"
  type        = string
  sensitive   = true
}

variable "azure_client_secret" {
  description = "Azure Service Principal Client Secret"
  type        = string
  sensitive   = true
}

variable "azure_tenant_id" {
  description = "Azure Tenant ID"
  type        = string
  sensitive   = true
}

# Terraform State Backend Variables
variable "tf_state_resource_group" {
  description = "Resource Group name for Terraform state storage"
  type        = string
}

variable "tf_state_storage_account" {
  description = "Storage Account name for Terraform state"
  type        = string
}

variable "tf_state_container_name" {
  description = "Container name for Terraform state"
  type        = string
  default     = "tfstate"
}

# Project Configuration Variables
variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "databricks-dab-lab"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Azure region for resource deployment"
  type        = string
  default     = "northeurope"
}

variable "resource_group_name" {
  description = "Name of the existing resource group (must already exist)"
  type        = string
  default     = "rg-databricks-dab"
}

# Databricks Configuration Variables
variable "databricks_sku" {
  description = "Databricks workspace SKU (standard, premium, trial)"
  type        = string
  default     = "trial"

  validation {
    condition     = contains(["standard", "premium", "trial"], var.databricks_sku)
    error_message = "The databricks_sku must be either 'standard', 'premium', or 'trial'."
  }
}

# Tagging Variables
variable "tags" {
  description = "Centralized tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "Databricks-DAB-Lab"
    Environment = "Development"
    ManagedBy   = "Terraform"
    Owner       = "DataEngineering"
    CostCenter  = "Engineering"
    Purpose     = "DAB-Tutorial"
  }
}
