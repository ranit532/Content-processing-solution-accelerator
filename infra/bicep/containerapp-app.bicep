param containerAppEnvId string
param name string
param image string
param registryServer string
param registryUsername string
param registryPassword string
param envVars object = {}

resource app 'Microsoft.App/containerApps@2023-06-01' = {
  name: name
  location: resourceGroup().location
  properties: {
    managedEnvironmentId: containerAppEnvId
    configuration: {
      registries: [
        {
          server: registryServer
          username: registryUsername
          password: registryPassword
        }
      ]
    }
    template: {
      containers: [
        {
          name: name
          image: image
          env: [for keyVal in envVars: {
            name: keyVal[0]
            value: keyVal[1]
          }]
          resources: {
            cpu: 0.5
            memory: '1.0Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
    identity: {
      type: 'UserAssigned'
      userAssignedIdentities: {
        '${userAssignedIdentityId}': {}
      }
    }
  }
}

output appId string = app.id
output fqdn string = app.properties.configuration.ingress.fqdn
