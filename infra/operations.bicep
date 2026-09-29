targetScope = 'subscription'

@description('Existing platform resource group. No foundation resources are recreated.')
param platformResourceGroupName string
@description('Existing platform naming stem.')
param stem string = 'iyqpis-dev'
@description('Region for regional identity resources.')
param location string = 'eastus2'
@description('Alert recipients supplied through ignored local settings or an encrypted CI secret.')
@secure()
param alertEmail string
@description('Monthly resource-group budget in the subscription billing currency; not a spending cap.')
@minValue(1)
param monthlyBudget int = 100
@description('First day of the budget start month, in ISO format. Keep stable on redeploy.')
param budgetStartDate string
@description('Exact verified GitHub OIDC subject. Empty means no federated access or deployment role.')
@secure()
param githubSubject string = ''

resource platform 'Microsoft.Resources/resourceGroups@2024-03-01' existing = {
  name: platformResourceGroupName
}
resource logs 'Microsoft.OperationalInsights/workspaces@2025-02-01' existing = {
  scope: platform
  name: 'log-${stem}'
}

module operations './modules/operations.bicep' = {
  name: '${stem}-operations'
  scope: platform
  params: {
    stem: stem
    location: location
    alertEmail: alertEmail
    monthlyBudget: monthlyBudget
    budgetStartDate: budgetStartDate
    githubSubject: githubSubject
  }
}

// Activity Log export is subscription-scoped; it retains subscription administrative
// evidence in the existing private workspace without changing workspace networking.
resource activityExport 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: '${stem}-activity-log'
  properties: {
    workspaceId: logs.id
    logs: [for category in ['Administrative', 'Security', 'ServiceHealth', 'Alert', 'Recommendation', 'Policy', 'Autoscale', 'ResourceHealth']: {
      category: category
      enabled: true
    }]
  }
}
