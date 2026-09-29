[CmdletBinding()]
param(
    [ValidatePattern('^[a-f0-9]{32}$')][string]$DataRunId = 'cb03fc7d2f32c0e29031cc4fd00fc4fb',
    [string]$ContextFile = "$PSScriptRoot/context.local.json",
    [string]$ParametersFile = "$PSScriptRoot/ai-job.parameters.local.json",
    [switch]$ApproveRun
)
$ErrorActionPreference = 'Stop'
if (-not $ApproveRun) { throw 'An on-demand AI validation execution incurs bounded job charges. Pass -ApproveRun after review.' }
function Read-Az([string[]]$Arguments) {
    $raw = & az @Arguments --only-show-errors -o json
    if ($LASTEXITCODE -ne 0) { throw 'Azure reference AI command failed.' }
    return (($raw -join "`n") | ConvertFrom-Json)
}
$ctx = Get-Content $ContextFile -Raw | ConvertFrom-Json
$account = Read-Az @('account','show')
if ($account.id -ne $ctx.subscriptionId -or $account.tenantId -ne $ctx.tenantId -or $account.user.name -ne $ctx.accountEmail) { throw 'Wrong Azure context.' }
$rg='rg-iyqpis-dev-platform'; $name='job-iyqpis-dev-data'
$job = Read-Az @('containerapp','job','show','-g',$rg,'-n',$name)
if ($job.properties.configuration.triggerType -ne 'Manual' -or ($job.location -replace '\s','') -ne 'eastus2' -or $job.properties.configuration.replicaTimeout -gt 3600 -or $job.properties.configuration.replicaRetryLimit -gt 1) { throw 'Unexpected job configuration.' }
$runs = @(Read-Az @('containerapp','job','execution','list','-g',$rg,'-n',$name))
if (@($runs | Where-Object { $_.properties.status -notin @('Succeeded','Failed','Stopped') }).Count) { throw 'Another execution is active or unresolved.' }
$parameters = (Get-Content $ParametersFile -Raw | ConvertFrom-Json).parameters
$registry = Read-Az @('acr','show','-g',$rg,'-n',$parameters.registryName.value)
if ($registry.publicNetworkAccess -ne 'Disabled' -or @($registry.networkRuleSet.ipRules).Count) { throw 'Registry must be private with no temporary access rules.' }
$pattern='^'+[regex]::Escape($registry.loginServer)+'/iyqpis-data@sha256:[a-f0-9]{64}$'
if ($parameters.image.value -notmatch $pattern) { throw 'Published immutable reference image required.' }
$container = $job.properties.template.containers | Where-Object name -eq 'data-batch'
if (-not $container -or $container.resources.cpu -gt 2 -or $container.resources.memory -ne '4Gi') { throw 'Unexpected compute envelope.' }
$container.image=$parameters.image.value
$container | Add-Member -NotePropertyName command -NotePropertyValue @('python','-m','iyqpis.azure_intelligence') -Force
$container | Add-Member -NotePropertyName args -NotePropertyValue @() -Force
$container.env = @($container.env | Where-Object name -ne 'DATA_RUN_ID') + @(@{name='DATA_RUN_ID';value=$DataRunId})
$templatePath="$PSScriptRoot/ai-execution-template.local.json"
$job.properties.template | ConvertTo-Json -Depth 30 | Set-Content $templatePath
$execution=Read-Az @('containerapp','job','start','-g',$rg,'-n',$name,'--yaml',$templatePath)
$execution | ConvertTo-Json -Depth 30 | Set-Content "$PSScriptRoot/ai-execution.local.json"
Write-Output 'Reference AI validation submitted. Default data job, schedule and infrastructure are unchanged. Verify execution status and completion evidence.'
