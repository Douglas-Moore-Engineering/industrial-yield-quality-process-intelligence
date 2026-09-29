$ErrorActionPreference='Stop'
$testRoot=Join-Path ([IO.Path]::GetTempPath()) ('iyqpis-ai-test-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $testRoot | Out-Null
Copy-Item "$PSScriptRoot/Invoke-ReferenceAI.ps1" $testRoot
@{subscriptionId='test-sub';tenantId='test-tenant';accountEmail='test@example.invalid'} | ConvertTo-Json | Set-Content "$testRoot/context.local.json"
$image='crtest.azurecr.io/iyqpis-data@sha256:'+('a'*64)
@{parameters=@{registryName=@{value='crtest'};image=@{value=$image}}} | ConvertTo-Json -Depth 5 | Set-Content "$testRoot/ai-job.parameters.local.json"
$global:aiGuardStarts=0
$global:aiGuardActive=$false
$global:aiGuardPublic='Disabled'
function az {
    $global:LASTEXITCODE=0
    $call=$args -join ' '
    if ($call -like 'account show*') { return '{"id":"test-sub","tenantId":"test-tenant","user":{"name":"test@example.invalid"}}' }
    if ($call -like 'containerapp job show*') { return '{"location":"East US 2","properties":{"configuration":{"triggerType":"Manual","replicaTimeout":3600,"replicaRetryLimit":1},"template":{"containers":[{"name":"data-batch","image":"old-image","resources":{"cpu":2,"memory":"4Gi"},"env":[{"name":"AZURE_CLIENT_ID","value":"test-identity"}]}]}}}' }
    if ($call -like 'containerapp job execution list*') {
        if ($global:aiGuardActive) { return '[{"properties":{"status":"Running"}}]' }
        return '[]'
    }
    if ($call -like 'acr show*') { return (@{loginServer='crtest.azurecr.io';publicNetworkAccess=$global:aiGuardPublic;networkRuleSet=@{ipRules=@()}} | ConvertTo-Json -Depth 4) }
    if ($call -like 'containerapp job start*') {
        $index=[array]::IndexOf($args,'--yaml')
        if ($index -lt 0) { throw 'Missing template' }
        $template=Get-Content $args[$index+1] -Raw | ConvertFrom-Json
        $container=$template.containers[0]
        if (($container.command -join ' ') -ne 'python -m iyqpis.azure_intelligence' -or $container.image -ne $image -or ($container.env | Where-Object name -eq AZURE_CLIENT_ID).value -ne 'test-identity' -or ($container.env | Where-Object name -eq DATA_RUN_ID).value.Length -ne 32) { throw 'Execution template lost configuration' }
        $global:aiGuardStarts++
        return '{"name":"test-ai-execution"}'
    }
    throw 'Unexpected Azure command'
}
try {
    $script=Join-Path $testRoot 'Invoke-ReferenceAI.ps1'
    $refused=$false
    try { & $script } catch { $refused=$true }
    if (-not $refused -or $global:aiGuardStarts) { throw 'Approval guard failed' }
    & $script -ApproveRun | Out-Null
    if ($global:aiGuardStarts -ne 1) { throw 'Expected one execution' }
    foreach ($mode in @('active','public')) {
        $global:aiGuardActive=$mode -eq 'active'
        if ($mode -eq 'public') { $global:aiGuardPublic='Enabled' }
        $refused=$false
        try { & $script -ApproveRun } catch { $refused=$true }
        if (-not $refused -or $global:aiGuardStarts -ne 1) { throw 'Unsafe execution not refused' }
    }
    Write-Output 'PASS: AI approval, immutable template preservation, active-run refusal and private-registry guard'
} finally {
    Remove-Item Function:\az
    $separator=[IO.Path]::DirectorySeparatorChar
    $resolved=[IO.Path]::GetFullPath($testRoot)
    $temp=[IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd($separator)+$separator
    if (-not $resolved.StartsWith($temp,[StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe cleanup path' }
    Remove-Item -LiteralPath $resolved -Recurse -Force
}
