[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ResourceGroup,
    [Parameter(Mandatory)][string]$ParametersFile,
    [Parameter(Mandatory)][string]$PreviewFile,
    [switch]$Apply
)
$ErrorActionPreference = 'Stop'
if ($env:GITHUB_REF -ne 'refs/heads/main' -or $env:GITHUB_EVENT_NAME -ne 'workflow_dispatch') {
    throw 'CI deployment requires a manual main-branch workflow.'
}
if ([string]::IsNullOrWhiteSpace($env:AZURE_SUBSCRIPTION_ID) -or [string]::IsNullOrWhiteSpace($env:AZURE_TENANT_ID)) { throw 'Missing expected Azure context.' }
$account = az account show -o json | ConvertFrom-Json
if ($LASTEXITCODE -ne 0 -or $account.id -ne $env:AZURE_SUBSCRIPTION_ID -or $account.tenantId -ne $env:AZURE_TENANT_ID) { throw 'CI Azure context mismatch.' }
$template = Join-Path $PSScriptRoot '../foundation-ci.bicep'
$parameters = Get-Content -LiteralPath $ParametersFile -Raw | ConvertFrom-Json
if ($parameters.parameters.environment.value -notin @('dev','test')) { throw 'CI parameters must explicitly select dev or test.' }
$arguments = @('--subscription', $env:AZURE_SUBSCRIPTION_ID, '--resource-group', $ResourceGroup,
    '--name', 'platform-ci', '--template-file', $template, '--parameters', "@$ParametersFile")
$preview = az deployment group what-if @arguments --no-pretty-print -o json
if ($LASTEXITCODE -ne 0) { throw 'Azure what-if failed.' }
$preview | Set-Content -LiteralPath $PreviewFile
$result = ($preview -join "`n") | ConvertFrom-Json
if ($result.status -ne 'Succeeded' -or @($result.changes).Count -eq 0) { throw 'Incomplete Azure preview; operator review required.' }
# Ignore represents unmanaged resources retained by incremental deployment.
if (@($result.changes | Where-Object { $_.changeType -notin @('Create','Modify','NoChange','Ignore') }).Count -gt 0) { throw 'Destructive or unresolved Azure changes require operator review.' }
if (@($result.diagnostics | Where-Object { $_.level -in @('Warning','Error') }).Count -gt 0) { throw 'Azure could not completely evaluate the preview.' }
$sanitized = ($result.changes | ConvertTo-Json -Depth 40) -replace '(?i)[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '[redacted-id]'
$sanitized = $sanitized -replace '(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}', '[redacted-email]'
if ($env:GITHUB_STEP_SUMMARY) {
    @('### Platform change preview', '```json', $sanitized, '```') | Add-Content -LiteralPath $env:GITHUB_STEP_SUMMARY
}
Write-Output 'Preview passed structural checks. This does not prove modifications are operationally safe.'
if ($Apply) {
    az deployment group create @arguments --mode Incremental --only-show-errors -o none
    if ($LASTEXITCODE -ne 0) { throw 'CI deployment failed.' }
    Write-Output 'CI foundation deployment succeeded.'
}
