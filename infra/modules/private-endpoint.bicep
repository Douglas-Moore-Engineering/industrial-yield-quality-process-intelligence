@description('Endpoint name.')
param name string
@description('Azure region.')
param location string
@description('Governance tags.')
param tags object
@description('Dedicated endpoint subnet resource ID.')
param subnetId string
@description('Private Link target resource ID.')
param targetId string
@description('Service-specific Private Link group.')
param groupId string
@description('Existing private DNS zone IDs to associate with the endpoint.')
param dnsZoneIds array

resource endpoint 'Microsoft.Network/privateEndpoints@2024-07-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    subnet: { id: subnetId }
    privateLinkServiceConnections: [
      {
        name: '${name}-connection'
        properties: {
          privateLinkServiceId: targetId
          groupIds: [groupId]
        }
      }
    ]
  }
}

resource zoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-07-01' = {
  parent: endpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [for (zoneId, i) in dnsZoneIds: {
      name: 'zone-${i}'
      properties: { privateDnsZoneId: zoneId }
    }]
  }
}
