# Infrastructure provisioning (Bicep)

This document summarizes the exact steps performed to provision the Azure infrastructure for the Content Processing POC and contains the commands you can run locally (or in CI) to reproduce the deployment using the Bicep template in `infra/bicep/main.bicep`.

WARNING: do not paste production secrets into CI logs or public chat. Use Key Vault or CI secret storage.

## Prerequisites

- Azure CLI installed and logged-in: `az login`
- Target Azure subscription selected: `az account set --subscription "<SUB_ID_OR_NAME>"`
- Enough permissions to create resources in the target subscription / resource group
- Bicep tooling available through the Azure CLI (az will prompt to install if needed)

## Files

- `infra/bicep/main.bicep` — Bicep template that creates Storage (blob + queue), Cosmos DB account, ACR, Log Analytics workspace, User-assigned Managed Identity, Key Vault and Container Apps Managed Environment.
- `infra/params.deploy.json` — example parameters file used for the deployment (created during the run).

> Note: role assignments and Key Vault secrets are intentionally NOT created inside the Bicep template. This avoids deployment scope and permission issues (role assignment scope mismatch and Key Vault access/permission problems). Role assignments and secrets are created explicitly after the template deployment using `az` commands.

---

## High-level steps performed

1. Create a resource group.
2. Deploy the `main.bicep` template into the resource group (no secrets in-template).
3. Inspect the deployment outputs to discover resource names (storage, key vault, ACR, identity etc.).
4. Create role assignments for the user-assigned managed identity (so the app can access Storage + Key Vault secrets).
5. Grant CLI principal access to Key Vault (so you or the deployer can set secrets), then set the OPENAI API key into Key Vault.
6. (Optional) Create a service principal for CI/CD and assign minimal permissions (ACR push, Container Apps deploy).

---

## Commands (run in zsh)

### 1) Create resource group (example)

```bash
az group create -n my-cpsa-rg -l eastus
```

### 2) Create a small params file (we used `infra/params.deploy.json`)

Create the file (example content):

```json
{
  "projectName": { "value": "cpsa" },
  "openaiApiKey": { "value": "" },
  "cosmosKey": { "value": "" }
}
```

We leave secret values empty so Key Vault exists but secrets are set post-deploy.

### 3) Deploy the Bicep template to the resource group

```bash
az deployment group create -g my-cpsa-rg --template-file infra/bicep/main.bicep --parameters @infra/params.deploy.json --name cpsa-deploy
```

This will create resources and produce outputs. If the deployment succeeds it will print an object with `outputs`.

### 4) Read deployment outputs (to find resource names)

```bash
az deployment group show -g my-cpsa-rg -n cpsa-deploy --query properties.outputs
```

Example outputs from a sample run (your names will match these patterns):

- storageAccountName: `cpsasa`
- acrName: `cpsaacr`
- cosmosName: `cpsacosmos`
- keyVaultName: `cpsa-kv`
- identityClientId: `<client-id>`
- containerAppEnvId: `/subscriptions/.../providers/Microsoft.App/managedEnvironments/cpsa-env`

### 5) Get the managed identity principalId (needed for role assignment)

```bash
az identity show -g my-cpsa-rg -n cpsa-identity --query principalId -o tsv
# example result: ebce1b85-c940-45f6-8475-9fed04f6e2de
```

### 6) Create role assignments for the managed identity (grant resource access)

- Grant Storage Blob Data Contributor (so apps can read/write blobs):

```bash
az role assignment create --assignee <PRINCIPAL_ID> --role "Storage Blob Data Contributor" --scope /subscriptions/<SUB_ID>/resourceGroups/my-cpsa-rg/providers/Microsoft.Storage/storageAccounts/<storageAccountName>
```

- Grant Key Vault Secrets User (so apps can read secrets at runtime):

```bash
az role assignment create --assignee <PRINCIPAL_ID> --role "Key Vault Secrets User" --scope /subscriptions/<SUB_ID>/resourceGroups/my-cpsa-rg/providers/Microsoft.KeyVault/vaults/<keyVaultName>
```

Replace `<PRINCIPAL_ID>`, `<SUB_ID>`, `<storageAccountName>` and `<keyVaultName>` with real values from the deployment outputs.

### 7) Grant your CLI principal permission to set secrets in Key Vault (so you can set OPENAI key)

If the account you used to deploy doesn't already have Key Vault secret permissions you must grant them before setting secrets.

Get your signed-in user object id (example):

```bash
az ad signed-in-user show --query id -o tsv
```

Then grant secret permissions on the vault:

```bash
az keyvault set-policy --name <keyVaultName> --object-id <YOUR_OBJECT_ID> --secret-permissions get list set delete
```

### 8) Set the OPENAI key in Key Vault securely

Prefer to use an environment variable so the value is not left in shell history:

```bash
export OPENAI_KEY="<YOUR_OPENAI_KEY>"
az keyvault secret set --vault-name <keyVaultName> --name OPENAI-API-KEY --value "$OPENAI_KEY"
unset OPENAI_KEY
```

> Important: Key Vault secret names must follow allowed characters (use hyphens, lowercase/uppercase letters and digits; avoid underscores for the CLI). In this repo we used `OPENAI-API-KEY`.

### 9) Verify secret exists

```bash
az keyvault secret show --vault-name <keyVaultName> --name OPENAI-API-KEY --query id -o tsv
```

---

## What we changed vs. a single-template approach

During deployment we encountered two common real-world issues:

1. Role assignment creation inside the same resource-group scoped deployment can fail due to scope mismatch constraints. To avoid this, role assignments were created explicitly with `az role assignment create` after the resources were created.

2. Key Vault secret creation in-template failed because the deploying principal did not have Key Vault `set` permission. To avoid blocked deployments we removed Key Vault secret resources from the template and set secrets after the vault exists (and after granting the deployer CLI access to set secrets).

These changes improve reliability during iterative development and allow centralised, auditable secret provisioning.

---

## Post-deploy next steps (recommended)

- Create a CI service principal and give it minimal permissions needed for your pipeline (ACR push + Container Apps deploy or a service connection in Azure DevOps/GitHub Actions). Example to create an SP and capture credentials:

```bash
az ad sp create-for-rbac --name "cpsa-sp" --role Contributor --scopes /subscriptions/<SUB_ID>/resourceGroups/my-cpsa-rg
```

- Build and push Docker images to ACR (use `az acr login` and `docker build`/`docker push` or pipeline tasks).
- Deploy container apps (or other compute) using the managed identity and Key Vault secrets. Container Apps can reference Key Vault via managed identity at runtime.
- Test the API endpoints and run the smoke test script included in `scripts/smoke_test.py`.

---

## Troubleshooting

- If deployment fails with role assignment scope errors, ensure you create role assignments after deployment at the correct resource or subscription scope as shown above.
- If `az keyvault secret set` returns `Forbidden`, grant your user secret permissions using `az keyvault set-policy` or use the Portal to add an access policy.
- If Bicep emits parameter warnings (length), make sure `projectName` values meet Azure resource name constraints or adjust naming.

---

## Commands I ran (exact sequence)

Below are the exact commands I executed interactively while provisioning your infra. You can copy/paste these in order (replace placeholders) to reproduce the same result.

1) Create resource group

```bash
az group create -n my-cpsa-rg -l eastus
```

2) Create a params file used for deployment (leave secrets empty)

```bash
cat > infra/params.deploy.json <<EOF
{
  "projectName": { "value": "cpsa" },
  "openaiApiKey": { "value": "" },
  "cosmosKey": { "value": "" }
}
EOF
```

3) Deploy the Bicep template

```bash
az deployment group create -g my-cpsa-rg --template-file infra/bicep/main.bicep --parameters @infra/params.deploy.json --name cpsa-deploy-3
```

4) Show deployment outputs (capture resource names)

```bash
az deployment group show -g my-cpsa-rg -n cpsa-deploy-3 --query properties.outputs
```

5) Get the managed identity principalId

```bash
az identity show -g my-cpsa-rg -n cpsa-identity --query principalId -o tsv
# -> principalId (save this value)
```

6) Create role assignments for the managed identity

```bash
# Storage access (Blob Data Contributor)
az role assignment create --assignee <PRINCIPAL_ID> --role "Storage Blob Data Contributor" --scope /subscriptions/<SUB_ID>/resourceGroups/my-cpsa-rg/providers/Microsoft.Storage/storageAccounts/<storageAccountName>

# Key Vault access (Secrets User)
az role assignment create --assignee <PRINCIPAL_ID> --role "Key Vault Secrets User" --scope /subscriptions/<SUB_ID>/resourceGroups/my-cpsa-rg/providers/Microsoft.KeyVault/vaults/<keyVaultName>
```

7) Grant your CLI principal permission to set secrets (if needed)

```bash
# get your signed-in user id
az ad signed-in-user show --query id -o tsv

# grant secret permissions on the vault
az keyvault set-policy --name <keyVaultName> --object-id <YOUR_OBJECT_ID> --secret-permissions get list set delete
```

8) Set the OPENAI API key into Key Vault securely

```bash
export OPENAI_KEY="<YOUR_OPENAI_KEY>"
az keyvault secret set --vault-name <keyVaultName> --name OPENAI-API-KEY --value "$OPENAI_KEY"
unset OPENAI_KEY
```

9) (Optional) Create a CI service principal and give it permissions

```bash
# Create SP for ACR push scope (returns appId, password, tenant)
az ad sp create-for-rbac --name "cpsa-sp" --role "AcrPush" --scopes /subscriptions/<SUB_ID>/resourceGroups/my-cpsa-rg/providers/Microsoft.ContainerRegistry/registries/<acrName> -o json

# (I also created a Contributor assignment at the RG level interactively)
az role assignment create --assignee <SP_APPID> --role "Contributor" --scope /subscriptions/<SUB_ID>/resourceGroups/my-cpsa-rg
```

10) Store CI service principal credentials in Key Vault (example)

```bash
# store appId
echo "<SP_APPID>" | az keyvault secret set --vault-name <keyVaultName> --name cpsa-sp-appid --value @-
# store secret
echo "<SP_PASSWORD>" | az keyvault secret set --vault-name <keyVaultName> --name cpsa-sp-secret --value @-
# store tenant
echo "<SP_TENANT>" | az keyvault secret set --vault-name <keyVaultName> --name cpsa-sp-tenant --value @-
```

11) Retrieve secrets from Key Vault in CI or locally

```bash
# get secret value (in CI use a secure method to retrieve and set as env vars)
az keyvault secret show --vault-name <keyVaultName> --name OPENAI-API-KEY --query value -o tsv

# or retrieve SP creds stored earlier
az keyvault secret show --vault-name <keyVaultName> --name cpsa-sp-appid --query value -o tsv
az keyvault secret show --vault-name <keyVaultName> --name cpsa-sp-secret --query value -o tsv
az keyvault secret show --vault-name <keyVaultName> --name cpsa-sp-tenant --query value -o tsv
```

Notes & troubleshooting

- Role assignments: if you see `InvalidCreateRoleAssignmentRequest` during a single deployment, create role assignments after resources are deployed (as shown above).
- Key Vault permissions: `az keyvault secret set` can fail with `Forbidden` unless your CLI principal has an access policy or RBAC permission to set secrets. Use `az keyvault set-policy` to add `set` permission for your user or set secrets through a service principal with proper permissions.
- Secret naming: avoid underscores in secret names when using CLI; use hyphens (we used `OPENAI-API-KEY`).
- Audit & rotation: rotate service principal secrets periodically and use Key Vault references in CI.

If you want, I can commit this README update (already saved) and also create a dedicated script (`infra/scripts/deploy.sh`) that wraps these commands and prompts for inputs. Tell me if you want the deploy script created.

