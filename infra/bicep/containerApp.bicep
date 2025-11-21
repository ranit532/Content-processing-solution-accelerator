@description('Name of the Container App Environment')
param containerAppEnvName string = 'my-content-env'
param location string = resourceGroup().location

resource containerAppEnv 'Microsoft.Web/containerApps/environments@2023-10-01' = {
  name: containerAppEnvName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
    }
  }
}

output containerAppEnvId string = containerAppEnv.id
