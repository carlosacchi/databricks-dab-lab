#!/bin/bash

# GitHub Secrets Setup Script
# This script helps you configure all required GitHub secrets for the Databricks DAB Lab project
# using the GitHub CLI (gh)

set -e  # Exit on error

echo "=========================================="
echo "GitHub Secrets Setup for Databricks DAB Lab"
echo "=========================================="
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is not installed"
    echo "Install it from: https://cli.github.com/"
    echo "Or run: brew install gh (on macOS)"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Error: Not authenticated with GitHub CLI"
    echo "Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is installed and authenticated"
echo ""

# Get repository name
REPO="yourghusername/databricks-dab-lab"
echo "Repository: $REPO"
echo ""

# Function to set secret
set_secret() {
    local secret_name=$1
    local secret_description=$2
    local secret_value

    echo "---"
    echo "Setting: $secret_name"
    echo "Description: $secret_description"
    echo ""

    # Prompt for secret value (hidden input)
    read -sp "Enter value for $secret_name: " secret_value
    echo ""

    if [ -z "$secret_value" ]; then
        echo "⚠️  Skipping empty value for $secret_name"
        return
    fi

    # Set the secret using gh CLI
    echo "$secret_value" | gh secret set "$secret_name" --repo "$REPO"

    if [ $? -eq 0 ]; then
        echo "✅ Successfully set $secret_name"
    else
        echo "❌ Failed to set $secret_name"
    fi
    echo ""
}

# Prompt to continue
echo "This script will help you set up all required GitHub secrets."
echo "You will be prompted for each secret value."
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "=========================================="
echo "Azure Authentication Secrets"
echo "=========================================="
echo ""
echo "Get these values from your Azure Service Principal creation output."
echo "If you haven't created it yet, run:"
echo "  az ad sp create-for-rbac --name sp-databricks-dab-lab --role Contributor --scopes /subscriptions/<subscription-id> --sdk-auth"
echo ""

set_secret "AZURE_SUBSCRIPTION_ID" "Azure Subscription ID"
set_secret "AZURE_CLIENT_ID" "Azure Service Principal Client ID (Application ID)"
set_secret "AZURE_CLIENT_SECRET" "Azure Service Principal Client Secret"
set_secret "AZURE_TENANT_ID" "Azure Tenant ID"

echo ""
echo "=========================================="
echo "Terraform State Backend Secrets"
echo "=========================================="
echo ""
echo "Get these values from your Terraform state storage setup."
echo ""

set_secret "TF_STATE_RESOURCE_GROUP" "Resource Group name for Terraform state (value: rg-databricks-dab)"
set_secret "TF_STATE_STORAGE_ACCOUNT" "Storage Account name for Terraform state (value: yourbackendstorage)"
set_secret "TF_STATE_CONTAINER_NAME" "Container name for Terraform state (value: tfdab)"

echo ""
echo "=========================================="
echo "Databricks Workspace Secrets"
echo "=========================================="
echo ""
echo "⚠️  IMPORTANT: These secrets should be set AFTER deploying Databricks workspace with Terraform"
echo "Skip these for now if you haven't deployed the workspace yet."
echo ""
read -p "Have you deployed the Databricks workspace? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Get DATABRICKS_HOST from Terraform outputs or Azure Portal"
    echo "Example: adb-123456789.12.azuredatabricks.net (without https://)"
    echo ""
    set_secret "DATABRICKS_HOST" "Databricks workspace URL (without https://)"

    echo ""
    echo "Generate DATABRICKS_TOKEN from Databricks UI:"
    echo "  1. Login to your Databricks workspace"
    echo "  2. User Settings → Access tokens → Generate new token"
    echo ""
    set_secret "DATABRICKS_TOKEN" "Databricks Personal Access Token"
else
    echo "⚠️  Skipping Databricks secrets. Set them later using:"
    echo "    gh secret set DATABRICKS_HOST --repo $REPO"
    echo "    gh secret set DATABRICKS_TOKEN --repo $REPO"
fi

echo ""
echo "=========================================="
echo "✅ GitHub Secrets Setup Complete!"
echo "=========================================="
echo ""
echo "To verify your secrets, run:"
echo "  gh secret list --repo $REPO"
echo ""
echo "To update a secret later, run:"
echo "  gh secret set SECRET_NAME --repo $REPO"
echo ""
echo "Next steps:"
echo "  1. Review secrets: gh secret list --repo $REPO"
echo "  2. Deploy infrastructure: Run 'Terraform Azure Databricks Deployment' workflow"
echo "  3. After deployment, add DATABRICKS_HOST and DATABRICKS_TOKEN secrets"
echo "  4. Deploy DAB jobs: Run 'Databricks Asset Bundle Deployment' workflow"
echo ""
