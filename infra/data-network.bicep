@description('Region of the existing development VNet.')
param location string = 'eastus2'
@description('New dedicated Container Apps subnet; confirm non-overlap before deployment.')
param dataJobSubnetPrefix string = '10.80.2.0/27'

resource vnet 'Microsoft.Network/virtualNetworks@2024-07-01' existing = { name: 'vnet-iyqpis-dev' }
resource endpoints 'Microsoft.Network/networkSecurityGroups@2024-07-01' existing = { name: 'nsg-iyqpis-dev-endpoints' }
module nsg './modules/data-job-nsg.bicep' = {
  name: 'iyqpis-dev-data-job-nsg'
  params: { location: location, stem: 'iyqpis-dev', subnetPrefix: dataJobSubnetPrefix, endpointPrefix: '10.80.0.0/24' }
}
resource subnet 'Microsoft.Network/virtualNetworks/subnets@2024-07-01' = {
  parent: vnet
  name: 'snet-data-jobs'
  properties: {
    addressPrefix: dataJobSubnetPrefix
    networkSecurityGroup: { id: nsg.outputs.id }
    delegations: [{ name: 'container-apps', properties: { serviceName: 'Microsoft.App/environments' } }]
  }
}
resource endpointAccess 'Microsoft.Network/networkSecurityGroups/securityRules@2024-07-01' = {
  parent: endpoints
  name: 'AllowDataJobHttps'
  properties: {
    priority: 120
    direction: 'Inbound'
    access: 'Allow'
    protocol: 'Tcp'
    sourceAddressPrefix: dataJobSubnetPrefix
    sourcePortRange: '*'
    destinationAddressPrefix: '10.80.0.0/24'
    destinationPortRange: '443'
  }
}
output subnetId string = subnet.id
