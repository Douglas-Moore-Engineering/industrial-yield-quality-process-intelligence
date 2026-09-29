param location string
param stem string
param subnetPrefix string
param endpointPrefix string

var httpsDestinations = ['MicrosoftContainerRegistry', 'AzureFrontDoor.FirstParty', 'AzureActiveDirectory', 'AzureMonitor', 'Storage.${location}', endpointPrefix]
var httpsRules = [for (destination, i) in httpsDestinations: {
      name: 'HttpsDependency${i}'
      properties: {
        priority: 100 + i
        direction: 'Outbound'
        access: 'Allow'
        protocol: 'Tcp'
        sourceAddressPrefix: subnetPrefix
        sourcePortRange: '*'
        destinationAddressPrefix: destination
        destinationPortRange: '443'
      }
    }]
var intraRules = [for (direction, i) in ['Inbound', 'Outbound']: {
      name: 'IntraSubnet${direction}'
      properties: {
        priority: 200 + i
        direction: direction
        access: 'Allow'
        protocol: '*'
        sourceAddressPrefix: subnetPrefix
        sourcePortRange: '*'
        destinationAddressPrefix: subnetPrefix
        destinationPortRange: '*'
      }
    }]
var serviceRules = [{
      name: 'AzureDns'
      properties: {
        priority: 210
        direction: 'Outbound'
        access: 'Allow'
        protocol: '*'
        sourceAddressPrefix: subnetPrefix
        sourcePortRange: '*'
        destinationAddressPrefix: '168.63.129.16'
        destinationPortRange: '53'
      }
    }, {
      name: 'LoadBalancerProbes'
      properties: {
        priority: 220
        direction: 'Inbound'
        access: 'Allow'
        protocol: 'Tcp'
        sourceAddressPrefix: 'AzureLoadBalancer'
        sourcePortRange: '*'
        destinationAddressPrefix: subnetPrefix
        destinationPortRange: '30000-32767'
      }
    }]
var denyRules = [for direction in ['Inbound', 'Outbound']: {
      name: 'DenyOther${direction}'
      properties: {
        priority: 4000
        direction: direction
        access: 'Deny'
        protocol: '*'
        sourceAddressPrefix: '*'
        sourcePortRange: '*'
        destinationAddressPrefix: '*'
        destinationPortRange: '*'
      }
    }]
resource nsg 'Microsoft.Network/networkSecurityGroups@2024-07-01' = {
  name: 'nsg-${stem}-data-jobs'
  location: location
  properties: {
    securityRules: concat(httpsRules, intraRules, serviceRules, denyRules)
  }
}
output id string = nsg.id
