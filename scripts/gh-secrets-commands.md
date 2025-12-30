# GitHub CLI Commands for Setting Secrets

This document contains the GitHub CLI commands to set all required secrets for the Databricks DAB Lab project.

## Prerequisites

1. Install GitHub CLI: https://cli.github.com/
2. Authenticate: `gh auth login`
3. Have your Azure Service Principal credentials ready

## Option 1: Interactive Script (Recommended)

Use the interactive setup script:

```bash
./scripts/setup-github-secrets.sh
```

## Option 2: Manual Commands

### Azure Authentication Secrets

Replace the placeholder values with your actual Azure Service Principal credentials:

```bash
# Azure Subscription ID
gh secret set AZURE_SUBSCRIPTION_ID \
  --repo yourghusername/databricks-dab-lab \
  --body "YOUR_AZURE_SUBSCRIPTION_ID"

# Azure Client ID (Service Principal Application ID)
gh secret set AZURE_CLIENT_ID \
  --repo yourghusername/databricks-dab-lab \
  --body "YOUR_AZURE_CLIENT_ID"

# Azure Client Secret (Service Principal Secret)
gh secret set AZURE_CLIENT_SECRET \
  --repo yourghusername/databricks-dab-lab \
  --body "YOUR_AZURE_CLIENT_SECRET"

# Azure Tenant ID
gh secret set AZURE_TENANT_ID \
  --repo yourghusername/databricks-dab-lab \
  --body "YOUR_AZURE_TENANT_ID"
```

### Terraform State Backend Secrets

```bash
# Terraform State Resource Group
gh secret set TF_STATE_RESOURCE_GROUP \
  --repo yourghusername/databricks-dab-lab \
  --body "rg-terraform-state"

# Terraform State Storage Account (use your unique name)
gh secret set TF_STATE_STORAGE_ACCOUNT \
  --repo yourghusername/databricks-dab-lab \
  --body "sttfstateYOURNAME123"

# Terraform State Container Name
gh secret set TF_STATE_CONTAINER_NAME \
  --repo yourghusername/databricks-dab-lab \
  --body "tfstate"
```

### Databricks Workspace Secrets

**⚠️ Set these AFTER Terraform deploys the Databricks workspace**

```bash
# Databricks Host (without https://)
# Example: adb-123456789.12.azuredatabricks.net
gh secret set DATABRICKS_HOST \
  --repo yourghusername/databricks-dab-lab \
  --body "adb-XXXXXXXXX.XX.azuredatabricks.net"

# Databricks Personal Access Token
# Generate from: Databricks UI → User Settings → Access tokens
gh secret set DATABRICKS_TOKEN \
  --repo yourghusername/databricks-dab-lab \
  --body "dapiXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

## Option 3: Set Secrets from Environment Variables

If you have your secrets already in environment variables:

```bash
# Set all secrets from environment variables
gh secret set AZURE_SUBSCRIPTION_ID --repo yourghusername/databricks-dab-lab --body "$AZURE_SUBSCRIPTION_ID"
gh secret set AZURE_CLIENT_ID --repo yourghusername/databricks-dab-lab --body "$AZURE_CLIENT_ID"
gh secret set AZURE_CLIENT_SECRET --repo yourghusername/databricks-dab-lab --body "$AZURE_CLIENT_SECRET"
gh secret set AZURE_TENANT_ID --repo yourghusername/databricks-dab-lab --body "$AZURE_TENANT_ID"
gh secret set TF_STATE_RESOURCE_GROUP --repo yourghusername/databricks-dab-lab --body "$TF_STATE_RESOURCE_GROUP"
gh secret set TF_STATE_STORAGE_ACCOUNT --repo yourghusername/databricks-dab-lab --body "$TF_STATE_STORAGE_ACCOUNT"
gh secret set TF_STATE_CONTAINER_NAME --repo yourghusername/databricks-dab-lab --body "tfstate"
```

## Option 4: Pipe Secrets from Files

If you have secrets stored in files (ensure files are not in git!):

```bash
# From files
gh secret set AZURE_CLIENT_SECRET --repo yourghusername/databricks-dab-lab < /path/to/secret.txt

# From command output
az account show --query id -o tsv | gh secret set AZURE_SUBSCRIPTION_ID --repo yourghusername/databricks-dab-lab
```

## Verify Secrets

List all secrets to verify they were set correctly:

```bash
gh secret list --repo yourghusername/databricks-dab-lab
```

Expected output:
```
AZURE_CLIENT_ID           Updated 2024-XX-XX
AZURE_CLIENT_SECRET       Updated 2024-XX-XX
AZURE_SUBSCRIPTION_ID     Updated 2024-XX-XX
AZURE_TENANT_ID           Updated 2024-XX-XX
DATABRICKS_HOST           Updated 2024-XX-XX
DATABRICKS_TOKEN          Updated 2024-XX-XX
TF_STATE_CONTAINER_NAME   Updated 2024-XX-XX
TF_STATE_RESOURCE_GROUP   Updated 2024-XX-XX
TF_STATE_STORAGE_ACCOUNT  Updated 2024-XX-XX
```

## Update a Secret

To update an existing secret:

```bash
gh secret set SECRET_NAME --repo yourghusername/databricks-dab-lab --body "NEW_VALUE"
```

## Delete a Secret

To delete a secret:

```bash
gh secret delete SECRET_NAME --repo yourghusername/databricks-dab-lab
```

## Security Best Practices

1. **Never commit secrets to git**
   - Use `.gitignore` to exclude secret files
   - Review commits before pushing

2. **Use secure input methods**
   - Use interactive prompts (hides input)
   - Or pipe from secure password managers
   - Never type secrets in plain view

3. **Rotate secrets regularly**
   ```bash
   # Rotate Azure SP secret
   az ad sp credential reset --id $AZURE_CLIENT_ID
   # Then update GitHub secret with new value
   ```

4. **Audit secret usage**
   ```bash
   # Check when secrets were last updated
   gh secret list --repo yourghusername/databricks-dab-lab
   ```

## Troubleshooting

### Error: "not found" or "404"

Make sure you're authenticated and have access to the repository:
```bash
gh auth status
gh auth refresh
```

### Error: "secret not found"

The secret doesn't exist yet. Use `set` instead of `update`:
```bash
gh secret set SECRET_NAME --repo yourghusername/databricks-dab-lab
```

### Error: "permission denied"

You need admin or write access to the repository to manage secrets.

## Alternative: Using GitHub Web UI

If you prefer using the web interface:

1. Go to: https://github.com/yourghusername/databricks-dab-lab/settings/secrets/actions
2. Click "New repository secret"
3. Enter secret name and value
4. Click "Add secret"

## Getting Azure Service Principal Credentials

If you need to create a Service Principal:

```bash
# Create Service Principal and output in JSON
az ad sp create-for-rbac \
  --name "sp-databricks-dab-lab" \
  --role "Contributor" \
  --scopes "/subscriptions/$(az account show --query id -o tsv)" \
  --sdk-auth

# Extract specific values
az ad sp create-for-rbac \
  --name "sp-databricks-dab-lab" \
  --role "Contributor" \
  --scopes "/subscriptions/$(az account show --query id -o tsv)" \
  --query "{clientId:appId, clientSecret:password, tenantId:tenant}"
```

## Complete Setup Script

Here's a complete script to set all secrets at once:

```bash
#!/bin/bash
# save as: setup-all-secrets.sh

# Prompt for values
read -p "Azure Subscription ID: " AZURE_SUB_ID
read -p "Azure Client ID: " AZURE_CLI_ID
read -sp "Azure Client Secret: " AZURE_CLI_SEC
echo ""
read -p "Azure Tenant ID: " AZURE_TEN_ID
read -p "TF State Resource Group: " TF_RG
read -p "TF State Storage Account: " TF_SA

# Set all secrets
gh secret set AZURE_SUBSCRIPTION_ID --repo yourghusername/databricks-dab-lab --body "$AZURE_SUB_ID"
gh secret set AZURE_CLIENT_ID --repo yourghusername/databricks-dab-lab --body "$AZURE_CLI_ID"
gh secret set AZURE_CLIENT_SECRET --repo yourghusername/databricks-dab-lab --body "$AZURE_CLI_SEC"
gh secret set AZURE_TENANT_ID --repo yourghusername/databricks-dab-lab --body "$AZURE_TEN_ID"
gh secret set TF_STATE_RESOURCE_GROUP --repo yourghusername/databricks-dab-lab --body "$TF_RG"
gh secret set TF_STATE_STORAGE_ACCOUNT --repo yourghusername/databricks-dab-lab --body "$TF_SA"
gh secret set TF_STATE_CONTAINER_NAME --repo yourghusername/databricks-dab-lab --body "tfstate"

echo "✅ All secrets set successfully!"
gh secret list --repo yourghusername/databricks-dab-lab
```

---

**Remember**: Keep your secrets secure and never commit them to version control!
