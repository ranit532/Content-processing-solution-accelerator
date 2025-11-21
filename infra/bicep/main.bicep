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

// Blob service (parent for containers)
resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2022-09-01' = {
  parent: sa
  name: 'default'
}

resource blobContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2022-09-01' = {
  parent: blobService
  name: 'documents'
  properties: {}
}

// Queue service (parent for queues)
resource queueService 'Microsoft.Storage/storageAccounts/queueServices@2022-09-01' = {
  parent: sa
  name: 'default'
}

resource queue 'Microsoft.Storage/storageAccounts/queueServices/queues@2022-09-01' = {
  parent: queueService
  name: 'processing-queue'
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
    accessPolicies: []
    enableSoftDelete: true
  }
}

// NOTE: Key Vault secrets are set post-deployment via az keyvault secret set to avoid deployment permission issues.

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
}

// NOTE: role assignments are intentionally not created here to avoid scope mismatch errors
// Role assignments will be created post-deployment using the Azure CLI with the managed identity principalId.

// Outputs
output storageAccountName string = sa.name
output storageAccountId string = sa.id
output cosmosName string = cosmos.name
output acrName string = acr.name
output keyVaultName string = keyVault.name
output identityClientId string = identity.properties.clientId
output logAnalyticsName string = logAnalytics.name
output containerAppEnvId string = containerAppEnv.id
