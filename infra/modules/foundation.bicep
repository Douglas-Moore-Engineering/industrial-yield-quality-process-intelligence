@description('Azure region.')
param location string
@description('Stable workload/environment name prefix.')
param stem string
@description('Required governance tags.')
param tags object
@description('Isolated virtual network CIDR.')
param vnetAddressPrefix string
@description('Dedicated private endpoint CIDR.')
param endpointSubnetPrefix string
@description('Reserved build runner CIDR.')
param runnerSubnetPrefix string
@description('Optional delegated data-job CIDR, retained on future foundation updates.')
param dataJobSubnetPrefix string = ''
@description('Approved Log Analytics retention.')
param logRetentionDays int

@description('Bootstrap role assignments require an operator. Routine CI preserves existing grants.')
param manageRoleAssignments bool = true

var suffix = uniqueString(subscription().subscriptionId, resourceGroup().id)
var dnsNames = [
  'privatelink.vaultcore.azure.net'
  'privatelink.azurecr.io'
  'privatelink.monitor.azure.com'
  'privatelink.oms.opinsights.azure.com'
  'privatelink.ods.opinsights.azure.com'
  'privatelink.agentsvc.azure-automation.net'
  'privatelink.blob.${environment().suffixes.storage}'
  'privatelink.dfs.${environment().suffixes.storage}'
]
// Data zones per docs/04-data-architecture-and-digital-thread.md#data-zones; feature/model-ready and ML default storage are deliberately out of scope here.
var dataLakeContainers = ['raw', 'validated', 'contextualized', 'curated-evidence']

resource endpointNsg 'Microsoft.Network/networkSecurityGroups@2024-07-01' = {
  name: 'nsg-${stem}-endpoints'
  location: location
  tags: tags
  properties: {
    securityRules: concat([
      {
        name: 'AllowRunnerHttps'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: runnerSubnetPrefix
          sourcePortRange: '*'
          destinationAddressPrefix: endpointSubnetPrefix
          destinationPortRange: '443'
        }
      }
      {
        name: 'DenyOtherInbound'
        properties: {
          priority: 4000
          direction: 'Inbound'
          access: 'Deny'
          protocol: '*'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
    ], empty(dataJobSubnetPrefix) ? [] : [{
      name: 'AllowDataJobHttps'
      properties: {
        priority: 120
        direction: 'Inbound'
        access: 'Allow'
        protocol: 'Tcp'
        sourceAddressPrefix: dataJobSubnetPrefix
        sourcePortRange: '*'
        destinationAddressPrefix: endpointSubnetPrefix
        destinationPortRange: '443'
      }
    }])
  }
}

resource runnerNsg 'Microsoft.Network/networkSecurityGroups@2024-07-01' = {
  name: 'nsg-${stem}-runners'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'DenyInbound'
        properties: {
          priority: 4000
          direction: 'Inbound'
          access: 'Deny'
          protocol: '*'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
      {
        name: 'AllowPrivateHttps'
        properties: {
          priority: 100
          direction: 'Outbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: endpointSubnetPrefix
          destinationPortRange: '443'
        }
      }
      {
        name: 'AllowAzureDns'
        properties: {
          priority: 110
          direction: 'Outbound'
          access: 'Allow'
          protocol: '*'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '168.63.129.16'
          destinationPortRange: '53'
        }
      }
      {
        name: 'DenyOtherOutbound'
        properties: {
          priority: 4000
          direction: 'Outbound'
          access: 'Deny'
          protocol: '*'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
    ]
  }
}

module dataJobNsg './data-job-nsg.bicep' = if (!empty(dataJobSubnetPrefix)) {
  name: '${stem}-data-job-nsg'
  params: { location: location, stem: stem, subnetPrefix: dataJobSubnetPrefix, endpointPrefix: endpointSubnetPrefix }
}

resource vnet 'Microsoft.Network/virtualNetworks@2024-07-01' = {
  name: 'vnet-${stem}'
  location: location
  tags: tags
  properties: {
    addressSpace: { addressPrefixes: [vnetAddressPrefix] }
    subnets: concat([
      {
        name: 'snet-private-endpoints'
        properties: {
          addressPrefix: endpointSubnetPrefix
          privateEndpointNetworkPolicies: 'Enabled'
          networkSecurityGroup: { id: endpointNsg.id }
          defaultOutboundAccess: false
        }
      }
      {
        name: 'snet-runners'
        properties: {
          addressPrefix: runnerSubnetPrefix
          networkSecurityGroup: { id: runnerNsg.id }
          defaultOutboundAccess: false
        }
      }
    ], empty(dataJobSubnetPrefix) ? [] : [{
      name: 'snet-data-jobs'
      properties: {
        addressPrefix: dataJobSubnetPrefix
        networkSecurityGroup: { id: dataJobNsg!.outputs.id }
        delegations: [{ name: 'container-apps', properties: { serviceName: 'Microsoft.App/environments' } }]
      }
    }])
  }
}

resource zones 'Microsoft.Network/privateDnsZones@2024-06-01' = [for zone in dnsNames: {
  name: zone
  location: 'global'
  tags: tags
}]

resource links 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = [for (zone, i) in dnsNames: {
  parent: zones[i]
  name: 'link-${stem}'
  location: 'global'
  tags: tags
  properties: {
    registrationEnabled: false
    virtualNetwork: { id: vnet.id }
  }
}]

resource logs 'Microsoft.OperationalInsights/workspaces@2025-02-01' = {
  name: 'log-${stem}'
  location: location
  tags: tags
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: logRetentionDays
    publicNetworkAccessForIngestion: 'Disabled'
    publicNetworkAccessForQuery: 'Disabled'
    features: { disableLocalAuth: true }
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-${stem}'
  location: location
  kind: 'web'
  tags: tags
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logs.id
    DisableLocalAuth: true
    publicNetworkAccessForIngestion: 'Disabled'
    publicNetworkAccessForQuery: 'Disabled'
  }
}

resource monitorScope 'Microsoft.Insights/privateLinkScopes@2021-07-01-preview' = {
  name: 'ampls-${stem}'
  location: 'global'
  tags: tags
  properties: {
    accessModeSettings: {
      ingestionAccessMode: 'PrivateOnly'
      queryAccessMode: 'PrivateOnly'
    }
  }
}

resource scopedLogs 'Microsoft.Insights/privateLinkScopes/scopedResources@2021-07-01-preview' = {
  parent: monitorScope
  name: 'workspace'
  properties: { linkedResourceId: logs.id }
}

resource scopedInsights 'Microsoft.Insights/privateLinkScopes/scopedResources@2021-07-01-preview' = {
  parent: monitorScope
  name: 'application-insights'
  properties: { linkedResourceId: appInsights.id }
}

resource vault 'Microsoft.KeyVault/vaults@2024-11-01' = {
  name: 'kv-${suffix}'
  location: location
  tags: tags
  properties: {
    tenantId: tenant().tenantId
    sku: { family: 'A', name: 'standard' }
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enablePurgeProtection: true
    publicNetworkAccess: 'Disabled'
    networkAcls: { defaultAction: 'Deny', bypass: 'None' }
  }
}

// Quarantine requires a scanner/release identity and promotion workflow; no images are deployed in this foundation.
resource registry 'Microsoft.ContainerRegistry/registries@2025-04-01' = {
  //checkov:skip=CKV_AZURE_166:Quarantine deferred until a scan-and-release pipeline exists; see infra/azure/README.md.
  name: 'cr${suffix}'
  location: location
  tags: tags
  sku: { name: 'Premium' }
  properties: {
    adminUserEnabled: false
    anonymousPullEnabled: false
    publicNetworkAccess: 'Disabled'
    networkRuleBypassOptions: 'None'
    networkRuleSet: { defaultAction: 'Deny' }
    policies: {
      retentionPolicy: { status: 'enabled', days: 30 }
    }
  }
}

resource publisher 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  name: 'id-${stem}-publisher'
  location: location
  tags: tags
}

resource runtime 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  name: 'id-${stem}-runtime'
  location: location
  tags: tags
}

// Data Lake Gen2: hierarchical namespace, private-only. Kept separate from any future ML workspace default storage.
resource dataLake 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  //checkov:skip=CKV_AZURE_43:Name is a deterministic lowercase-alphanumeric uniqueString() expression; static analysis cannot evaluate the interpolation.
  //checkov:skip=CKV_AZURE_206:Geo-redundancy (GRS/RAGRS/GZRS) is a production DR decision gated by the pending RPO/RTO approval in infra/azure/OPERATIONS.md; this holds fully recreatable public/synthetic sample data. ZRS gives regional HA in the interim.
  name: 'st${suffix}'
  location: location
  tags: tags
  sku: { name: 'Standard_ZRS' }
  kind: 'StorageV2'
  properties: {
    isHnsEnabled: true
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    defaultToOAuthAuthentication: true
    publicNetworkAccess: 'Disabled'
    networkAcls: { defaultAction: 'Deny', bypass: 'AzureServices' }
  }
}

resource dataLakeBlobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: dataLake
  name: 'default'
}

resource dataLakeContainerResources 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = [for name in dataLakeContainers: {
  parent: dataLakeBlobService
  name: name
  properties: { publicAccess: 'None' }
}]

resource dataLakePublishRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (manageRoleAssignments) {
  name: guid(dataLake.id, publisher.id, 'StorageBlobDataContributor')
  scope: dataLake
  properties: {
    principalId: publisher.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  }
}

resource dataLakeReadRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (manageRoleAssignments) {
  name: guid(dataLake.id, runtime.id, 'StorageBlobDataReader')
  scope: dataLake
  properties: {
    principalId: runtime.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1')
  }
}

resource publishRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (manageRoleAssignments) {
  name: guid(registry.id, publisher.id, 'AcrPush')
  scope: registry
  properties: {
    principalId: publisher.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '8311e382-0749-4cb8-b61a-304f252e45ec')
  }
}

resource pullRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (manageRoleAssignments) {
  name: guid(registry.id, runtime.id, 'AcrPull')
  scope: registry
  properties: {
    principalId: runtime.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
  }
}

resource vaultDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'platform-logs'
  scope: vault
  properties: {
    workspaceId: logs.id
    logs: [{ categoryGroup: 'allLogs', enabled: true }]
    metrics: [{ category: 'AllMetrics', enabled: true }]
  }
}

resource registryDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'platform-logs'
  scope: registry
  properties: {
    workspaceId: logs.id
    logs: [{ categoryGroup: 'allLogs', enabled: true }]
    metrics: [{ category: 'AllMetrics', enabled: true }]
  }
}

resource dataLakeDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'platform-logs'
  scope: dataLakeBlobService
  properties: {
    workspaceId: logs.id
    logs: [{ categoryGroup: 'allLogs', enabled: true }]
    metrics: [{ category: 'Transaction', enabled: true }]
  }
}

module vaultEndpoint './private-endpoint.bicep' = {
  name: 'vault-endpoint'
  params: {
    name: 'pep-${stem}-vault'
    location: location
    tags: tags
    subnetId: resourceId('Microsoft.Network/virtualNetworks/subnets', vnet.name, 'snet-private-endpoints')
    targetId: vault.id
    groupId: 'vault'
    dnsZoneIds: [zones[0].id]
  }
}

module registryEndpoint './private-endpoint.bicep' = {
  name: 'registry-endpoint'
  params: {
    name: 'pep-${stem}-registry'
    location: location
    tags: tags
    subnetId: resourceId('Microsoft.Network/virtualNetworks/subnets', vnet.name, 'snet-private-endpoints')
    targetId: registry.id
    groupId: 'registry'
    dnsZoneIds: [zones[1].id]
  }
}

module monitorEndpoint './private-endpoint.bicep' = {
  name: 'monitor-endpoint'
  params: {
    name: 'pep-${stem}-monitor'
    location: location
    tags: tags
    subnetId: resourceId('Microsoft.Network/virtualNetworks/subnets', vnet.name, 'snet-private-endpoints')
    targetId: monitorScope.id
    groupId: 'azuremonitor'
    dnsZoneIds: [for i in range(2, 5): zones[i].id]
  }
  dependsOn: [scopedLogs, scopedInsights]
}

module dataLakeBlobEndpoint './private-endpoint.bicep' = {
  name: 'datalake-blob-endpoint'
  params: {
    name: 'pep-${stem}-datalake-blob'
    location: location
    tags: tags
    subnetId: resourceId('Microsoft.Network/virtualNetworks/subnets', vnet.name, 'snet-private-endpoints')
    targetId: dataLake.id
    groupId: 'blob'
    dnsZoneIds: [zones[6].id]
  }
}

module dataLakeDfsEndpoint './private-endpoint.bicep' = {
  name: 'datalake-dfs-endpoint'
  params: {
    name: 'pep-${stem}-datalake-dfs'
    location: location
    tags: tags
    subnetId: resourceId('Microsoft.Network/virtualNetworks/subnets', vnet.name, 'snet-private-endpoints')
    targetId: dataLake.id
    groupId: 'dfs'
    dnsZoneIds: [zones[7].id]
  }
}

output resourceIds object = {
  vnet: vnet.id
  keyVault: vault.id
  registry: registry.id
  logAnalytics: logs.id
  applicationInsights: appInsights.id
  publisherIdentity: publisher.id
  runtimeIdentity: runtime.id
  dataLake: dataLake.id
  dataLakeContainers: dataLakeContainers
}
