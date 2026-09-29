targetScope = 'resourceGroup'

@description('Existing environment; production requires a separate approved release process.')
@allowed(['dev', 'test'])
param environment string = 'dev'
@description('Existing Azure region.')
param location string = 'eastus2'
@description('Accountable team.')
param owner string = 'platform-engineering'
@description('Approved cost allocation.')
param costCenter string = 'platform-engineering'
@description('Existing network CIDR.')
param vnetAddressPrefix string = '10.80.0.0/16'
@description('Existing private endpoint subnet CIDR.')
param endpointSubnetPrefix string = '10.80.0.0/24'
@description('Existing reserved runner subnet CIDR.')
param runnerSubnetPrefix string = '10.80.1.0/24'
@description('Preserve the approved data-job subnet after activation; empty before activation.')
param dataJobSubnetPrefix string = ''
@description('Existing approved log retention.')
@minValue(30)
@maxValue(730)
param logRetentionDays int = 30

module foundation './modules/foundation.bicep' = {
  name: 'iyqpis-${environment}-foundation'
  params: {
    location: location
    stem: 'iyqpis-${environment}'
    tags: { workload: 'iyqpis', environment: environment, owner: owner, costCenter: costCenter, managedBy: 'bicep', scope: 'platform-only' }
    vnetAddressPrefix: vnetAddressPrefix
    endpointSubnetPrefix: endpointSubnetPrefix
    runnerSubnetPrefix: runnerSubnetPrefix
    dataJobSubnetPrefix: dataJobSubnetPrefix
    logRetentionDays: logRetentionDays
    manageRoleAssignments: false
  }
}
