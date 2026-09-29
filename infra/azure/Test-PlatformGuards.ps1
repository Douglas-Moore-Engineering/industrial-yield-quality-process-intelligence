# Exercises deployment safety without Azure login or network calls.
$ErrorActionPreference = 'Stop'
$global:iyqpisTestCommands = [Collections.Generic.List[string]]::new()
$global:iyqpisTestContext = @{
    id = '11111111-1111-1111-1111-111111111111'
    tenantId = '22222222-2222-2222-2222-222222222222'
    user = @{ name = 'engineer@example.com' }
}
function global:az {
    $global:iyqpisTestCommands.Add(($args -join ' '))
    $global:LASTEXITCODE = 0
    if ($args[0] -eq 'account') { $global:iyqpisTestContext | ConvertTo-Json }
}
function Assert-Blocked {
    param([scriptblock]$Operation, [string]$Expected)
    $blocked = $false
    try { & $Operation | Out-Null } catch {
        if ($_.Exception.Message -notlike "*$Expected*") { throw }
        $blocked = $true
    }
    if (-not $blocked) { throw "Expected rejection: $Expected" }
    if ($global:iyqpisTestCommands | Where-Object { $_ -like 'deployment sub create*' }) { throw 'Blocked operation invoked create.' }
    $global:iyqpisTestCommands.Clear()
}
$parameterPath = Join-Path ([IO.Path]::GetTempPath()) ('iyqpis-test-' + [guid]::NewGuid() + '.json')
$contextPath = Join-Path ([IO.Path]::GetTempPath()) ('iyqpis-context-' + [guid]::NewGuid() + '.json')
try {
    @{ subscriptionId = $global:iyqpisTestContext.id; tenantId = $global:iyqpisTestContext.tenantId; accountEmail = $global:iyqpisTestContext.user.name } | ConvertTo-Json | Set-Content -LiteralPath $contextPath
    $parameters = Get-Content "$PSScriptRoot/dev.parameters.example.json" -Raw | ConvertFrom-Json
    $parameters.parameters.costCenter.value = 'test'
    $parameters | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $parameterPath
    $global:iyqpisTestContext.user.name = 'wrong@example.com'
    Assert-Blocked { & "$PSScriptRoot/platform.ps1" -Action Deploy -ParametersFile $parameterPath -ContextFile $contextPath -ApproveDeployment } 'Wrong Azure context'
    $global:iyqpisTestContext.user.name = 'engineer@example.com'
    $global:iyqpisTestContext.id = 'wrong-subscription'
    Assert-Blocked { & "$PSScriptRoot/platform.ps1" -Action Preview -ParametersFile $parameterPath -ContextFile $contextPath } 'Wrong Azure context'
    $global:iyqpisTestContext.id = '11111111-1111-1111-1111-111111111111'
    $global:iyqpisTestContext.tenantId = 'wrong-tenant'
    Assert-Blocked { & "$PSScriptRoot/platform.ps1" -Action Preview -ParametersFile $parameterPath -ContextFile $contextPath } 'Wrong Azure context'
    $global:iyqpisTestContext.tenantId = '22222222-2222-2222-2222-222222222222'
    Assert-Blocked { & "$PSScriptRoot/platform.ps1" -Action Deploy -ParametersFile $parameterPath -ContextFile $contextPath } 'explicitly pass -ApproveDeployment'
    & "$PSScriptRoot/platform.ps1" -Action Preview -ParametersFile $parameterPath -ContextFile $contextPath | Out-Null
    if ($global:iyqpisTestCommands | Where-Object { $_ -like 'deployment sub create*' }) { throw 'Preview invoked create.' }
    if (-not ($global:iyqpisTestCommands | Where-Object { $_ -like 'deployment sub what-if*' })) { throw 'Preview did not invoke what-if.' }
    $global:iyqpisTestCommands.Clear()
    $parameters.parameters.environment.value = 'prod'
    $parameters | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $parameterPath
    Assert-Blocked { & "$PSScriptRoot/platform.ps1" -Action Deploy -ParametersFile $parameterPath -ContextFile $contextPath -ApproveDeployment } 'Production is gated'
    $operations = Get-Content "$PSScriptRoot/operations.parameters.example.json" -Raw | ConvertFrom-Json
    $operations.parameters.budgetStartDate.value = '2026-09-01T00:00:00Z'
    $operations | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $parameterPath
    Assert-Blocked { & "$PSScriptRoot/platform.ps1" -Action Deploy -TemplateSet Operations -ParametersFile $parameterPath -ContextFile $contextPath -ApproveDeployment } 'approved alert recipient'
    $operations.parameters.alertEmail.value = 'operator@example.com'
    $operations.parameters.monthlyBudget.value = 0
    $operations | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $parameterPath
    Assert-Blocked { & "$PSScriptRoot/platform.ps1" -Action Deploy -TemplateSet Operations -ParametersFile $parameterPath -ContextFile $contextPath -ApproveDeployment } 'positive monthly budget'
    $operations.parameters.monthlyBudget.value = 100
    $operations.parameters.budgetStartDate.value = 'invalid'
    $operations | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $parameterPath
    Assert-Blocked { & "$PSScriptRoot/platform.ps1" -Action Deploy -TemplateSet Operations -ParametersFile $parameterPath -ContextFile $contextPath -ApproveDeployment } 'first of a month'
    $operations.parameters.budgetStartDate.value = '2026-09-01T00:00:00Z'
    $operations.parameters.platformResourceGroupName.value = 'rg-unrelated'
    $operations | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $parameterPath
    Assert-Blocked { & "$PSScriptRoot/platform.ps1" -Action Deploy -TemplateSet Operations -ParametersFile $parameterPath -ContextFile $contextPath -ApproveDeployment } 'dev/test platform'
    Remove-Item -LiteralPath $contextPath
    Assert-Blocked { & "$PSScriptRoot/platform.ps1" -Action Preview -ContextFile $contextPath } 'Missing local Azure context'
    @{ subscriptionId = ''; tenantId = 'REPLACE-ME'; accountEmail = '' } | ConvertTo-Json | Set-Content -LiteralPath $contextPath
    Assert-Blocked { & "$PSScriptRoot/platform.ps1" -Action Preview -ContextFile $contextPath } 'Invalid local Azure context'
    Write-Output 'PASS: deployment, local context and operations parameter guards (12 cases).'
} finally {
    Remove-Item -LiteralPath $contextPath -ErrorAction SilentlyContinue
    Remove-Item Function:/az
    Remove-Item -LiteralPath $parameterPath -ErrorAction SilentlyContinue
}
