targetScope = 'resourceGroup'
param storageAccountName string
@minValue(7)
@maxValue(30)
param retentionDays int = 7
resource lake 'Microsoft.Storage/storageAccounts@2023-05-01' existing = { name: storageAccountName }
resource blobs 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: lake
  name: 'default'
  properties: {
    deleteRetentionPolicy: { enabled: true, days: retentionDays, allowPermanentDelete: false }
    containerDeleteRetentionPolicy: { enabled: true, days: retentionDays }
  }
}
