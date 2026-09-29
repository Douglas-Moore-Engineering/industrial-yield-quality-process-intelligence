targetScope = 'subscription'

@description('Azure region approved for this environment. No production region is assumed.')
param location string

@description('Environment boundary. Use separate subscriptions for production where possible.')
@allowed(['dev', 'test', 'prod'])
param environment string

@description('Named team accountable for this platform.')
@minLength(1)
param owner string

@description('Billing allocation reference.')
@minLength(1)
param costCenter string

@description('Isolated platform address space; review against enterprise and plant networks before connecting.')
param vnetAddressPrefix string = '10.80.0.0/16'

@description('Dedicated private endpoint subnet; sized for Azure Monitor and future endpoints.')
param endpointSubnetPrefix string = '10.80.0.0/24'

@description('Reserved subnet for future privately connected build agents. No agents are installed.')
param runnerSubnetPrefix string = '10.80.1.0/24'

@description('Optional dedicated on-demand data-job subnet. Empty retains the platform-only network. Once enabled, preserve on every redeployment.')
param dataJobSubnetPrefix string = ''

@description('Log retention in days; data owner must approve production retention.')
@minValue(30)
@maxValue(730)
param logRetentionDays int = 30

var stem = 'iyqpis-${environment}'
var tags = {
  workload: 'iyqpis'
  environment: environment
  owner: owner
  costCenter: costCenter
  managedBy: 'bicep'
  scope: 'platform-only'
}

resource platform 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-${stem}-platform'
  location: location
  tags: tags
}

module foundation './modules/foundation.bicep' = {
  name: '${stem}-foundation'
  scope: platform
  params: {
    location: location
    stem: stem
    tags: tags
    vnetAddressPrefix: vnetAddressPrefix
    endpointSubnetPrefix: endpointSubnetPrefix
    runnerSubnetPrefix: runnerSubnetPrefix
    dataJobSubnetPrefix: dataJobSubnetPrefix
    logRetentionDays: logRetentionDays
  }
}

output resourceGroupName string = platform.name
output platformResourceIds object = foundation.outputs.resourceIds
