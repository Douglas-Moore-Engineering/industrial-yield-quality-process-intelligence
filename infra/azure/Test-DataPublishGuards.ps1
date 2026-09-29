$ErrorActionPreference = 'Stop'
$root = Join-Path ([IO.Path]::GetTempPath()) ('iyqpis-publish-test-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $root | Out-Null
$context = Join-Path $root 'context.json'
$parameters = Join-Path $root 'parameters.json'
@{subscriptionId='test-sub';tenantId='test-tenant';accountEmail='test@example.invalid'} | ConvertTo-Json | Set-Content $context
@{parameters=@{registryName=@{value='crtest'};image=@{value='pending'}}} | ConvertTo-Json -Depth 5 | Set-Content $parameters
function az {
    $global:LASTEXITCODE = 0
    $global:publishTest.calls++
    $command = $args -join ' '
    if ($command -like 'account show*') { return '{"id":"test-sub","tenantId":"test-tenant","user":{"name":"test@example.invalid"}}' }
    if ($command -like 'acr show*') {
        return (@{loginServer='crtest.azurecr.io';publicNetworkAccess=$global:publishTest.access;adminUserEnabled=$false;networkRuleBypassOptions='None';networkRuleSet=@{defaultAction='Deny';ipRules=@($global:publishTest.rules)}} | ConvertTo-Json -Depth 5)
    }
    if ($command -like 'acr network-rule add*') { $global:publishTest.rules=@(@{ipAddressOrRange='203.0.113.5';action='Allow'}); return }
    if ($command -like 'acr network-rule remove*') {
        if ($command -notlike '*203.0.113.5/32*') { $global:publishTest.rules=@() }
        return
    }
    if ($command -like 'acr update*true*') {
        $global:publishTest.access='Enabled'
        if ($global:publishTest.mode -eq 'enable-timeout') { $global:LASTEXITCODE=1 }
        return
    }
    if ($command -like 'acr update*false*') { $global:publishTest.access='Disabled'; return }
    if ($command -like 'acr login*') { return }
    throw "Unexpected mocked Azure command: $command"
}
function docker {
    $global:LASTEXITCODE = 0
    $command = $args -join ' '
    if ($command -like 'image inspect*') { return (@(@{Id=('sha256:' + ('a'*64));RepoDigests=@('crtest.azurecr.io/iyqpis-data@sha256:' + ('b'*64))}) | ConvertTo-Json -Depth 5 -Compress) }
    if ($command -like 'tag*') { return }
    if ($command -like 'push*') { if($global:publishTest.mode -eq 'push-failure'){$global:LASTEXITCODE=1}; return }
    throw 'Unexpected mocked Docker command'
}
try {
    $global:publishTest=@{calls=0;access='Disabled';rules=@();mode='success'}
    $rejected=$false
    try { & "$PSScriptRoot/Publish-DataImage.ps1" -PublisherPublicIp '203.0.113.5' -ContextFile $context -ParametersFile $parameters }
    catch { $rejected=$true }
    if (-not $rejected -or $global:publishTest.calls -ne 0) { throw 'Missing-approval guard failed' }
    foreach($mode in @('success','push-failure','enable-timeout')) {
        $global:publishTest=@{calls=0;access='Disabled';rules=@();mode=$mode}
        $failed=$false
        try { & "$PSScriptRoot/Publish-DataImage.ps1" -PublisherPublicIp '203.0.113.5' -ContextFile $context -ParametersFile $parameters -ApproveTemporaryRegistryAccess }
        catch { $failed=$true }
        if ($failed -ne ($mode -ne 'success')) { throw "Unexpected outcome for $mode" }
        if ($global:publishTest.access -ne 'Disabled' -or $global:publishTest.rules.Count -ne 0) { throw "Restoration failed for $mode" }
    }
    Write-Output 'PASS: four publisher guard cases (approval, success, push failure, ambiguous enable timeout); all changes simulated.'
} finally {
    Remove-Item -LiteralPath $context,$parameters -Force
    Remove-Item -LiteralPath $root
    Remove-Item Function:az,Function:docker
    Remove-Variable publishTest -Scope Global
}
