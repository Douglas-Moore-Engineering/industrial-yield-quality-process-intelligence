@description('Existing platform naming stem.')
param stem string
@description('Region for the identity.')
param location string
@description('Approved alert recipients. Never place real addresses in source.')
@secure()
param alertEmail string
@description('Monthly budget in billing currency.')
param monthlyBudget int
@description('Stable budget start date.')
param budgetStartDate string
@description('Verified OIDC subject; empty disables federation and deployment permission.')
@secure()
param githubSubject string

var tags = { workload: 'iyqpis', scope: 'platform-only', managedBy: 'bicep' }

resource notifications 'Microsoft.Insights/actionGroups@2023-01-01' = {
  name: 'ag-${stem}-operations'
  location: 'global'
  tags: tags
  properties: {
    groupShortName: 'iyqpis-ops'
    enabled: true
    emailReceivers: [for (email, i) in [alertEmail]: {
      name: 'operator-${i}'
      emailAddress: email
      useCommonAlertSchema: true
    }]
  }
}

resource budget 'Microsoft.Consumption/budgets@2024-08-01' = {
  name: 'budget-${stem}'
  properties: {
    amount: monthlyBudget
    category: 'Cost'
    timeGrain: 'Monthly'
    timePeriod: { startDate: budgetStartDate }
    notifications: {
      actual50: { enabled: true, operator: 'GreaterThanOrEqualTo', threshold: 50, thresholdType: 'Actual', contactEmails: [alertEmail] }
      actual80: { enabled: true, operator: 'GreaterThanOrEqualTo', threshold: 80, thresholdType: 'Actual', contactEmails: [alertEmail] }
      actual100: { enabled: true, operator: 'GreaterThanOrEqualTo', threshold: 100, thresholdType: 'Actual', contactEmails: [alertEmail] }
      forecast100: { enabled: true, operator: 'GreaterThanOrEqualTo', threshold: 100, thresholdType: 'Forecasted', contactEmails: [alertEmail] }
    }
  }
}

var alertDefinitions = [
  {
    name: 'failed-operations'
    scope: resourceGroup().id
    conditions: [{ field: 'category', equals: 'Administrative' }, { field: 'status', equals: 'Failed' }]
    description: 'Failed Azure management operation within the platform resource group.'
  }
  {
    name: 'resource-health'
    scope: resourceGroup().id
    conditions: [{ field: 'category', equals: 'ResourceHealth' }, { anyOf: [{ field: 'properties.currentHealthStatus', equals: 'Degraded' }, { field: 'properties.currentHealthStatus', equals: 'Unavailable' }] }]
    description: 'Platform resource degraded or unavailable.'
  }
  {
    name: 'service-health'
    scope: subscription().id
    conditions: [{ field: 'category', equals: 'ServiceHealth' }]
    description: 'Azure Service Health events affecting this subscription.'
  }
  {
    name: 'access-changes'
    scope: resourceGroup().id
    conditions: [{ field: 'category', equals: 'Administrative' }, { field: 'status', equals: 'Succeeded' }, { anyOf: [{ field: 'operationName', equals: 'Microsoft.Authorization/roleAssignments/write' }, { field: 'operationName', equals: 'Microsoft.Authorization/roleAssignments/delete' }] }]
    description: 'Successful role assignment changes in the platform resource group.'
  }
]
resource alerts 'Microsoft.Insights/activityLogAlerts@2020-10-01' = [for alert in alertDefinitions: {
  name: 'alert-${stem}-${alert.name}'
  location: 'global'
  tags: tags
  properties: {
    enabled: true
    scopes: [alert.scope]
    description: alert.description
    condition: { allOf: alert.conditions }
    actions: { actionGroups: [{ actionGroupId: notifications.id }] }
  }
}]

resource deployer 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  name: 'id-${stem}-deployer'
  location: location
  tags: tags
}
resource federation 'Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials@2024-11-30' = if (!empty(githubSubject)) {
  parent: deployer
  name: 'github-platform-dev'
  properties: {
    issuer: 'https://token.actions.githubusercontent.com'
    subject: githubSubject
    audiences: ['api://AzureADTokenExchange']
  }
}
// Foundation updates only; no role assignment rights, no subscription-wide rights.
resource deployRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(githubSubject)) {
  name: guid(resourceGroup().id, deployer.id, 'Contributor')
  properties: {
    principalId: deployer.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b24988ac-6180-42a0-ab88-20f7382dd24c')
  }
}
