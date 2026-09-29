[CmdletBinding()]
param(
    [string]$ContextFile = "$PSScriptRoot/context.local.json",
    [string]$ParametersFile = "$PSScriptRoot/dev.parameters.local.json",
    [switch]$ApproveTemporaryCompute,
    # standardBsv2Family has 0 quota and is subscription-restricted in eastus2; standardDalsv7Family has 10 quota, 0 usage, no restrictions and EncryptionAtHostSupported.
    [string]$VmSize = 'Standard_D2als_v7'
)
$ErrorActionPreference = 'Stop'
if (-not $ApproveTemporaryCompute) { throw 'Temporary VM and disk incur charges. Explicitly pass -ApproveTemporaryCompute after reviewing the probe template and costs.' }
function Invoke-Az { param([string[]]$Arguments)
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { $result = & az @Arguments --only-show-errors 2>&1; $exitCode = $LASTEXITCODE }
    finally { $ErrorActionPreference = $previousPreference }
    if ($exitCode -ne 0) {
        $result | ForEach-Object { $_.ToString() } | Set-Content (Join-Path $PSScriptRoot 'azure-probe-error.local.json')
        throw "Azure command failed: $($Arguments[0..1] -join ' '); full error saved to ignored local output."
    }
    return $result
}
function Read-Az { param([string[]]$Arguments)
    $raw = Invoke-Az ($Arguments + @('-o','json'))
    $parsed = ($raw -join "`n") | ConvertFrom-Json
    return $parsed
}
$context = Get-Content -LiteralPath $ContextFile -Raw | ConvertFrom-Json
$account = Read-Az @('account','show')
if ($account.id -ne $context.subscriptionId -or $account.tenantId -ne $context.tenantId -or $account.user.name -ne $context.accountEmail) { throw 'Wrong Azure context.' }
$parameters = (Get-Content -LiteralPath $ParametersFile -Raw | ConvertFrom-Json).parameters
if ($parameters.environment.value -notin @('dev','test')) { throw 'Probe is restricted to development/test.' }
$feature = Read-Az @('feature','show','--namespace','Microsoft.Compute','--name','EncryptionAtHost')
if ($feature.properties.state -ne 'Registered') { throw 'EncryptionAtHost subscription feature must be registered before starting this probe. No compute was created.' }
$stem = "iyqpis-$($parameters.environment.value)"
$rg = "rg-$stem-platform"
$probeName = 'probe-' + [guid]::NewGuid().ToString('N').Substring(0,12)
$keyPath = Join-Path ([IO.Path]::GetTempPath()) "$probeName.key"
$bodyPath = Join-Path ([IO.Path]::GetTempPath()) "$probeName.json"
$logPath = Join-Path $PSScriptRoot 'private-probe.local.json'
$metadataPath = Join-Path $PSScriptRoot 'private-probe-resources.local.json'
Get-Command ssh-keygen -ErrorAction Stop | Out-Null

$registry = @(Read-Az @('acr','list','-g',$rg))[0]
$vault = @(Read-Az @('keyvault','list','-g',$rg))[0]
$publisher = Read-Az @('identity','show','-g',$rg,'-n',"id-$stem-publisher")
$runtime = Read-Az @('identity','show','-g',$rg,'-n',"id-$stem-runtime")
$vaultHost = ([uri]$vault.properties.vaultUri).Host
if (-not $vaultHost) {
    $vault = Read-Az @('keyvault','show','-g',$rg,'-n',$vault.name)
    $vaultHost = ([uri]$vault.properties.vaultUri).Host
}
$settings = @{
    hosts = @($registry.loginServer,$vaultHost,'api.loganalytics.io')
    registryHost = $registry.loginServer; vaultHost = $vaultHost
    publisherClientId = $publisher.clientId; runtimeClientId = $runtime.clientId
    endpointSubnet = $parameters.endpointSubnetPrefix.value
} | ConvertTo-Json -Compress
$source = Get-Content (Join-Path $PSScriptRoot 'private-probe.py') -Raw
$source64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($source))
$settings64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($settings))
$cloudInit = @"
#cloud-config
write_files:
  - path: /var/lib/platform-probe/probe.py
    permissions: '0700'
    encoding: b64
    content: $source64
  - path: /var/lib/platform-probe/settings.json
    permissions: '0600'
    encoding: b64
    content: $settings64
runcmd:
  - [sh, -c, 'python3 /var/lib/platform-probe/probe.py > /dev/ttyS0 2>&1']
"@
$cleanupFailed = $false
try {
    # An ephemeral key authorizes no external access: the VM has no public IP/inbound rule.
    & ssh-keygen -t rsa -b 3072 -f $keyPath -N '""' -q
    if ($LASTEXITCODE -ne 0) { throw 'Temporary key generation failed.' }
    $values = @{
        location=@{value=$parameters.location.value}; probeName=@{value=$probeName}
        vnetName=@{value="vnet-$stem"}; publisherName=@{value="id-$stem-publisher"}; runtimeName=@{value="id-$stem-runtime"}
        sshPublicKey=@{value=(Get-Content "$keyPath.pub" -Raw).Trim()}
        customData=@{value=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($cloudInit))}
        shutdownTime=@{value=[DateTime]::UtcNow.AddHours(1).ToString('HHmm')}
        vmSize=@{value=$VmSize}
    }
    @{parameters=$values} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $bodyPath
    @{resourceGroup=$rg;probeName=$probeName;diskName="$probeName-os";nicName="$probeName-nic";scheduleName="shutdown-computevm-$probeName";cleanup='pending'} | ConvertTo-Json | Set-Content $metadataPath
    Invoke-Az @('deployment','group','create','-g',$rg,'-n',$probeName,'--template-file',(Join-Path $PSScriptRoot '../probe.bicep'),'--parameters',"@$bodyPath",'-o','none')
    $deadline = [DateTime]::UtcNow.AddMinutes(15)
    $passed = $false
    do {
        $boot = Invoke-Az @('vm','boot-diagnostics','get-boot-log','-g',$rg,'-n',$probeName)
        $boot | Set-Content -LiteralPath $logPath
        if ($boot -match 'IYQPIS_PROBE_FAIL') { throw 'Private probe failed; see ignored local boot log.' }
        if ($boot -match 'IYQPIS_PROBE_PASS') { $passed = $true; break }
        Start-Sleep -Seconds 20
    } while ([DateTime]::UtcNow -lt $deadline)
    if (-not $passed) { throw 'Private probe timed out; see ignored local boot log.' }
    Write-Output 'PASS: private DNS/TLS, identity token grants, publisher push initiation, runtime push denial, vault RBAC denial.'
} finally {
    # Restrict deletion to the unique names generated in this invocation. Require our tag.
    foreach ($name in @($probeName,"shutdown-computevm-$probeName","$probeName-nic","$probeName-os")) {
        $inventory = @(Read-Az @('resource','list','-g',$rg))
        $resource = @($inventory | Where-Object name -eq $name)
        if ($resource.Count -eq 0) { continue }
        # OS disk inherits deletion from VM; never independently delete an untagged disk.
        if ($resource[0].tags.purpose -ne 'temporary-platform-acceptance') {
            if ($name -eq "$probeName-os") { continue }
            $cleanupFailed = $true
            continue
        }
        try {
            if ($name -eq $probeName) { Invoke-Az @('vm','delete','--ids',$resource[0].id,'--yes','-o','none') }
            else { Invoke-Az @('resource','delete','--ids',$resource[0].id,'-o','none') }
        } catch { $cleanupFailed = $true }
    }
    $remaining = @(Read-Az @('resource','list','-g',$rg) | Where-Object { $_.name -in @($probeName,"shutdown-computevm-$probeName","$probeName-nic","$probeName-os") })
    foreach ($file in @($keyPath,"$keyPath.pub",$bodyPath)) { if (Test-Path -LiteralPath $file) { Remove-Item -LiteralPath $file } }
    if ($cleanupFailed -or $remaining.Count -gt 0) { throw 'Probe cleanup incomplete. Use private-probe-resources.local.json to remove only the listed temporary resources; disk charges may continue.' }
    @{resourceGroup=$rg;probeName=$probeName;cleanup='verified-removed'} | ConvertTo-Json | Set-Content $metadataPath
    Write-Output 'PASS: temporary probe resources removed.'
}
