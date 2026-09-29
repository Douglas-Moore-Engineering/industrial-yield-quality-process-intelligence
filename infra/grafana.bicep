targetScope = 'resourceGroup'
@allowed(['eastus2'])
param location string = 'eastus2'
param grafanaName string = 'grafana-iyqpis-dev'
@description('Approved operator object ID; supply using ignored local parameters.')
param operatorObjectId string
var tags = { workload: 'iyqpis', purpose: 'temporary-learning', managedBy: 'bicep' }
resource logs 'Microsoft.OperationalInsights/workspaces@2025-02-01' existing = { name: 'log-iyqpis-dev' }
resource monitorScope 'Microsoft.Insights/privateLinkScopes@2021-07-01-preview' existing = { name: 'ampls-iyqpis-dev' }
resource vnet 'Microsoft.Network/virtualNetworks@2024-07-01' existing = { name: 'vnet-iyqpis-dev' }
resource subnet 'Microsoft.Network/virtualNetworks/subnets@2024-07-01' existing = { parent: vnet, name: 'snet-private-endpoints' }
resource grafana 'Microsoft.Dashboard/grafana@2025-08-01' = {
  name: grafanaName
  location: location
  tags: tags
  identity: { type: 'SystemAssigned' }
  sku: { name: 'Standard' }
  properties: {
    publicNetworkAccess: 'Disabled'
    apiKey: 'Disabled'
    zoneRedundancy: 'Disabled'
    deterministicOutboundIP: 'Disabled'
    grafanaConfigurations: { snapshots: { externalEnabled: false } }
  }
}
resource reader 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(logs.id, grafana.id, 'monitoring-reader')
  scope: logs
  properties: {
    principalId: grafana.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions','43d0d8ad-25c7-4714-9337-8ba259a9fe05')
  }
}
resource admin 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(grafana.id, operatorObjectId, 'grafana-admin')
  scope: grafana
  properties: {
    principalId: operatorObjectId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions','22926164-76b3-42b3-bc55-97df8dab3e41')
  }
}
resource sourceEndpoint 'Microsoft.Dashboard/grafana/managedPrivateEndpoints@2025-08-01' = {
  parent: grafana
  name: 'platform-monitor'
  location: location
  properties: {
    privateLinkResourceId: monitorScope.id
    groupIds: ['azuremonitor']
    privateLinkServiceUrl: 'api.loganalytics.io'
    requestMessage: 'Read-only reference platform monitoring through Grafana.'
  }
}
resource zone 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.grafana.azure.com'
  location: 'global'
  tags: tags
}
resource link 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: zone
  name: 'link-iyqpis-grafana'
  location: 'global'
  properties: { registrationEnabled: false, virtualNetwork: { id: vnet.id } }
}
module endpoint './modules/private-endpoint.bicep' = {
  name: 'grafana-private-access'
  params: {
    name: 'pep-iyqpis-grafana'
    location: location
    tags: tags
    subnetId: subnet.id
    targetId: grafana.id
    groupId: 'grafana'
    dnsZoneIds: [zone.id]
  }
}
// Deployment requires subsequent managed endpoint approval/sync, data source
// provisioning, dashboard import and a successful private-client query.
