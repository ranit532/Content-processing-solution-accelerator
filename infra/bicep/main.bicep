param location string = resourceGroup().location
param projectName string = 'my-content-processing-solution-accelerator'

// Shorter prefix required for Azure resource naming limits
param prefix string = 'cpsa'

// Optional secrets (set via Key Vault or pipeline, not used directly here)
param openaiApiKey string = ''
param cosmosKey string = ''

//
// STORAGE ACCOUNT
//
resource sa 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: toLower('${prefix}sa')
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {}
}

// Blob service
resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2022-09-01' = {
  parent: sa
  name: 'default'
}

resource blobContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2022-09-01' = {
  parent: blobService
  name: 'documents'
  properties: {}
}

//
// QUEUE STORAGE
//
resource queueService 'Microsoft.Storage/storageAccounts/queueServices@2022-09-01' = {
  parent: sa
  name: 'default'
}

resource queue 'Microsoft.Storage/storageAccounts/queueServices/queues@2022-09-01' = {
  parent: queueService
  name: 'processing-queue'
  properties: {}
}

//
// COSMOS DB ACCOUNT
//
resource cosmos 'Microsoft.DocumentDB/databaseAccounts@2021-10-15' = {
  name: toLower('${prefix}cosmos')
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

//
// COSMOS DB SQL DATABASE
//
resource cosmosDb 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2021-10-15' = {
  parent: cosmos
  name: 'contentdb'
  properties: {
    resource: {
      id: 'contentdb'
    }
  }
}

//
// COSMOS DB SQL CONTAINER
//
resource cosmosContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2021-10-15' = {
  parent: cosmosDb
  name: 'items'
  properties: {
    resource: {
      id: 'items'
      partitionKey: {
        paths: ['/id']
        kind: 'Hash'
      }
    }
  }
}

//
// CONTAINER REGISTRY
//
resource acr 'Microsoft.ContainerRegistry/registries@2022-02-01-preview' = {
  name: toLower('${prefix}acr')
  location: location
  sku: {
    name: 'Basic'
  }
}

//
// LOG ANALYTICS WORKSPACE
//
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2020-08-01' = {
  name: toLower('${prefix}-logs')
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
  }
}

//
// MANAGED IDENTITY
//
resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2018-11-30' = {
  name: toLower('${prefix}-identity')
  location: location
}

//
// KEY VAULT
//
resource keyVault 'Microsoft.KeyVault/vaults@2021-10-01' = {
  name: toLower('${prefix}-kv')
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

//
// CONTAINER APPS ENVIRONMENT
//
resource containerAppEnv 'Microsoft.App/managedEnvironments@2022-03-01' = {
  name: toLower('${prefix}-env')
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

//
// OUTPUTS
//
output storageAccountName string = sa.name
output storageAccountId string = sa.id
output cosmosName string = cosmos.name
output acrName string = acr.name
output keyVaultName string = keyVault.name
output identityClientId string = identity.properties.clientId
output logAnalyticsName string = logAnalytics.name
output containerAppEnvId string = containerAppEnv.id
