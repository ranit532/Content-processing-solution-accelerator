output storageConnectionString string = listKeys(resourceId('Microsoft.Storage/storageAccounts', '${projectName}sa'), '2022-09-01').keys[0].value
