targetScope = 'resourceGroup'

@description('Region of the existing platform VNet.')
param location string = 'eastus2'
@description('Existing VNet name.')
param vnetName string = 'vnet-iyqpis-dev'
@description('Existing publisher identity name.')
param publisherName string = 'id-iyqpis-dev-publisher'
@description('Existing runtime identity name.')
param runtimeName string = 'id-iyqpis-dev-runtime'
@description('Unique short probe name for deterministic cleanup.')
@maxLength(40)
param probeName string
@description('Temporary public SSH key; no inbound SSH access is provisioned.')
@secure()
param sshPublicKey string
@description('Base64 cloud-init containing the private acceptance test, with no credentials.')
@secure()
param customData string
@description('Small temporary VM size. Verify quota and region availability before running.')
param vmSize string = 'Standard_D2als_v7'
@description('Temporary admin account; SSH remains unreachable from outside the subnet.')
param adminUsername string = 'platformprobe'
@description('UTC HHmm shutdown time, generated as one hour after probe launch. Cleanup still removes disks/NIC.')
param shutdownTime string

resource vnet 'Microsoft.Network/virtualNetworks@2024-07-01' existing = { name: vnetName }
resource publisher 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' existing = { name: publisherName }
resource runtime 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' existing = { name: runtimeName }
resource nic 'Microsoft.Network/networkInterfaces@2024-07-01' = {
  name: '${probeName}-nic'
  location: location
  tags: { workload: 'iyqpis', purpose: 'temporary-platform-acceptance', managedBy: 'bicep' }
  properties: {
    ipConfigurations: [{
      name: 'private'
      properties: {
        privateIPAllocationMethod: 'Dynamic'
        subnet: { id: '${vnet.id}/subnets/snet-runners' }
      }
    }]
  }
}
resource vm 'Microsoft.Compute/virtualMachines@2024-07-01' = {
  name: probeName
  location: location
  tags: { workload: 'iyqpis', purpose: 'temporary-platform-acceptance', managedBy: 'bicep' }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${publisher.id}': {}, '${runtime.id}': {} }
  }
  properties: {
    hardwareProfile: { vmSize: vmSize }
    securityProfile: {
      securityType: 'TrustedLaunch'
      uefiSettings: { secureBootEnabled: true, vTpmEnabled: true }
      encryptionAtHost: true
    }
    storageProfile: {
      imageReference: { publisher: 'Canonical', offer: '0001-com-ubuntu-server-jammy', sku: '22_04-lts-gen2', version: 'latest' }
      osDisk: {
        name: '${probeName}-os'
        createOption: 'FromImage'
        deleteOption: 'Delete'
        managedDisk: { storageAccountType: 'StandardSSD_LRS' }
      }
    }
    networkProfile: { networkInterfaces: [{ id: nic.id, properties: { primary: true, deleteOption: 'Delete' } }] }
    osProfile: {
      allowExtensionOperations: false
      computerName: probeName
      adminUsername: adminUsername
      customData: customData
      linuxConfiguration: {
        disablePasswordAuthentication: true
        ssh: { publicKeys: [{ path: '/home/${adminUsername}/.ssh/authorized_keys', keyData: sshPublicKey }] }
      }
    }
    diagnosticsProfile: { bootDiagnostics: { enabled: true } }
  }
}

resource shutdown 'Microsoft.DevTestLab/schedules@2018-09-15' = {
  name: 'shutdown-computevm-${probeName}'
  location: location
  tags: { workload: 'iyqpis', purpose: 'temporary-platform-acceptance' }
  properties: {
    status: 'Enabled'
    taskType: 'ComputeVmShutdownTask'
    dailyRecurrence: { time: shutdownTime }
    timeZoneId: 'UTC'
    targetResourceId: vm.id
    notificationSettings: { status: 'Disabled', timeInMinutes: 30 }
  }
}
