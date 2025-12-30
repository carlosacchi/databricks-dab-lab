# Databricks Asset Bundles (DAB) - Complete Lab & Tutorial

[![Terraform](https://img.shields.io/badge/Terraform-1.14-623CE4?logo=terraform)](https://www.terraform.io/)
[![Databricks](https://img.shields.io/badge/Databricks-Azure-FF3621?logo=databricks)](https://databricks.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A comprehensive, production-ready repository demonstrating **Databricks Asset Bundles (DAB)** with complete infrastructure-as-code deployment on Azure using Terraform and GitHub Actions.

## 📋 Table of Contents

- [Overview](#overview)
- [What are Databricks Asset Bundles?](#what-are-databricks-asset-bundles)
- [Why Use DAB?](#why-use-dab)
- [Repository Structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Deployment Guide](#deployment-guide)
- [DAB Examples](#dab-examples)
- [Old Way vs DAB Way](#old-way-vs-dab-way)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🎯 Overview

This repository provides a complete, end-to-end implementation of Databricks Asset Bundles (DAB) including:

- ✅ **Complete Azure Infrastructure** - Terraform code to deploy Databricks workspace on Azure
- ✅ **Two Production-Ready DAB Examples** - ETL Pipeline and ML Training workflows
- ✅ **Automated CI/CD** - GitHub Actions for both infrastructure and DAB deployments
- ✅ **Multi-Environment Support** - Dev and Prod configurations with environment parity
- ✅ **Security Best Practices** - Azure Service Principal authentication, secrets management
- ✅ **Comprehensive Documentation** - Setup guides, architecture diagrams, and tutorials

## 🚀 What are Databricks Asset Bundles?

**Databricks Asset Bundles (DAB)** is a deployment framework that enables Infrastructure-as-Code (IaC) for Databricks jobs, workflows, Delta Live Tables, and other workspace resources.

### Key Features

| Feature | Description |
|---------|-------------|
| **Version Control** | All job configurations, notebooks, and code in Git |
| **Environment Management** | Deploy to dev, staging, prod with guaranteed parity |
| **CI/CD Integration** | Native GitHub Actions, GitLab CI, Azure DevOps support |
| **Validation** | Built-in validation before deployment |
| **State Management** | Automatic tracking of deployed resources |
| **Rollback** | Easy rollback via Git revert |

## 💡 Why Use DAB?

### Problems DAB Solves

#### ❌ **Before DAB (Manual Approach)**
```
1. Create jobs manually in Databricks UI
2. Copy-paste configurations between environments
3. No version control of job configurations
4. Manual parameter updates across multiple jobs
5. Configuration drift between dev and prod
6. No automated testing or validation
7. Difficult team collaboration
8. No rollback capability
```

#### ✅ **With DAB**
```yaml
# One configuration file
resources:
  jobs:
    etl_pipeline:
      name: "ETL Pipeline - ${bundle.target}"
      tasks:
        - task_key: extract
          notebook_task:
            notebook_path: ../src/etl/extract.py

# Deploy anywhere with one command
$ databricks bundle deploy -t dev   # Deploy to dev
$ databricks bundle deploy -t prod  # Deploy to prod
```

**Benefits:**
- ✅ Version controlled in Git
- ✅ Environment parity guaranteed
- ✅ Code review process for job changes
- ✅ Automated testing and validation
- ✅ Easy rollback (git revert + redeploy)
- ✅ Team collaboration built-in

See [Old Way vs DAB Way](notebooks/old_approach/manual_job_setup.md) for detailed comparison.

## 📁 Repository Structure

```
databricks-dab-lab/
├── .github/
│   └── workflows/
│       ├── terraform-deploy.yml      # Infrastructure deployment pipeline
│       └── dab-deploy.yml            # DAB deployment pipeline
├── terraform/                         # Azure infrastructure as code
│   ├── main.tf                       # Provider configuration
│   ├── variables.tf                  # Input variables
│   ├── resources.tf                  # Databricks workspace & resources
│   ├── data.tf                       # Data sources
│   ├── outputs.tf                    # Output values
│   ├── locals.tf                     # Local values & naming conventions
│   └── terraform.tfvars.example      # Example variables file
├── src/                              # Source code for DAB jobs
│   ├── setup/                        # Setup scripts
│   │   └── create_sample_data.py     # Sample data generation
│   ├── etl_pipeline/                 # ETL job notebooks
│   │   ├── extract.py                # Data extraction
│   │   ├── transform.py              # Data transformation
│   │   ├── load.py                   # Data loading
│   │   └── validate.py               # Data quality validation
│   └── ml_training/                  # ML training notebooks
│       ├── prepare_data.py           # Feature engineering
│       ├── train_model.py            # Model training
│       ├── evaluate_model.py         # Model evaluation
│       └── register_model.py         # Model registration
├── resources/                        # DAB job configurations
│   ├── setup_job.yml                 # Setup job definition
│   ├── etl_pipeline_job.yml         # ETL job definition
│   └── ml_training_job.yml          # ML training job definition
├── notebooks/
│   └── old_approach/                 # Documentation of old methods
│       └── manual_job_setup.md       # Old way vs DAB comparison
├── scripts/                          # Utility scripts
│   ├── setup-github-secrets.sh       # Interactive secrets setup
│   └── gh-secrets-commands.md        # GitHub CLI commands reference
├── databricks.yml                    # Main DAB configuration file
├── README.md                         # This file
└── .gitignore                        # Git ignore rules
```

## 📋 Prerequisites

### Required Tools

- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) (v2.40+)
- [Terraform](https://www.terraform.io/downloads) (v1.14)
- [Databricks CLI](https://docs.databricks.com/dev-tools/cli/index.html) (v0.213.0+)
- [Git](https://git-scm.com/downloads)
- [GitHub CLI](https://cli.github.com/) (optional, for secrets setup)
- [GitHub Account](https://github.com) with Actions enabled

### Azure Requirements

You need an **existing Azure infrastructure** with:
- **Resource Group**: Already created (e.g., `rg-databricks-dab`)
- **Storage Account**: For Terraform state (e.g., `yourbackendstorage`)
- **Container**: In the storage account (e.g., `tfdab`)
- **Service Principal** with:
  - `Contributor` role on the Resource Group
  - `Storage Blob Data Contributor` on the Storage Account

> **Note**: This project uses existing infrastructure. The Service Principal has limited permissions (Resource Group level only, not subscription-wide) following security best practices.

### Knowledge Requirements

- Basic understanding of Git and GitHub
- Familiarity with Azure portal
- Basic knowledge of Databricks concepts
- Understanding of YAML syntax

## 🚀 Quick Start

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourghusername/databricks-dab-lab.git
cd databricks-dab-lab
```

### Step 2: Configure GitHub Secrets

You need to configure the following secrets in your GitHub repository:

**Required Secrets for Terraform Deployment:**
- `AZURE_SUBSCRIPTION_ID` - Your Azure subscription ID
- `AZURE_CLIENT_ID` - Service Principal application ID
- `AZURE_CLIENT_SECRET` - Service Principal password
- `AZURE_TENANT_ID` - Your Azure AD tenant ID
- `TF_STATE_RESOURCE_GROUP` - Resource group for Terraform state
- `TF_STATE_STORAGE_ACCOUNT` - Storage account for Terraform state
- `TF_STATE_CONTAINER_NAME` - Container for Terraform state files

**Required Secrets for DAB Deployment:**
- `DATABRICKS_HOST` - Databricks workspace URL (set after Terraform deployment)
- `DATABRICKS_TOKEN` - Databricks personal access token (set after Terraform deployment)
- `DATABRICKS_CLUSTER_ID` - Cluster ID (set after Terraform deployment)

#### Setup Methods

**Option A: Interactive Script (Easiest)**
```bash
./scripts/setup-github-secrets.sh
```

**Option B: GitHub CLI Manual Commands**
```bash
# See scripts/gh-secrets-commands.md for individual commands
gh secret set AZURE_SUBSCRIPTION_ID --body="<your-subscription-id>"
gh secret set AZURE_CLIENT_ID --body="<your-client-id>"
# ... etc
```

**Option C: GitHub Web UI**
1. Go to your repository on GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret" for each secret

### Step 3: Deploy Infrastructure via GitHub Actions

1. Go to your repository's **Actions** tab
2. Select **Terraform Azure Databricks Deployment** workflow
3. Click **Run workflow**
4. Select:
   - **Action**: `apply`
   - **Auto-approve**: `false` (recommended for first run)
5. Click **Run workflow**

The workflow will:
- Initialize Terraform with remote state
- Validate configuration
- Create execution plan
- Deploy Databricks workspace and cluster
- Create directories and secret scopes
- Output workspace URL and cluster ID

### Step 4: Update DAB Deployment Secrets

After Terraform deployment completes, you need to set three additional secrets:

**4.1 Get Databricks Host URL**

Check the Terraform workflow output or run:
```bash
cd terraform
terraform output databricks_host
# Example: adb-1234567890123456.7.azuredatabricks.net
```

**4.2 Get Cluster ID**

From Terraform output:
```bash
terraform output databricks_cluster_id
# Example: 1229-221552-7wmjd6ef
```

**4.3 Generate Databricks Token**

1. Open the Databricks workspace URL from step 4.1
2. Click your username (top right) → **User Settings**
3. Go to **Access Tokens** tab
4. Click **Generate New Token**
5. Enter a comment (e.g., "GitHub Actions DAB") and lifetime (e.g., 90 days)
6. Click **Generate**
7. **Copy the token immediately** (it won't be shown again)

**4.4 Set the Secrets**

```bash
gh secret set DATABRICKS_HOST --body="<workspace-url>"
gh secret set DATABRICKS_CLUSTER_ID --body="<cluster-id>"
gh secret set DATABRICKS_TOKEN --body="<token-value>"
```

### Step 5: Deploy DAB Jobs

1. Go to **Actions** tab
2. Select **DAB Deployment** workflow
3. Click **Run workflow**
4. Select:
   - **Action**: `deploy`
   - **Environment**: `dev`
5. Click **Run workflow**

This deploys three jobs to your Databricks workspace:
- **Setup Job**: Creates sample data
- **ETL Pipeline**: Data processing workflow
- **ML Training Pipeline**: Machine learning workflow

### Step 6: Create Sample Data

Before running the main jobs, create sample data:

**Option A: Via Databricks CLI**
```bash
databricks bundle run setup_sample_data -t dev
```

**Option B: Via Databricks UI**
1. Open your Databricks workspace
2. Go to **Workflows** in the left sidebar
3. Find "DAB Setup - Create Sample Data - dev"
4. Click **Run now**

This creates:
- Schema: `hive_metastore.dab_lab`
- Table: `raw_customer_data` (1000 sample records)

### Step 7: Run the Pipelines

**Run ETL Pipeline:**
```bash
databricks bundle run etl_pipeline -t dev
```

Or via Databricks UI: Workflows → "DAB ETL Pipeline - dev" → Run now

The pipeline will:
1. Extract data from `raw_customer_data`
2. Transform and clean the data
3. Load to `transformed_data` and `final_data` tables
4. Validate data quality

**Run ML Training Pipeline:**
```bash
databricks bundle run ml_training -t dev
```

Or via Databricks UI: Workflows → "DAB ML Training Pipeline - dev" → Run now

The pipeline will:
1. Prepare features from `final_data`
2. Train a classification model
3. Evaluate model performance
4. Register model to MLflow Model Registry

## 📊 DAB Examples

### Example 1: ETL Pipeline

A complete ETL workflow demonstrating:
- **Extract**: Read from Delta tables
- **Transform**: Data cleaning, enrichment, and quality checks
- **Load**: Write to Delta tables with schema evolution
- **Validate**: Data quality checks and metrics

**Configuration**: [resources/etl_pipeline_job.yml](resources/etl_pipeline_job.yml)

**Task Flow**:
```
extract → transform → load → validate
```

**Key Features**:
- Parameterized inputs/outputs
- Data quality validation
- Error handling and logging
- Schema evolution support

### Example 2: ML Training Pipeline

A complete MLOps workflow demonstrating:
- **Prepare**: Feature engineering and train/test split
- **Train**: Model training with hyperparameter tuning
- **Evaluate**: Model performance evaluation
- **Register**: MLflow Model Registry integration

**Configuration**: [resources/ml_training_job.yml](resources/ml_training_job.yml)

**Task Flow**:
```
prepare_training_data → train_model → evaluate_model → register_model
```

**Key Features**:
- MLflow experiment tracking
- Hyperparameter tuning
- Model evaluation metrics
- Automated model registration
- Environment-based deployment (Staging/Production)

## 🔄 Old Way vs DAB Way

### Manual Job Creation (Old Way)

```python
# 1. Create notebook in Databricks UI
# 2. Manually configure job via UI:
#    - Job name
#    - Cluster settings
#    - Schedule
#    - Parameters
#    - Notifications
# 3. Test in dev environment
# 4. Repeat ALL steps manually in prod
# 5. No version control of job configuration
# 6. Hope you didn't miss any settings
```

**Problems**:
- ❌ Configuration drift between environments
- ❌ No version control for job definitions
- ❌ Manual errors during replication
- ❌ Difficult to review changes
- ❌ No rollback capability
- ❌ Time-consuming for multiple jobs

### Databricks Asset Bundles (New Way)

```yaml
# resources/etl_pipeline_job.yml
resources:
  jobs:
    etl_pipeline:
      name: "ETL Pipeline - ${bundle.target}"
      tasks:
        - task_key: extract
          notebook_task:
            notebook_path: ../src/etl_pipeline/extract.py
            base_parameters:
              source_table: ${var.catalog}.${var.schema}.raw_data
          existing_cluster_id: ${var.cluster_id}
```

```bash
# Deploy to any environment
databricks bundle deploy -t dev
databricks bundle deploy -t prod

# Run the job
databricks bundle run etl_pipeline -t dev
```

**Benefits**:
- ✅ Single source of truth in Git
- ✅ Guaranteed environment parity
- ✅ Code review process
- ✅ Automated validation
- ✅ One command deployment
- ✅ Easy rollback (git revert)

See [notebooks/old_approach/manual_job_setup.md](notebooks/old_approach/manual_job_setup.md) for detailed comparison.

## 🏗️ Architecture

### Infrastructure Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         GitHub                              │
│  ┌──────────────────┐           ┌──────────────────┐       │
│  │ Terraform Code   │           │   DAB Config     │       │
│  │  (terraform/)    │           │ (databricks.yml) │       │
│  └────────┬─────────┘           └────────┬─────────┘       │
│           │                              │                  │
│  ┌────────▼──────────────────────────────▼─────────┐       │
│  │         GitHub Actions Workflows                │       │
│  │  ├─ terraform-deploy.yml                        │       │
│  │  └─ dab-deploy.yml                              │       │
│  └───────────────────┬──────────────────────────────┘       │
└────────────────────────┼────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                                 │
        ▼                                 ▼
┌───────────────────┐           ┌──────────────────────┐
│   Terraform       │           │    Databricks        │
│   Remote State    │           │    Workspace         │
│ (Azure Storage)   │           │                      │
└───────────────────┘           │  ┌────────────────┐  │
                                │  │   Cluster      │  │
                                │  ├────────────────┤  │
                                │  │   Jobs         │  │
                                │  │ • Setup        │  │
                                │  │ • ETL Pipeline │  │
                                │  │ • ML Training  │  │
                                │  ├────────────────┤  │
                                │  │  Delta Tables  │  │
                                │  ├────────────────┤  │
                                │  │  MLflow        │  │
                                │  │  Experiments   │  │
                                │  └────────────────┘  │
                                └──────────────────────┘
```

### DAB Deployment Flow

```
┌─────────────────────────────────────────────────────────┐
│ Step 1: Code Changes                                    │
│ ─────────────────────────────────────────────────────── │
│ Developer commits changes to:                           │
│ • Job configurations (resources/*.yml)                  │
│ • Notebook code (src/**/*.py)                           │
│ • DAB config (databricks.yml)                           │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ Step 2: GitHub Actions Trigger                          │
│ ─────────────────────────────────────────────────────── │
│ Workflow: dab-deploy.yml                                │
│ • Checkout code                                         │
│ • Setup Databricks CLI                                  │
│ • Authenticate (DATABRICKS_HOST + TOKEN)                │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ Step 3: DAB Validation                                  │
│ ─────────────────────────────────────────────────────── │
│ databricks bundle validate -t <env>                     │
│ • Check YAML syntax                                     │
│ • Validate variable references                          │
│ • Verify notebook paths                                 │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ Step 4: DAB Deployment                                  │
│ ─────────────────────────────────────────────────────── │
│ databricks bundle deploy -t <env>                       │
│ • Upload notebooks to workspace                         │
│ • Create/update job definitions                         │
│ • Update job parameters                                 │
│ • Track deployment state                                │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ Step 5: Jobs Ready to Run                               │
│ ─────────────────────────────────────────────────────── │
│ Jobs are deployed and ready in Databricks workspace:    │
│ • Manual trigger via UI                                 │
│ • Scheduled execution                                   │
│ • API/CLI trigger: databricks bundle run <job> -t <env> │
└─────────────────────────────────────────────────────────┘
```

### Multi-Environment Strategy

```yaml
# databricks.yml
targets:
  dev:
    mode: development
    # Uses hive_metastore.dab_lab
    # Models registered to Staging

  prod:
    mode: production
    # Can override catalog/schema
    # Models registered to Production
```

**Environment Parity**: Same code, different configurations
- Variable substitution: `${bundle.target}`
- Environment-specific parameters
- Different resource naming
- Separate MLflow experiments

## 🔧 Troubleshooting

### Common Issues

#### Issue: Terraform Deployment Fails with Authentication Error

```
Error: azure-client-id is required
```

**Solution**:
1. Verify all secrets are set in GitHub Actions
2. Check secret names match exactly (case-sensitive)
3. Verify Service Principal credentials are valid

#### Issue: DAB Deployment Fails After Terraform Destroy/Recreate

```
Error: cluster '<cluster-id>' not found
Error: RESOURCE_DOES_NOT_EXIST: Workspace not found
```

**Root Cause**: After running `terraform destroy` and `terraform apply`, the following values change:
- Databricks workspace URL (`DATABRICKS_HOST`)
- Cluster ID (`DATABRICKS_CLUSTER_ID`)
- Access tokens (`DATABRICKS_TOKEN`)

**Solution - Update All Affected Secrets**:

1. **Get new Databricks Host**:
   ```bash
   cd terraform
   terraform output databricks_host
   # Example output: adb-1234567890123456.7.azuredatabricks.net
   ```

2. **Get new Cluster ID**:
   ```bash
   terraform output databricks_cluster_id
   # Example output: 1229-221552-7wmjd6ef
   ```

3. **Generate new Databricks Token**:
   - Login to the NEW Databricks workspace URL
   - User Settings → Access Tokens → Generate New Token
   - Copy the token value

4. **Update GitHub Secrets** (all three must be updated):
   ```bash
   # Update Databricks Host
   gh secret set DATABRICKS_HOST --body="<new-workspace-url>"

   # Update Cluster ID
   gh secret set DATABRICKS_CLUSTER_ID --body="<new-cluster-id>"

   # Update Access Token
   gh secret set DATABRICKS_TOKEN --body="<new-token>"
   ```

5. **Redeploy DAB**:
   ```bash
   databricks bundle deploy -t dev --var="cluster_id=<new-cluster-id>"
   ```

**Important**: This is required EVERY time you run `terraform destroy` followed by `terraform apply`, as new Databricks resources are created with different IDs.

#### Issue: DAB Validation Fails

```
Error: failed to load databricks.yml
```

**Solution**:
1. Check YAML syntax (indentation, quotes)
2. Validate variable references: `${var.variable_name}`
3. Ensure notebook paths are correct (relative to bundle root)

#### Issue: Job Fails to Run - Cluster Not Found

```
Error: Cluster <id> does not exist
```

**Solution**:
1. Verify cluster is running in Databricks UI
2. Check `cluster_id` variable matches deployed cluster
3. Ensure cluster has not auto-terminated

#### Issue: MLflow Directory Error

```
Error: RESOURCE_DOES_NOT_EXIST: Workspace directory '/Shared/dab-lab/experiments' not found
```

**Solution**:
The MLflow experiments directory is created by Terraform. If you see this error:
1. Verify Terraform deployment completed successfully
2. Check the directory exists in Databricks: Workspace → Shared → dab-lab → experiments
3. If missing, re-run Terraform apply

**Important for Cleanup**: Before running `terraform destroy`, manually delete the MLflow experiments directory and its contents from the Databricks UI to avoid "directory not empty" errors.

#### Issue: Sample Data Not Found

```
Error: Table or view not found: hive_metastore.dab_lab.raw_customer_data
```

**Solution**:
Run the setup job first:
```bash
databricks bundle run setup_sample_data -t dev
```

### Debug Mode

Enable debug logging:

```bash
# Terraform
export TF_LOG=DEBUG
terraform apply

# Databricks CLI
databricks bundle deploy -t dev --debug

# Azure CLI
az login --debug
```

### Getting Help

For issues not covered here:
1. Check [Databricks Asset Bundles Documentation](https://docs.databricks.com/dev-tools/bundles/index.html)
2. Review GitHub Actions workflow logs
3. Check Databricks job run logs in the workspace UI
4. Open an issue in this repository

## 🤝 Contributing

Contributions are welcome! This repository is designed as a learning resource and demonstration of DAB best practices.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Areas for Contribution

- Additional DAB job examples
- Enhanced error handling
- Additional data quality checks
- Performance optimizations
- Documentation improvements
- Bug fixes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Databricks](https://databricks.com/) for the Asset Bundles framework
- [HashiCorp](https://www.hashicorp.com/) for Terraform
- The data engineering and MLOps community

## 📬 Contact

For questions or feedback:
- Open an issue in this repository
- Follow me on [Medium](https://medium.com/@yourghusername) for the full article

---

**Built with ❤️ for the Data Engineering community**

**Keywords**: Databricks, Asset Bundles, DAB, Azure, Terraform, CI/CD, MLOps, DataOps, Infrastructure as Code, GitHub Actions, ETL, Machine Learning
