[CmdletBinding()]
param(
    [string]$ContextFile = "$PSScriptRoot/context.local.json",
    [string]$ParametersFile = "$PSScriptRoot/data-job.parameters.local.json",
    [string]$LocalImage = 'iyqpis-data:review',
    [Parameter(Mandatory)][string]$PublisherPublicIp,
    [switch]$ApproveTemporaryRegistryAccess
)
$ErrorActionPreference = 'Stop'
if (-not $ApproveTemporaryRegistryAccess) { throw 'This operation temporarily enables the registry public endpoint for one IPv4 address. Explicit approval is required.' }
$ip = $null
if (-not [Net.IPAddress]::TryParse($PublisherPublicIp,[ref]$ip) -or $ip.AddressFamily -ne [Net.Sockets.AddressFamily]::InterNetwork) { throw 'Provide one IPv4 address, not a CIDR or range.' }
function Invoke-Az([string[]]$Arguments) {
    $result = & az @Arguments --only-show-errors
    if ($LASTEXITCODE -ne 0) { throw 'Registry operation failed.' }
    return $result
}
$context = Get-Content $ContextFile -Raw | ConvertFrom-Json
$account = (Invoke-Az @('account','show','-o','json')) | ConvertFrom-Json
if ($account.id -ne $context.subscriptionId -or $account.tenantId -ne $context.tenantId -or $account.user.name -ne $context.accountEmail) { throw 'Wrong Azure context.' }
$parameters = Get-Content $ParametersFile -Raw | ConvertFrom-Json
$name = $parameters.parameters.registryName.value
$registry = (Invoke-Az @('acr','show','-g','rg-iyqpis-dev-platform','-n',$name,'-o','json')) | ConvertFrom-Json
if ($registry.publicNetworkAccess -ne 'Disabled' -or $registry.networkRuleSet.defaultAction -ne 'Deny' -or $registry.networkRuleBypassOptions -ne 'None' -or @($registry.networkRuleSet.ipRules).Count -ne 0 -or $registry.adminUserEnabled) { throw 'Registry baseline differs from the reviewed private-only configuration.' }
$local = docker image inspect $LocalImage | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw 'Build the data image before opening the publishing window.' }
$tag = $registry.loginServer + '/iyqpis-data:' + ($local[0].Id -replace '^sha256:','').Substring(0,16)
docker tag $LocalImage $tag
if ($LASTEXITCODE -ne 0) { throw 'Could not tag local image.' }
$cidr = $ip.ToString() + '/32'
$opened = $false
try {
    # Mark cleanup necessary before the first mutation, including ambiguous timeouts.
    $opened = $true
    Invoke-Az @('acr','network-rule','add','-n',$name,'--ip-address',$cidr,'-o','none')
    Invoke-Az @('acr','update','-n',$name,'--public-network-enabled','true','-o','none')
    Invoke-Az @('acr','login','-n',$name)
    docker push $tag
    if ($LASTEXITCODE -ne 0) { throw 'Image push failed; registry access will be closed.' }
    $pushed = docker image inspect $tag | ConvertFrom-Json
    if ($LASTEXITCODE -ne 0) { throw 'Could not inspect pushed digest.' }
    $digests = @($pushed[0].RepoDigests | Where-Object { $_ -like ($registry.loginServer + '/iyqpis-data@sha256:*') })
    if ($digests.Count -ne 1) { throw 'Cannot identify the published immutable digest.' }
    $parameters.parameters.image.value = $digests[0]
    $parameters | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $ParametersFile
    Write-Output 'Published image digest saved to ignored local parameters.'
} finally {
    if ($opened) {
        $closed = $false
        try { Invoke-Az @('acr','update','-n',$name,'--public-network-enabled','false','-o','none'); $closed = $true }
        finally {
            # Azure normalizes a /32 rule to a bare address. Read back its exact form.
            $current = (Invoke-Az @('acr','show','-n',$name,'-o','json')) | ConvertFrom-Json
            foreach ($rule in @($current.networkRuleSet.ipRules | Where-Object { $_.ipAddressOrRange -in @($cidr,$ip.ToString()) })) {
                Invoke-Az @('acr','network-rule','remove','-n',$name,'--ip-address',$rule.ipAddressOrRange,'-o','none')
            }
        }
        if (-not $closed) { throw 'Could not confirm registry public endpoint disabled. Inspect Azure immediately.' }
        $restored = (Invoke-Az @('acr','show','-n',$name,'-o','json')) | ConvertFrom-Json
        if ($restored.publicNetworkAccess -ne 'Disabled' -or @($restored.networkRuleSet.ipRules).Count -ne 0 -or $restored.adminUserEnabled) { throw 'Registry restoration could not be verified. Inspect Azure immediately.' }
        Write-Output 'Verified: registry public access disabled, no IP rules, admin account disabled.'
    }
}
