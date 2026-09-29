$ErrorActionPreference = 'Stop'
$testRoot = Join-Path ([IO.Path]::GetTempPath()) ('iyqpis-job-test-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $testRoot | Out-Null
Copy-Item "$PSScriptRoot/Invoke-DataJob.ps1" $testRoot
@{subscriptionId='test-sub';tenantId='test-tenant';accountEmail='test@example.invalid'} | ConvertTo-Json | Set-Content "$testRoot/context.local.json"
$global:jobTestActive = $false
$global:jobTestStarted = 0
function az {
    $global:LASTEXITCODE = 0
    $command = $args -join ' '
    if ($command -like 'account show*') { return '{"id":"test-sub","tenantId":"test-tenant","user":{"name":"test@example.invalid"}}' }
    if ($command -like 'containerapp job show*') {
        return '{"location":"East US 2","properties":{"configuration":{"triggerType":"Manual"},"template":{"containers":[{"name":"data-batch","image":"example@sha256:unchanged","resources":{"cpu":2,"memory":"4Gi"},"env":[{"name":"DATASETS","value":"manufacturing-spc"},{"name":"INGEST_TIME","value":"2026-09-28T00:00:00Z"},{"name":"AZURE_CLIENT_ID","value":"test-identity"}]}]}}}'
    }
    if ($command -like 'containerapp job execution list*') {
        if ($global:jobTestActive) { return '[{"properties":{"status":"Running"}}]' }
        return '[]'
    }
    if ($command -like 'containerapp job start*') {
        $global:jobTestStarted++
        $yamlIndex = [array]::IndexOf($args, '--yaml')
        if ($yamlIndex -lt 0) { throw 'Missing complete template override' }
        $template = Get-Content $args[$yamlIndex + 1] -Raw | ConvertFrom-Json
        $container = $template.containers[0]
        if (($container.env | Where-Object name -eq DATASETS).value -ne 'manufacturing-spc,secom') { throw 'Dataset override lost' }
        if (($container.env | Where-Object name -eq AZURE_CLIENT_ID).value -ne 'test-identity' -or $container.resources.cpu -ne 2 -or $container.image -ne 'example@sha256:unchanged') { throw 'Template settings lost' }
        return '{"name":"test-execution"}'
    }
    throw 'Unexpected Azure command'
}
try {
    $operator = Join-Path $testRoot 'Invoke-DataJob.ps1'
    $refused = $false
    try { & $operator -Action Start } catch { $refused = $true }
    if (-not $refused -or $global:jobTestStarted) { throw 'Approval guard failed' }
    & $operator -Action Start -ApproveRun -Datasets manufacturing-spc,secom | Out-Null
    if ($global:jobTestStarted -ne 1) { throw 'Expected one start' }
    $global:jobTestActive = $true
    $refused = $false
    try { & $operator -Action Start -ApproveRun -Datasets manufacturing-spc,secom } catch { $refused = $true }
    if (-not $refused -or $global:jobTestStarted -ne 1) { throw 'Active execution guard failed' }
    Write-Output 'PASS: approval guard, normalized Azure region, complete dataset template, active execution guard'
} finally {
    Remove-Item Function:\az
    # Only remove the uniquely named test directory under the resolved temp root.
    $resolvedTest = [IO.Path]::GetFullPath($testRoot)
    $separator = [IO.Path]::DirectorySeparatorChar
    $resolvedTemp = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd($separator) + $separator
    if (-not $resolvedTest.StartsWith($resolvedTemp, [StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe test cleanup path' }
    Remove-Item -LiteralPath $resolvedTest -Recurse -Force
}
