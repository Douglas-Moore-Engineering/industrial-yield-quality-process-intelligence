[CmdletBinding()]
param(
    [ValidateSet('Validate', 'Preview', 'Deploy')]
    [string]$Action = 'Validate',
    [ValidateSet('Foundation', 'Operations')]
    [string]$TemplateSet = 'Foundation',
    [string]$ParametersFile = '',
    [string]$ContextFile = "$PSScriptRoot/context.local.json",
    [switch]$ApproveDeployment
)
$ErrorActionPreference = 'Stop'
$template = Join-Path $PSScriptRoot $(if ($TemplateSet -eq 'Operations') { '../operations.bicep' } else { '../main.bicep' })
if ([string]::IsNullOrWhiteSpace($ParametersFile)) {
    $ParametersFile = Join-Path $PSScriptRoot $(if ($TemplateSet -eq 'Operations') { 'operations.parameters.example.json' } else { 'dev.parameters.example.json' })
}

function Invoke-AzChecked {
    param([string[]]$Arguments)
    $result = & az @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Azure CLI failed: $($Arguments[0..1] -join ' ')" }
    return $result
}

$compiled = Join-Path ([IO.Path]::GetTempPath()) ('iyqpis-' + [guid]::NewGuid() + '.json')
try {
    Invoke-AzChecked -Arguments @('bicep', 'build', '--file', $template, '--outfile', $compiled)
    if ($Action -eq 'Validate') {
        Write-Output 'Bicep compilation passed. Run Checkov separately; no Azure changes made.'
        return
    }

    if (-not (Test-Path -LiteralPath $ContextFile)) {
        throw 'Missing local Azure context. Copy context.example.json to context.local.json and set the approved target.'
    }
    $context = Get-Content -LiteralPath $ContextFile -Raw | ConvertFrom-Json
    foreach ($field in @('subscriptionId', 'tenantId', 'accountEmail')) {
        if ([string]::IsNullOrWhiteSpace($context.$field) -or $context.$field -like '*REPLACE*') {
            throw 'Invalid local Azure context. Set all target fields before cloud operations.'
        }
    }
    $subscriptionId = $context.subscriptionId
    $tenantId = $context.tenantId
    $accountEmail = $context.accountEmail
    $account = (Invoke-AzChecked -Arguments @('account', 'show', '--output', 'json')) | ConvertFrom-Json
    if ($account.id -ne $subscriptionId -or $account.tenantId -ne $tenantId -or $account.user.name -ne $accountEmail) {
        throw 'Wrong Azure context. Sign in to the target defined in your local configuration. No deployment attempted.'
    }
    $parameterPath = (Resolve-Path -LiteralPath $ParametersFile).Path
    $parameters = (Get-Content -LiteralPath $parameterPath -Raw | ConvertFrom-Json).parameters
    if ($TemplateSet -eq 'Operations') {
        if ([string]::IsNullOrWhiteSpace($parameters.alertEmail.value) -or $parameters.alertEmail.value -like '*REPLACE*') { throw 'Set an approved alert recipient in local operations parameters.' }
        if ($parameters.monthlyBudget.value -lt 1) { throw 'Set a positive monthly budget.' }
        if ($parameters.budgetStartDate.value -notmatch '^\d{4}-\d{2}-01T00:00:00Z$') { throw 'Budget start must be the first of a month in UTC.' }
        if ($parameters.stem.value -notin @('iyqpis-dev','iyqpis-test') -or $parameters.platformResourceGroupName.value -ne "rg-$($parameters.stem.value)-platform") { throw 'Operations target must be the dev/test platform resource group.' }
        $deploymentName = "$($parameters.stem.value)-operations"
    } else {
        if ($parameters.costCenter.value -eq 'REPLACE-ME') { throw 'Set an approved costCenter in a copied parameter file.' }
        $deploymentName = "iyqpis-$($parameters.environment.value)-platform"
    }
    if ($parameters.environment.value -eq 'prod') {
        throw 'Production is gated by governance/pre_azure_gate_status.md; this bootstrap script supports dev/test only.'
    }
    $deployArgs = @('--subscription', $subscriptionId, '--location', $parameters.location.value,
        '--name', $deploymentName, '--template-file', $compiled,
        '--parameters', "@$parameterPath")
    Invoke-AzChecked -Arguments (@('deployment', 'sub', 'validate') + $deployArgs)
    Invoke-AzChecked -Arguments (@('deployment', 'sub', 'what-if') + $deployArgs)
    if ($Action -eq 'Deploy') {
        if (-not $ApproveDeployment) { throw 'Review Preview output and explicitly pass -ApproveDeployment to create billable resources.' }
        Invoke-AzChecked -Arguments (@('deployment', 'sub', 'create') + $deployArgs)
    }
} finally {
    if (Test-Path -LiteralPath $compiled) { Remove-Item -LiteralPath $compiled }
}
