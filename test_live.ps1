$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
$envFile = Join-Path $root ".env"
if (-not (Test-Path -LiteralPath $envFile)) {
    throw "Missing .env. Copy .env.example to .env, configure it, then rerun .\test_live.ps1."
}

$healthUri = "http://127.0.0.1:8000/api/v1/health"
try {
    $health = Invoke-RestMethod -Uri $healthUri -TimeoutSec 10
}
catch {
    throw "TruthGuard is not reachable at http://127.0.0.1:8000. Start it with .\start.ps1 first."
}
if ($health.mode -notin @("live", "demo")) {
    throw "Health did not report a valid TruthGuard mode. Start the server from this repository with .\start.ps1."
}
if ($health.mode -eq "demo") {
    throw "Refusing live verification: health reports demo mode. Set TAVILY_API_KEY in .env and rerun .\start.ps1."
}

$apiKeyLine = [IO.File]::ReadAllLines($envFile) |
    Where-Object { $_ -match '^\s*TRUTHGUARD_API_KEYS\s*=' } |
    Select-Object -First 1
if (-not $apiKeyLine) {
    throw "TRUTHGUARD_API_KEYS is missing from .env. Add a private API key there before running this test."
}
$apiKeyMatch = [regex]::Match($apiKeyLine, '^\s*TRUTHGUARD_API_KEYS\s*=\s*(.*)$')
if (-not $apiKeyMatch.Success) {
    throw "TRUTHGUARD_API_KEYS could not be read from .env."
}
$apiKeysValue = $apiKeyMatch.Groups[1].Value.Trim().Trim('"').Trim("'")
$apiKey = ($apiKeysValue -split ",")[0].Trim()
if ([string]::IsNullOrWhiteSpace($apiKey)) {
    throw "TRUTHGUARD_API_KEYS is empty in .env. Add a private API key there before running this test."
}

$answers = @(
    "The latest stable release of Python is 3.9."
    "The current CEO of Microsoft is Satya Nadella."
)
$rows = @()
foreach ($answer in $answers) {
    try {
        $result = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/verify" `
            -Method Post -Headers @{ "X-API-Key" = $apiKey } `
            -ContentType "application/json" -Body (@{ answer = $answer } | ConvertTo-Json -Compress) `
            -TimeoutSec 180
    }
    catch {
        $safeMessage = $null
        if ($_.ErrorDetails.Message) {
            try { $safeMessage = ($_.ErrorDetails.Message | ConvertFrom-Json).error.message } catch { }
        }
        if ($safeMessage -and $safeMessage.Contains($apiKey)) { $safeMessage = $null }
        if ($safeMessage) { throw "Live verification failed: $safeMessage" }
        throw "Live verification request failed. Check the server status and provider configuration; no key was displayed."
    }

    foreach ($claimResult in $result.claims) {
        $source = $claimResult.sources | Select-Object -First 1
        $freshness = if ($null -eq $claimResult.freshness_score) { "unknown" } else { $claimResult.freshness_score }
        $confidence = "{0:P0}" -f $claimResult.evidence_confidence
        $domain = if ($source) { $source.domain } else { "none" }
        $sourceDate = if ($source -and $source.published_date) { $source.published_date } else { "unknown" }
        if ($source -and $source.published_date_inferred) { $sourceDate += " (inferred)" }
        $rows += [PSCustomObject]@{
            Claim = $claimResult.claim.original_text
            Status = $claimResult.status
            Freshness = $freshness
            "Evidence confidence" = $confidence
            "Top source domain" = $domain
            "Source date" = $sourceDate
        }
    }
}

if ($rows.Count -eq 0) { throw "No verifiable claims were returned for the two test answers." }
$rows | Format-Table -Wrap -AutoSize | Out-String -Width 320 | Write-Host
