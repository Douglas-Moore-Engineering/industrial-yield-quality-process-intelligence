targetScope = 'resourceGroup'
param location string = 'eastus2'
param workspaceName string = 'log-iyqpis-dev'
param actionGroupName string = 'ag-iyqpis-dev-operations'
param jobName string = 'job-iyqpis-dev-data'
resource workspace 'Microsoft.OperationalInsights/workspaces@2025-02-01' existing = { name: workspaceName }
resource notifications 'Microsoft.Insights/actionGroups@2023-01-01' existing = { name: actionGroupName }

var failures = '''
ContainerAppSystemLogs
| where JobName startswith '__JOB__'
| where Reason has_any ('Failed', 'BackoffLimitExceeded', 'DeadlineExceeded', 'ImagePullBackOff', 'ErrImagePull') or Log has_any ('Job execution failed', 'BackoffLimitExceeded', 'DeadlineExceeded')
| project TimeGenerated, JobName, Reason, Log
'''
var quality = '''
ContainerAppConsoleLogs
| where JobName startswith '__JOB__'
| extend event = parse_json(Log)
| where tostring(event.event_type) == 'iyqpis_monitoring'
| where tostring(event.status) == 'failed' or tostring(event.data_quality_passed) == 'false' or tostring(event.performance_passed) == 'false' or tostring(event.drift_review_required) == 'true'
| project TimeGenerated, JobName, Log
'''
var rules = [
  { name: 'job-failure', query: replace(failures, '__JOB__', jobName), description: 'Job failure and startup failure detection; verify against real platform failure logs.' }
  { name: 'model-data-health', query: replace(quality, '__JOB__', jobName), description: 'Structured model, data quality and drift review signals. Drift threshold is provisional reference-only.' }
]
resource alerts 'Microsoft.Insights/scheduledQueryRules@2023-12-01' = [for rule in rules: {
  name: 'alert-iyqpis-dev-${rule.name}'
  location: location
  kind: 'LogAlert'
  properties: {
    displayName: 'IYQPIS ${rule.name}'
    description: rule.description
    enabled: true
    severity: 2
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    scopes: [workspace.id]
    criteria: { allOf: [{
      query: rule.query
      timeAggregation: 'Count'
      operator: 'GreaterThan'
      threshold: 0
      failingPeriods: { numberOfEvaluationPeriods: 1, minFailingPeriodsToAlert: 1 }
    }] }
    autoMitigate: true
    actions: { actionGroups: [notifications.id] }
    skipQueryValidation: false
  }
}]
resource workbook 'Microsoft.Insights/workbooks@2022-04-01' = {
  name: guid(resourceGroup().id, 'iyqpis-reference-operations')
  location: location
  kind: 'shared'
  properties: {
    displayName: 'IYQPIS Reference Operations'
    category: 'workbook'
    sourceId: workspace.id
    serializedData: string({
      version: 'Notebook/1.0'
      items: [
        { type: 1, content: { json: '# IYQPIS Reference Operations\nOn-demand execution: no events means no observation, not healthy live production. Drift is a review signal; performance requires labels. Production release remains blocked.' }, name: 'scope' }
        { type: 3, content: { version: 'KqlItem/1.0', query: 'ContainerAppSystemLogs | where JobName startswith "${jobName}" | project TimeGenerated, JobName, Reason, Log | order by TimeGenerated desc', size: 0, title: 'Job events', queryType: 0, resourceType: 'microsoft.operationalinsights/workspaces', crossComponentResources: [workspace.id], timeContext: { durationMs: 86400000 } }, name: 'jobs' }
        { type: 3, content: { version: 'KqlItem/1.0', query: 'ContainerAppConsoleLogs | where JobName startswith "${jobName}" | extend event=parse_json(Log) | where tostring(event.event_type)=="iyqpis_monitoring" | project TimeGenerated, JobName, event | order by TimeGenerated desc', size: 0, title: 'Data, model and drift observations', queryType: 0, resourceType: 'microsoft.operationalinsights/workspaces', crossComponentResources: [workspace.id], timeContext: { durationMs: 86400000 } }, name: 'model' }
      ]
      isLocked: false
    })
  }
}
