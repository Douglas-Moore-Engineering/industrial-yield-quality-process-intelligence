$ErrorActionPreference = 'Stop'
$tempDir = Join-Path ([IO.Path]::GetTempPath()) ('iyqpis-ci-test-' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $tempDir | Out-Null
$parametersPath = Join-Path $tempDir 'parameters.json'
$previewPath = Join-Path $tempDir 'preview.json'
$savedEnv = @{}
foreach ($key in @('GITHUB_REF','GITHUB_EVENT_NAME','AZURE_SUBSCRIPTION_ID','AZURE_TENANT_ID','GITHUB_STEP_SUMMARY')) { $savedEnv[$key] = [Environment]::GetEnvironmentVariable($key) }
$global:iyqpisCiCommands = [Collections.Generic.List[string]]::new()
$global:iyqpisCiPreview = @{status='Succeeded';changes=@(@{changeType='NoChange';resourceId='test-resource'});diagnostics=@()}
function global:az {
    $global:LASTEXITCODE = 0
    $global:iyqpisCiCommands.Add(($args -join ' '))
    if ($args[0] -eq 'account') { @{id='test-subscription';tenantId='test-tenant'} | ConvertTo-Json }
    elseif ($args[2] -eq 'what-if') { $global:iyqpisCiPreview | ConvertTo-Json -Depth 8 }
}
function Expect-Blocked {
    param([string]$Expected)
    $blocked = $false
    try { & "$PSScriptRoot/Invoke-CiDeployment.ps1" -ResourceGroup test -ParametersFile $parametersPath -PreviewFile $previewPath -Apply | Out-Null }
    catch { if ($_.Exception.Message -notlike "*$Expected*") { throw }; $blocked = $true }
    if (-not $blocked) { throw "Expected block: $Expected" }
    if ($global:iyqpisCiCommands | Where-Object { $_ -like 'deployment group create*' }) { throw 'Unsafe preview reached create.' }
    $global:iyqpisCiCommands.Clear()
}
try {
    @{parameters=@{environment=@{value='dev'}}} | ConvertTo-Json -Depth 5 | Set-Content $parametersPath
    $env:AZURE_SUBSCRIPTION_ID='test-subscription'; $env:AZURE_TENANT_ID='test-tenant'; $env:GITHUB_EVENT_NAME='workflow_dispatch'; $env:GITHUB_REF='refs/heads/other'; $env:GITHUB_STEP_SUMMARY=''
    Expect-Blocked 'manual main-branch'
    $env:GITHUB_REF='refs/heads/main'; $env:GITHUB_EVENT_NAME='pull_request'
    Expect-Blocked 'manual main-branch'
    $env:GITHUB_EVENT_NAME='workflow_dispatch'; $env:AZURE_TENANT_ID='wrong'
    Expect-Blocked 'context mismatch'
    $env:AZURE_TENANT_ID='test-tenant'
    foreach ($change in @('Delete','Unsupported','Deploy','Unexpected')) {
        $global:iyqpisCiPreview.changes[0].changeType=$change
        Expect-Blocked 'Destructive or unresolved'
    }
    $global:iyqpisCiPreview.changes[0].changeType='NoChange'
    $global:iyqpisCiPreview.diagnostics=@(@{level='Warning'})
    Expect-Blocked 'completely evaluate'
    $global:iyqpisCiPreview.diagnostics=@()
    & "$PSScriptRoot/Invoke-CiDeployment.ps1" -ResourceGroup test -ParametersFile $parametersPath -PreviewFile $previewPath | Out-Null
    if ($global:iyqpisCiCommands | Where-Object { $_ -like 'deployment group create*' }) { throw 'Preview applied changes.' }
    Write-Output 'PASS: nine CI safety cases (branch, event, context, four unresolved/destructive states, diagnostics, preview-only).'
} finally {
    Remove-Item Function:/az
    foreach ($key in $savedEnv.Keys) { [Environment]::SetEnvironmentVariable($key,$savedEnv[$key]) }
    foreach ($file in @($parametersPath,$previewPath)) { if (Test-Path -LiteralPath $file) { Remove-Item -LiteralPath $file } }
    Remove-Item -LiteralPath $tempDir
}
