# Development Guidelines for Databricks DAB Lab

This document provides coding standards, best practices, and conventions for contributing to this Databricks Asset Bundles (DAB) repository.

## 🌍 Language Requirements

### Code and Documentation Language: ENGLISH

All code, comments, documentation, and variable names must be in English:

✅ **DO**:
```python
# Extract customer data from source
def extract_customer_data(source_path: str) -> DataFrame:
    """
    Extracts customer data from the specified source path.

    Args:
        source_path: Path to the source data

    Returns:
        DataFrame containing customer data
    """
    return spark.read.csv(source_path)
```

❌ **DON'T**:
```python
# Estrai dati clienti dalla fonte
def estrai_dati_clienti(percorso_fonte: str) -> DataFrame:
    # Non usare nomi/commenti in altre lingue
    return spark.read.csv(percorso_fonte)
```

## 📝 Code Comments

### Minimal but Meaningful Comments

Comments should be minimal, clear, and add value. Avoid obvious comments.

✅ **DO**:
```python
# Use hyperparameter tuning to optimize model performance
param_grid = {'n_estimators': [50, 100, 150]}

# Retry on transient failures (network timeouts, rate limits)
@retry(max_attempts=3, backoff=exponential)
def api_call():
    pass
```

❌ **DON'T**:
```python
# This is a variable
x = 10

# Loop through items
for item in items:
    # Print item
    print(item)
```

### When to Add Comments

1. **Complex Business Logic**: Explain WHY, not WHAT
   ```python
   # Apply 20% discount for customers with quality score >= 0.8
   # Business rule: high-quality data indicates verified customers
   df = df.withColumn("discount", when(col("quality_score") >= 0.8, 0.20).otherwise(0))
   ```

2. **Non-obvious Technical Decisions**
   ```python
   # Use repartition(1) to ensure single output file for downstream system
   # Trade-off: Performance vs downstream compatibility
   df.repartition(1).write.parquet(output_path)
   ```

3. **Security or Performance Considerations**
   ```python
   # Escape user input to prevent SQL injection
   safe_query = query.replace("'", "''")
   ```

## 🔐 Security Best Practices

### Azure Security

1. **Service Principal Authentication**
   ```python
   # ✅ Use environment variables or Azure Key Vault
   client_id = os.environ.get("AZURE_CLIENT_ID")

   # ❌ Never hardcode credentials
   client_id = "abc-123-def-456"  # WRONG!
   ```

2. **Secrets Management**
   ```yaml
   # ✅ Reference secrets from Databricks Secret Scope
   notebook_task:
     base_parameters:
       api_key: "{{secrets/dab-lab-secrets/api-key}}"

   # ❌ Don't put secrets in configuration files
   notebook_task:
     base_parameters:
       api_key: "my-secret-key-12345"  # WRONG!
   ```

3. **Network Security**
   ```hcl
   # Use private endpoints in production
   resource "azurerm_databricks_workspace" "main" {
     public_network_access_enabled = false  # Production setting
     # Use true only for development/testing
   }
   ```

4. **Least Privilege Principle**
   ```bash
   # Assign minimal required permissions
   # ✅ Specific scope
   az role assignment create \
     --role "Contributor" \
     --scope "/subscriptions/xxx/resourceGroups/rg-databricks"

   # ❌ Too broad
   az role assignment create \
     --role "Owner" \
     --scope "/subscriptions/xxx"  # WRONG!
   ```

### Data Security

1. **Data Encryption**
   ```python
   # Enable encryption at rest for Delta tables
   spark.conf.set("spark.databricks.delta.properties.defaults.encryption.enabled", "true")
   ```

2. **PII/Sensitive Data Handling**
   ```python
   # ✅ Mask sensitive data in logs
   logger.info(f"Processing customer: {customer_id[:4]}****")

   # ❌ Don't log sensitive data
   logger.info(f"Processing email: {email}")  # WRONG!
   ```

## 📏 Naming Conventions

### Azure Resources

Follow Azure naming best practices with consistent prefixes:

| Resource Type | Prefix | Example |
|---------------|--------|---------|
| Resource Group | `rg-` | `rg-databricks-dab-lab-dev-ne` |
| Databricks Workspace | `dbw-` | `dbw-databricks-dab-lab-dev-ne` |
| Storage Account | `st` | `stdablab<unique>` (no hyphens, lowercase) |
| Key Vault | `kv-` | `kv-databricks-dab-lab-dev` |

**Pattern**: `<prefix>-<project>-<environment>-<region>`

```hcl
# ✅ Good naming
resource "azurerm_resource_group" "main" {
  name     = "rg-databricks-dab-lab-dev-ne"
  location = "northeurope"
}

# ❌ Bad naming
resource "azurerm_resource_group" "main" {
  name     = "myResourceGroup123"  # WRONG!
  location = "northeurope"
}
```

### Python Code

Follow PEP 8 with Databricks-specific conventions:

```python
# Variables and functions: snake_case
customer_data = load_data()
def extract_customer_data():
    pass

# Classes: PascalCase
class DataQualityValidator:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 300

# Private methods: prefix with _
def _internal_helper():
    pass
```

### YAML Configuration

```yaml
# Use lowercase with underscores for keys
resources:
  jobs:
    etl_pipeline:  # snake_case
      name: "ETL Pipeline - ${bundle.target}"  # Use bundle variables

# ❌ Don't use camelCase or PascalCase in YAML keys
resources:
  jobs:
    ETLPipeline:  # WRONG!
      name: "pipeline"
```

## 🏗️ Terraform Best Practices

### Resource Tagging

Always use centralized tags:

```hcl
# ✅ Centralized tags in locals.tf
locals {
  common_tags = merge(
    var.tags,
    {
      Location   = var.location
      DeployedAt = timestamp()
      Terraform  = "true"
    }
  )
}

resource "azurerm_resource_group" "main" {
  name     = local.resource_group_name
  location = var.location
  tags     = local.common_tags  # Apply to all resources
}
```

### State Management

```hcl
# ✅ Use remote backend for team collaboration
terraform {
  backend "azurerm" {
    resource_group_name  = var.tf_state_resource_group
    storage_account_name = var.tf_state_storage_account
    container_name       = "tfstate"
    key                  = "databricks-dab-lab.tfstate"
  }
}

# ❌ Don't use local state for shared projects
terraform {
  backend "local" {  # WRONG for team projects!
    path = "terraform.tfstate"
  }
}
```

### Sensitive Variables

```hcl
# Always mark sensitive variables
variable "azure_client_secret" {
  description = "Azure Service Principal Client Secret"
  type        = string
  sensitive   = true  # Prevents output in logs
}
```

## 🐍 Python/PySpark Best Practices

### DataFrame Operations

```python
# ✅ Chain operations for readability
df_result = (df_source
    .filter(col("status") == "active")
    .withColumn("full_name", concat(col("first_name"), lit(" "), col("last_name")))
    .select("customer_id", "full_name", "email")
)

# ✅ Use explicit column references
from pyspark.sql.functions import col
df.filter(col("age") > 18)

# ❌ Avoid string column references (error-prone)
df.filter("age > 18")  # Less safe
```

### Error Handling

```python
# ✅ Specific exception handling with context
try:
    df = spark.read.parquet(path)
except FileNotFoundError as e:
    logger.error(f"Data file not found at {path}: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error reading {path}: {e}")
    raise

# ❌ Bare except (hides errors)
try:
    df = spark.read.parquet(path)
except:  # WRONG!
    pass
```

### Logging

```python
# ✅ Use structured logging
import logging
logger = logging.getLogger(__name__)

logger.info(f"Processing {record_count} records from {source_table}")
logger.warning(f"Data quality score {score:.2f} below threshold {threshold}")
logger.error(f"Failed to write to {target_table}: {error}")

# ❌ Print statements (not production-ready)
print("Processing data...")  # WRONG for production!
```

## 📦 DAB Configuration Best Practices

### Job Configuration

```yaml
# ✅ Use variables for environment-specific values
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
              environment: ${bundle.target}

# ❌ Don't hardcode environment-specific values
resources:
  jobs:
    etl_pipeline:
      name: "ETL Pipeline - Dev"  # WRONG!
      tasks:
        - task_key: extract
          notebook_task:
            base_parameters:
              source_table: dev_catalog.schema.raw_data  # WRONG!
```

### Multi-Environment Configuration

```yaml
targets:
  dev:
    mode: development  # Allows in-place updates
    variables:
      catalog: dev_catalog
      schema: dab_lab

  prod:
    mode: production  # Immutable deployments
    variables:
      catalog: prod_catalog
      schema: dab_lab
    # Additional validation for production
```

## 🧪 Testing and Validation

### Pre-Deployment Validation

```bash
# Always validate before deploying
databricks bundle validate -t dev

# Run local syntax checks
terraform fmt -check -recursive
terraform validate
```

### Data Quality Checks

```python
# ✅ Include assertions for data quality
assert df.count() > 0, "DataFrame is empty"
assert df.filter(col("customer_id").isNull()).count() == 0, "Null customer IDs found"

# Include in notebooks for automated validation
if df.count() == 0:
    raise ValueError("No data to process")
```

## 📚 Documentation Standards

### README Files

Each major component should have documentation:

```markdown
# Component Name

## Purpose
Brief description of what this does

## Usage
Example code or commands

## Configuration
Required settings and variables

## Troubleshooting
Common issues and solutions
```

### Inline Documentation

```python
def train_model(X_train, y_train, params):
    """
    Train a Random Forest model with specified hyperparameters.

    Args:
        X_train: Training features (pandas DataFrame)
        y_train: Training labels (pandas Series)
        params: Hyperparameter dictionary with keys:
                - n_estimators: Number of trees
                - max_depth: Maximum tree depth

    Returns:
        Trained RandomForestClassifier model

    Raises:
        ValueError: If params are invalid
    """
    # Implementation
```

## 🚫 Common Pitfalls to Avoid

### 1. Hardcoded Values
```python
# ❌ WRONG
df.write.parquet("/mnt/dev/data/output")

# ✅ CORRECT
output_path = dbutils.widgets.get("output_path")
df.write.parquet(output_path)
```

### 2. Ignoring Errors
```python
# ❌ WRONG
try:
    process_data()
except:
    pass  # Silent failure

# ✅ CORRECT
try:
    process_data()
except Exception as e:
    logger.error(f"Processing failed: {e}")
    raise
```

### 3. Not Using Variables
```yaml
# ❌ WRONG
notebook_task:
  base_parameters:
    catalog: "dev_catalog"  # Different in each environment

# ✅ CORRECT
notebook_task:
  base_parameters:
    catalog: ${var.catalog}  # Configured per environment
```

## 🔄 Git Workflow

### Commit Messages

Follow conventional commits:

```bash
# ✅ Good commit messages
git commit -m "feat: add ML training pipeline with hyperparameter tuning"
git commit -m "fix: correct data quality validation threshold"
git commit -m "docs: update README with deployment instructions"
git commit -m "refactor: optimize ETL transform step for performance"

# ❌ Bad commit messages
git commit -m "update"
git commit -m "fixes"
git commit -m "commit message must not include any claude bot / commit user etc"
```

### Branch Naming

```bash
# ✅ Descriptive branch names
git checkout -b feature/add-data-quality-checks
git checkout -b fix/etl-pipeline-timeout
git checkout -b docs/update-secrets-guide

# ❌ Vague branch names
git checkout -b update
git checkout -b test
```

## 📊 Performance Best Practices

### Spark Optimization

```python
# ✅ Partition large datasets
df.repartition(col("date")).write.partitionBy("date").parquet(path)

# ✅ Cache when reusing DataFrames
df_cached = df.filter(col("status") == "active").cache()
df_cached.count()  # Trigger caching
# ... use df_cached multiple times

# ✅ Broadcast small lookup tables
from pyspark.sql.functions import broadcast
df_joined = df_large.join(broadcast(df_small), "key")

# ❌ Don't collect large datasets to driver
large_data = df.collect()  # WRONG if df is large!
```

## 🎯 Summary Checklist

Before committing code, verify:

- [ ] All code and comments are in English
- [ ] Comments are minimal and meaningful
- [ ] No secrets or credentials in code
- [ ] Naming conventions followed
- [ ] Variables used instead of hardcoded values
- [ ] Error handling implemented
- [ ] Logging added for important operations
- [ ] Data quality checks included
- [ ] Configuration validated (`databricks bundle validate`)
- [ ] Terraform formatted (`terraform fmt`)
- [ ] Commit message follows conventions

---

**These guidelines ensure code quality, security, and maintainability for the entire team.**