targetScope = 'resourceGroup'
param location string = 'eastus2'
param workspaceName string = 'mlw-iyqpis-dev'
param vaultName string = 'kv-4ilak3xb4dmrk'
param insightsName string = 'appi-iyqpis-dev'
param vnetName string = 'vnet-iyqpis-dev'
var tags = { workload: 'iyqpis', purpose: 'temporary-learning', managedBy: 'bicep' }
resource vault 'Microsoft.KeyVault/vaults@2024-11-01' existing = { name: vaultName }
resource insights 'Microsoft.Insights/components@2020-02-02' existing = { name: insightsName }
resource vnet 'Microsoft.Network/virtualNetworks@2024-07-01' existing = { name: vnetName }
resource subnet 'Microsoft.Network/virtualNetworks/subnets@2024-07-01' existing = { parent: vnet, name: 'snet-private-endpoints' }
resource blobZone 'Microsoft.Network/privateDnsZones@2024-06-01' existing = { name: 'privatelink.blob.${environment().suffixes.storage}' }
resource zones 'Microsoft.Network/privateDnsZones@2024-06-01' = [for name in ['privatelink.file.${environment().suffixes.storage}','privatelink.api.azureml.ms','privatelink.notebooks.azure.net']: {
  name: name
  location: 'global'
  tags: tags
}]
resource links 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = [for (name,i) in ['file','api','notebooks']: {
  parent: zones[i]
  name: 'link-ml-learning'
  location: 'global'
  properties: { registrationEnabled: false, virtualNetwork: { id: vnet.id } }
}]
resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  //checkov:skip=CKV_AZURE_36:Private-only storage deliberately has no trusted-service bypass; compiled security contract verifies this stricter boundary. See governance/azure-ml-scan-disposition.md.
  //checkov:skip=CKV_AZURE_43:stml plus uniqueString is a 17-character lowercase-alphanumeric name; compiled security contract pins the expression. See governance/azure-ml-scan-disposition.md.
  //checkov:skip=CKV_AZURE_206:Reference-only workspace uses LRS and has no ML compute/endpoints; geo-replication is not AML workspace failover. DR remains open; compiled guard rejects scope expansion. See governance/azure-ml-scan-disposition.md.
  name: 'stml${uniqueString(resourceGroup().id)}'
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: { name: 'Standard_LRS' }
  properties: {
    isHnsEnabled: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    defaultToOAuthAuthentication: true
    publicNetworkAccess: 'Disabled'
    networkAcls: { defaultAction: 'Deny', bypass: 'None' }
  }
}
resource workspace 'Microsoft.MachineLearningServices/workspaces@2025-06-01' = {
  //checkov:skip=CKV_AZURE_243:Rule checks managed outbound PrivateEndpoint rules, not workspace inbound Private Link. Compiled guard verifies inbound workspace/blob/file endpoints; managed compute remains absent. See governance/azure-ml-scan-disposition.md.
  name: workspaceName
  location: location
  tags: tags
  kind: 'Default'
  sku: { name: 'Basic', tier: 'Basic' }
  identity: { type: 'SystemAssigned' }
  properties: {
    friendlyName: 'IYQPIS learning workspace'
    description: 'Temporary model registration and batch-job walkthrough; no production authority.'
    storageAccount: storage.id
    keyVault: vault.id
    applicationInsights: insights.id
    systemDatastoresAuthMode: 'identity'
    publicNetworkAccess: 'Disabled'
    managedNetwork: { isolationMode: 'Disabled' }
  }
}
module workspaceEndpoint './modules/private-endpoint.bicep' = {
  name: 'ml-learning-workspace-endpoint'
  params: { name: 'pep-iyqpis-ml-learning', location: location, tags: tags, subnetId: subnet.id, targetId: workspace.id, groupId: 'amlworkspace', dnsZoneIds: [zones[1].id,zones[2].id] }
}
module blobEndpoint './modules/private-endpoint.bicep' = {
  name: 'ml-learning-blob-endpoint'
  params: { name: 'pep-iyqpis-ml-blob', location: location, tags: tags, subnetId: subnet.id, targetId: storage.id, groupId: 'blob', dnsZoneIds: [blobZone.id] }
}
module fileEndpoint './modules/private-endpoint.bicep' = {
  name: 'ml-learning-file-endpoint'
  params: { name: 'pep-iyqpis-ml-file', location: location, tags: tags, subnetId: subnet.id, targetId: storage.id, groupId: 'file', dnsZoneIds: [zones[0].id] }
}
// Registry association, RBAC acceptance, operator access and job compute are separate
// reviewed steps. This template alone is not a complete or usable learning deployment.
