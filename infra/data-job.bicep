@description('Development-only batch job region.')
param location string = 'eastus2'
@description('Existing private lake account name.')
param storageAccountName string
@description('Existing private registry name.')
param registryName string
@description('Existing platform Log Analytics workspace name.')
param workspaceName string = 'log-iyqpis-dev'
@description('Dedicated Microsoft.App/environments delegated subnet; never pass the endpoint or runner subnet.')
param infrastructureSubnetId string
@description('Built and scanned image in the existing registry, pinned with @sha256:<digest>.')
param image string
@description('Stable UTC ingest timestamp for this sample snapshot. Preserve for retries.')
param ingestTime string
@description('Comma-separated approved sample dataset names; on-demand reference dataset by default.')
param datasets string = 'manufacturing-spc'

var tags = { workload: 'iyqpis', environment: 'dev', scope: 'data-engineering', managedBy: 'bicep' }
var writableContainers = ['validated', 'contextualized', 'curated-evidence']
resource lake 'Microsoft.Storage/storageAccounts@2023-05-01' existing = { name: storageAccountName }
resource blobs 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' existing = { parent: lake, name: 'default' }
resource raw 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' existing = { parent: blobs, name: 'raw' }
resource outputs 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' existing = [for name in writableContainers: { parent: blobs, name: name }]
resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = { name: registryName }
resource logs 'Microsoft.OperationalInsights/workspaces@2025-02-01' existing = { name: workspaceName }

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  name: 'id-iyqpis-dev-data'
  location: location
  tags: tags
}
resource rawReader 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(raw.id, identity.id, 'reader')
  scope: raw
  properties: {
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1')
  }
}
resource writers 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for (name, i) in writableContainers: {
  name: guid(outputs[i].id, identity.id, 'writer')
  scope: outputs[i]
  properties: {
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  }
}]
resource puller 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(registry.id, identity.id, 'pull')
  scope: registry
  properties: {
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
  }
}
resource batchEnvironment 'Microsoft.App/managedEnvironments@2025-07-01' = {
  name: 'cae-iyqpis-dev-data'
  location: location
  tags: tags
  properties: {
    publicNetworkAccess: 'Disabled'
    vnetConfiguration: { internal: true, infrastructureSubnetId: infrastructureSubnetId }
    workloadProfiles: [{ name: 'Consumption', workloadProfileType: 'Consumption' }]
    appLogsConfiguration: { destination: 'azure-monitor' }
  }
}
resource diagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'platform-logs'
  scope: batchEnvironment
  properties: {
    workspaceId: logs.id
    logs: [{ categoryGroup: 'allLogs', enabled: true }]
  }
}
resource batch 'Microsoft.App/jobs@2025-01-01' = {
  name: 'job-iyqpis-dev-data'
  location: location
  tags: tags
  identity: { type: 'UserAssigned', userAssignedIdentities: { '${identity.id}': {} } }
  properties: {
    environmentId: batchEnvironment.id
    workloadProfileName: 'Consumption'
    configuration: {
      triggerType: 'Manual'
      replicaTimeout: 3600
      replicaRetryLimit: 1
      manualTriggerConfig: { parallelism: 1, replicaCompletionCount: 1 }
      registries: [{ server: registry.properties.loginServer, identity: identity.id }]
    }
    template: {
      containers: [{
        name: 'data-batch'
        image: image
        resources: { cpu: 2, memory: '4Gi' }
        env: [
          { name: 'AZURE_CLIENT_ID', value: identity.properties.clientId }
          { name: 'DATA_STORAGE_ACCOUNT', value: lake.name }
          { name: 'INGEST_TIME', value: ingestTime }
          { name: 'DATASETS', value: datasets }
        ]
      }]
    }
  }
  dependsOn: [rawReader, writers, puller]
}
output jobName string = batch.name
