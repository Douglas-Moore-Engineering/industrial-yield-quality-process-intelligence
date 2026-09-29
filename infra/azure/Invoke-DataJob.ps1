[CmdletBinding()]
param(
    [ValidateSet('Preview','Deploy','Start','Status')][string]$Action = 'Preview',
    [string]$ParametersFile = "$PSScriptRoot/data-job.parameters.local.json",
    [string]$ContextFile = "$PSScriptRoot/context.local.json",
    [ValidateSet('manufacturing-spc','ai4i-2020-predictive-maintenance','bosch-injector-eol','secom','steel-plates-faults')][string[]]$Datasets,
    [switch]$ApproveDeployment,
    [switch]$ApproveRun
)
$ErrorActionPreference = 'Stop'
if ($Action -eq 'Deploy' -and -not $ApproveDeployment) { throw 'Review the job preview and costs, then pass -ApproveDeployment.' }
if ($Action -eq 'Start' -and -not $ApproveRun) { throw 'An execution incurs compute/storage/log charges. Pass -ApproveRun after review.' }
function Read-Az([string[]]$Arguments) {
    $raw = & az @Arguments --only-show-errors -o json
    if ($LASTEXITCODE -ne 0) { throw 'Azure data-job command failed.' }
    return (($raw -join "`n") | ConvertFrom-Json)
}
$context = Get-Content $ContextFile -Raw | ConvertFrom-Json
$account = Read-Az @('account','show')
if ($account.id -ne $context.subscriptionId -or $account.tenantId -ne $context.tenantId -or $account.user.name -ne $context.accountEmail) { throw 'Wrong Azure context.' }
$rg = 'rg-iyqpis-dev-platform'
$name = 'job-iyqpis-dev-data'
if ($Action -in @('Start','Status')) {
    $job = Read-Az @('containerapp','job','show','-g',$rg,'-n',$name)
    if ($job.properties.configuration.triggerType -ne 'Manual' -or ($job.location -replace '\s','') -ne 'eastus2') { throw 'Expected the approved manual development job.' }
    $executions = @(Read-Az @('containerapp','job','execution','list','-g',$rg,'-n',$name))
    if ($Action -eq 'Status') { $executions | Select-Object name,@{n='status';e={$_.properties.status}}; return }
    if (@($executions | Where-Object { $_.properties.status -notin @('Succeeded','Failed','Stopped') }).Count -gt 0) { throw 'A job execution is active or has unresolved status; inspect it before starting another.' }
    $startArguments = @('containerapp','job','start','-g',$rg,'-n',$name)
    if ($Datasets) {
        $container = $job.properties.template.containers | Where-Object name -eq 'data-batch'
        if (-not $container) { throw 'Expected data-batch container.' }
        $datasetVariable = $container.env | Where-Object name -eq 'DATASETS'
        if (-not $datasetVariable) { throw 'Expected DATASETS environment variable.' }
        $datasetVariable.value = $Datasets -join ','
        # JSON is valid YAML; supply the complete template to preserve all settings.
        $overridePath = "$PSScriptRoot/data-execution-template.local.json"
        $job.properties.template | ConvertTo-Json -Depth 40 | Set-Content $overridePath
        $startArguments += @('--yaml', $overridePath)
    }
    $execution = Read-Az $startArguments
    $execution | ConvertTo-Json -Depth 30 | Set-Content "$PSScriptRoot/data-execution.local.json"
    Write-Output 'Manual execution submitted. Use -Action Status to verify completion; submission is not pipeline success.'
    return
}
$p = (Get-Content $ParametersFile -Raw | ConvertFrom-Json).parameters
if ($p.location.value -ne 'eastus2' -or $p.workspaceName.value -ne 'log-iyqpis-dev') { throw 'Expected East US 2 development platform.' }
$expectedSubnet = "/subscriptions/$($context.subscriptionId)/resourceGroups/$rg/providers/Microsoft.Network/virtualNetworks/vnet-iyqpis-dev/subnets/snet-data-jobs"
if ($p.infrastructureSubnetId.value -ne $expectedSubnet) { throw 'Unexpected data-job subnet.' }
$registry = Read-Az @('acr','show','-g',$rg,'-n',$p.registryName.value)
$imagePattern = '^' + [regex]::Escape($registry.loginServer) + '/[a-z0-9/._-]+@sha256:[a-f0-9]{64}$'
if ($p.image.value -notmatch $imagePattern) { throw 'Use an immutable image digest in the existing private registry.' }
$lake = Read-Az @('storage','account','show','-g',$rg,'-n',$p.storageAccountName.value)
if ($lake.publicNetworkAccess -ne 'Disabled' -or $lake.allowSharedKeyAccess -ne $false -or -not $lake.isHnsEnabled -or $registry.publicNetworkAccess -ne 'Disabled') { throw 'Private lake/registry security preflight failed.' }
$subnet = Read-Az @('network','vnet','subnet','show','--ids',$expectedSubnet)
if (@($subnet.delegations | Where-Object serviceName -eq 'Microsoft.App/environments').Count -ne 1) { throw 'Dedicated Container Apps subnet is not ready.' }
$template = Join-Path $PSScriptRoot '../data-job.bicep'
$arguments = @('-g',$rg,'-n','iyqpis-dev-data','--template-file',$template,'--parameters',"@$ParametersFile")
$preview = Read-Az (@('deployment','group','what-if') + $arguments + @('--no-pretty-print'))
$preview | ConvertTo-Json -Depth 80 | Set-Content "$PSScriptRoot/data-job-preview.local.json"
if ($preview.status -ne 'Succeeded' -or @($preview.changes).Count -eq 0 -or @($preview.changes | Where-Object changeType -notin @('Create','NoChange','Ignore')).Count -gt 0 -or @($preview.diagnostics | Where-Object level -in @('Warning','Error')).Count -gt 0) { throw 'Job preview is incomplete or changes existing resources; inspect ignored local preview.' }
$preview.changes | Group-Object changeType | Select-Object Name,Count
if ($Action -eq 'Deploy') {
    $result = Read-Az (@('deployment','group','create') + $arguments + @('--mode','Incremental'))
    $result | ConvertTo-Json -Depth 80 | Set-Content "$PSScriptRoot/data-job-deployment.local.json"
    if ($result.properties.provisioningState -ne 'Succeeded') { throw 'Data-job deployment did not succeed.' }
    Write-Output 'Data-job infrastructure deployed. No execution started.'
}
