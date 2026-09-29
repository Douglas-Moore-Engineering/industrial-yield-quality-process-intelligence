[CmdletBinding()]
param([string]$ContextFile = "$PSScriptRoot/context.local.json", [string]$ResourceGroup = 'rg-iyqpis-dev-platform', [switch]$IncludeOperations)
$ErrorActionPreference = 'Stop'
if ($ResourceGroup -notmatch '^rg-iyqpis-(dev|test)-platform$') { throw 'Verifier is restricted to the development/test platform.' }
$stem = $ResourceGroup.Substring(3) -replace '-platform$', ''
function Read-AzureJson {
    param([string[]]$Arguments)
    $result = & az @Arguments --output json
    if ($LASTEXITCODE -ne 0) { throw 'Azure verification query failed.' }
    $parsed = ($result -join "`n") | ConvertFrom-Json
    return $parsed
}
function Require { param([bool]$Condition, [string]$Label)
    if (-not $Condition) { throw "FAIL: $Label" }
    Write-Output "PASS: $Label"
}
$context = Get-Content -LiteralPath $ContextFile -Raw | ConvertFrom-Json
$account = Read-AzureJson @('account','show')
Require ($account.id -eq $context.subscriptionId -and $account.tenantId -eq $context.tenantId -and $account.user.name -eq $context.accountEmail) 'Expected local Azure context'
$resources = Read-AzureJson @('resource','list','-g',$ResourceGroup)
$vaultName = ($resources | Where-Object type -eq 'Microsoft.KeyVault/vaults').name
$registryName = ($resources | Where-Object type -eq 'Microsoft.ContainerRegistry/registries').name
$vault = Read-AzureJson @('keyvault','show','-g',$ResourceGroup,'-n',$vaultName)
Require ($vault.properties.publicNetworkAccess -eq 'Disabled' -and $vault.properties.enableRbacAuthorization -and $vault.properties.enablePurgeProtection) 'Key Vault private access, RBAC and purge protection'
$registry = Read-AzureJson @('acr','show','-g',$ResourceGroup,'-n',$registryName)
Require ($registry.publicNetworkAccess -eq 'Disabled' -and -not $registry.adminUserEnabled -and -not $registry.anonymousPullEnabled) 'Registry private access and local authentication disabled'
$endpoints = @(Read-AzureJson @('network','private-endpoint','list','-g',$ResourceGroup))
$requiredEndpoints = @("pep-$stem-registry", "pep-$stem-vault", "pep-$stem-monitor", "pep-$stem-datalake-blob", "pep-$stem-datalake-dfs")
Require (@($requiredEndpoints | Where-Object { $_ -notin $endpoints.name }).Count -eq 0) 'Required foundation private endpoints present'
foreach ($endpoint in $endpoints) {
    Require ($endpoint.provisioningState -eq 'Succeeded' -and @($endpoint.privateLinkServiceConnections | Where-Object { $_.privateLinkServiceConnectionState.status -ne 'Approved' }).Count -eq 0) "Approved endpoint: $($endpoint.name)"
    $groups = @(Read-AzureJson @('network','private-endpoint','dns-zone-group','list','-g',$ResourceGroup,'--endpoint-name',$endpoint.name))
    Require ($groups.Count -eq 1 -and $groups[0].provisioningState -eq 'Succeeded') "DNS association: $($endpoint.name)"
}
$zones = @(Read-AzureJson @('network','private-dns','zone','list','-g',$ResourceGroup))
$requiredZones = @('privatelink.ods.opinsights.azure.com','privatelink.vaultcore.azure.net','privatelink.blob.core.windows.net','privatelink.azurecr.io','privatelink.agentsvc.azure-automation.net','privatelink.oms.opinsights.azure.com','privatelink.monitor.azure.com','privatelink.dfs.core.windows.net')
Require (@($requiredZones | Where-Object { $_ -notin $zones.name }).Count -eq 0) 'Required foundation private DNS zones present'
foreach ($zone in $zones) {
    $links = @(Read-AzureJson @('network','private-dns','link','vnet','list','-g',$ResourceGroup,'-z',$zone.name))
    Require ($links.Count -eq 1 -and $links[0].virtualNetworkLinkState -eq 'Completed') "DNS VNet link: $($zone.name)"
}
$logs = Read-AzureJson @('monitor','log-analytics','workspace','show','-g',$ResourceGroup,'-n',"log-$stem")
Require ($logs.publicNetworkAccessForIngestion -eq 'Disabled' -and $logs.publicNetworkAccessForQuery -eq 'Disabled' -and $logs.features.disableLocalAuth) 'Monitor query/ingestion private and local authentication disabled'
foreach ($resource in @($vault,$registry)) {
    $settings = @(Read-AzureJson @('monitor','diagnostic-settings','list','--resource',$resource.id))
    $configured = @($settings | Where-Object { $_.workspaceId -eq $logs.id -and @($_.logs | Where-Object enabled).Count -gt 0 })
    Require ($configured.Count -gt 0) 'Service diagnostics wired to the platform workspace'
}
$roles = @(Read-AzureJson @('role','assignment','list','--scope',$registry.id))
foreach ($pair in @(@('publisher','AcrPush'),@('runtime','AcrPull'))) {
    $identity = Read-AzureJson @('identity','show','-g',$ResourceGroup,'-n',"id-$stem-$($pair[0])")
    Require (@($roles | Where-Object { $_.principalId -eq $identity.principalId -and $_.roleDefinitionName -eq $pair[1] -and $_.scope -eq $registry.id }).Count -eq 1) "Registry-scoped $($pair[1])"
}
if ($IncludeOperations) {
    $group = Read-AzureJson @('monitor','action-group','show','-g',$ResourceGroup,'-n',"ag-$stem-operations")
    Require ($group.enabled -and $group.location -eq 'global' -and $group.emailReceivers.Count -eq 1 -and $group.emailReceivers[0].emailAddress -eq $context.accountEmail) 'Operations action group and approved recipient configured (delivery not proven)'
    $alerts = @(Read-AzureJson @('monitor','activity-log','alert','list','-g',$ResourceGroup))
    foreach ($suffix in @('failed-operations','resource-health','service-health','access-changes')) {
        $alert = @($alerts | Where-Object name -eq "alert-$stem-$suffix")
        Require ($alert.Count -eq 1 -and $alert[0].enabled -and $alert[0].actions.actionGroups[0].actionGroupId -eq $group.id) "Operational alert enabled and routed: $suffix"
    }
    $scope = "/subscriptions/$($context.subscriptionId)"
    $budget = Read-AzureJson @('rest','--method','get','--url',"https://management.azure.com$scope/resourceGroups/$ResourceGroup/providers/Microsoft.Consumption/budgets/budget-${stem}?api-version=2024-08-01")
    $approved = (Get-Content "$PSScriptRoot/operations.parameters.local.json" -Raw | ConvertFrom-Json).parameters
    Require ($budget.properties.amount -eq $approved.monthlyBudget.value -and $budget.properties.timeGrain -eq 'Monthly') 'Approved monthly budget configured (not a spending cap)'
    foreach ($entry in @(@('actual50',50,'Actual'),@('actual80',80,'Actual'),@('actual100',100,'Actual'),@('forecast100',100,'Forecasted'))) {
        $notification = $budget.properties.notifications.($entry[0])
        Require ($notification.enabled -and $notification.threshold -eq $entry[1] -and $notification.thresholdType -eq $entry[2] -and $notification.contactEmails -contains $approved.alertEmail.value) "Budget notification: $($entry[0])"
    }
    $export = Read-AzureJson @('rest','--method','get','--url',"https://management.azure.com$scope/providers/Microsoft.Insights/diagnosticSettings/${stem}-activity-log?api-version=2021-05-01-preview")
    Require ($export.properties.workspaceId -eq $logs.id -and @($export.properties.logs | Where-Object enabled).Count -eq 8) 'Subscription Activity Log export configured for eight categories (arrival not proven)'
    if ([string]::IsNullOrWhiteSpace($approved.githubSubject.value)) {
        $deployer = Read-AzureJson @('identity','show','-g',$ResourceGroup,'-n',"id-$stem-deployer")
        $trusts = @(Read-AzureJson @('identity','federated-credential','list','-g',$ResourceGroup,'--identity-name',"id-$stem-deployer"))
        $assignments = @(Read-AzureJson @('role','assignment','list','--assignee-object-id',$deployer.principalId,'--all'))
        Require ($trusts.Count -eq 0 -and $assignments.Count -eq 0) 'CI deployment identity has no federation or assigned roles'
    }
    $probes = @($resources | Where-Object { $_.name -like 'probe-*' -or $_.name -like 'shutdown-computevm-probe-*' })
    Require ($probes.Count -eq 0) 'No temporary probe resources remain'
}
Write-Output 'Control-plane verification complete. Private-client DNS/TLS, authorization, log arrival and alert delivery tests are separate.'
