param location string = resourceGroup().location
param projectName string = 'my-content-processing-solution-accelerator'

// Optional secret values can be passed during deployment; for production use secure pipelines or Key Vault.
param openaiApiKey string = ''
param cosmosKey string = ''

// Storage account
resource sa 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: toLower('${projectName}sa')
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {}
}

resource blobContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2022-09-01' = {
  parent: sa
  name: 'default/documents'
  properties: {}
}

// Queue
resource queue 'Microsoft.Storage/storageAccounts/queueServices/queues@2022-09-01' = {
  parent: sa
  name: 'default/processing-queue'
  properties: {}
}

// Cosmos DB
resource cosmos 'Microsoft.DocumentDB/databaseAccounts@2021-10-15' = {
  name: toLower('${projectName}cosmos')
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    locations: [
      { locationName: location }
    ]
  }
}

// Container Registry
resource acr 'Microsoft.ContainerRegistry/registries@2022-02-01-preview' = {
  name: toLower('${projectName}acr')
  sku: {
    name: 'Basic'
  }
  location: location
}

// Log Analytics workspace
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2020-08-01' = {
  name: toLower('${projectName}-logs')
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
  }
}

// Managed identity for apps
resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2018-11-30' = {
  name: toLower('${projectName}-identity')
  location: location
}

// Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2021-10-01' = {
  name: toLower('${projectName}-kv')
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: {
      name: 'standard'
      family: 'A'
    }
    // Grant the user-assigned identity access to secrets via an access policy
    accessPolicies: [
      {
        tenantId: subscription().tenantId
        objectId: identity.principalId
        permissions: {
          secrets: [
            'get'
            'list'
            'set'
            'delete'
          ]
        }
      }
    ]
    enableSoftDelete: true
  }
}

// Provision Key Vault secrets (values provided as parameters during deployment or empty placeholders)
resource kvSecretOpenAI 'Microsoft.KeyVault/vaults/secrets@2021-10-01' = {
  name: '${keyVault.name}/OPENAI_API_KEY'
  properties: {
    value: openaiApiKey
  }
  dependsOn: [keyVault]
}

resource kvSecretCosmos 'Microsoft.KeyVault/vaults/secrets@2021-10-01' = {
  name: '${keyVault.name}/COSMOS_KEY'
  properties: {
    value: cosmosKey
  }
  dependsOn: [keyVault]
}

// Container App Environment (managed environment) linked to Log Analytics
resource containerAppEnv 'Microsoft.App/managedEnvironments@2022-03-01' = {
  name: toLower('${projectName}-env')
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: listKeys(resourceId('Microsoft.OperationalInsights/workspaces', logAnalytics.name), '2020-08-01').primarySharedKey
      }
    }
  }
  dependsOn: [logAnalytics]
}

// Role assignment: grant Storage Blob Data Contributor to the user-assigned identity on the storage account
resource storageBlobRole 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = if (identity != null) {
  name: guid(sa.id, identity.principalId, 'storageBlobDataContributor')
  properties: {
    principalId: identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe') // Storage Blob Data Contributor
    scope: sa.id
  }
  dependsOn: [identity, sa]
}

// Role assignment: grant Managed Identity Reader on Key Vault (RBAC) - optional
resource keyVaultRole 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = if (identity != null) {
  name: guid(keyVault.id, identity.principalId, 'keyVaultReader')
  properties: {
    principalId: identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'acdd72a7-3385-48ef-bd42-f606fba81ae7') // Contributor (use appropriate limited role in production)
    scope: keyVault.id
  }
  dependsOn: [identity, keyVault]
}

// Outputs
output storageAccountName string = sa.name
output storageAccountId string = sa.id
output cosmosName string = cosmos.name
output acrName string = acr.name
output keyVaultName string = keyVault.name
output identityClientId string = identity.clientId
output logAnalyticsName string = logAnalytics.name
output containerAppEnvId string = containerAppEnv.id
