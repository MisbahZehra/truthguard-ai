$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"
$sitePackages = Join-Path $backend ".venv\Lib\site-packages"
$dist = Join-Path $frontend "dist"
$envFile = Join-Path $root ".env"

if (-not (Test-Path -LiteralPath $envFile)) {
    throw "Missing .env. Copy .env.example to .env, add your own credentials, then rerun .\start.ps1."
}

$pythonCandidates = @(
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
)
$pythonCandidates += @(Get-ChildItem -Path "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe" -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty FullName)
$pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
if ($pythonCommand) { $pythonCandidates += $pythonCommand.Source }
$python = $pythonCandidates | Where-Object {
    (Test-Path -LiteralPath $_) -and $_ -notlike "*\backend\.venv\*"
} | Select-Object -First 1
if (-not $python) {
    $launcher = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($launcher) {
        $python = & $launcher.Source -3.12 -c "import sys; print(sys.executable)"
        if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $python) -or $python -like "*\backend\.venv\*") { $python = $null }
    }
}
if (-not $python) { throw "Python 3.12 was not found. Install Python 3.12 and rerun .\start.ps1." }

$env:PYTHONPATH = $sitePackages
$missingDependencies = $false
& $python -c "import fastapi, httpx, dotenv, pydantic, uvicorn"
if ($LASTEXITCODE -ne 0) { $missingDependencies = $true }
if ($missingDependencies) {
    Write-Host "Installing missing backend requirements..."
    & $python -m pip install --target $sitePackages -r (Join-Path $backend "requirements.txt")
    if ($LASTEXITCODE -ne 0) { throw "Backend dependency installation failed." }
    & $python -c "import fastapi, httpx, dotenv, pydantic, uvicorn"
    if ($LASTEXITCODE -ne 0) { throw "Backend dependencies remain unavailable after installation." }
}

if (-not (Test-Path -LiteralPath $dist)) {
    Push-Location $frontend
    try {
        npm.cmd install
        if ($LASTEXITCODE -ne 0) { throw "npm install failed." }
        npm.cmd run build
        if ($LASTEXITCODE -ne 0) { throw "Frontend build failed." }
    }
    finally {
        Pop-Location
    }
}

foreach ($name in @("TAVILY_API_KEY", "LLM_API_KEY", "LLM_MODEL", "LLM_BASE_URL")) {
    $value = [Environment]::GetEnvironmentVariable($name, "Process")
    if ([string]::IsNullOrWhiteSpace($value)) {
        [Environment]::SetEnvironmentVariable($name, $null, "Process")
    }
}

$env:STATIC_DIR = $dist
$uri = "http://127.0.0.1:8000"
$health = $null
$uiConfig = $null
try {
    $candidateHealth = Invoke-RestMethod -Uri "$uri/api/v1/health" -TimeoutSec 2
    if ($candidateHealth.status -eq "ok" -and $candidateHealth.mode -in @("live", "demo")) {
        $candidateConfig = Invoke-RestMethod -Uri "$uri/ui/config" -TimeoutSec 2
        if ($candidateConfig.mode -eq $candidateHealth.mode) {
            $health = $candidateHealth
            $uiConfig = $candidateConfig
        }
    }
}
catch { }

if (-not $health) {
    $listener = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
    if ($listener) {
        throw "Port 8000 is occupied by a service that does not expose TruthGuard's expected health and UI config. Stop that service and rerun .\start.ps1."
    }

    $stdoutLog = Join-Path $env:TEMP "truthguard-backend-stdout.log"
    $stderrLog = Join-Path $env:TEMP "truthguard-backend-stderr.log"
    $server = Start-Process -FilePath $python `
        -ArgumentList @("-m", "uvicorn", "app.main:create_app", "--factory", "--host", "127.0.0.1", "--port", "8000") `
        -WorkingDirectory $backend -PassThru `
        -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog

    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        Start-Sleep -Seconds 1
        try {
            $candidateHealth = Invoke-RestMethod -Uri "$uri/api/v1/health" -TimeoutSec 2
            $candidateConfig = Invoke-RestMethod -Uri "$uri/ui/config" -TimeoutSec 2
            if ($candidateHealth.status -eq "ok" -and $candidateHealth.mode -in @("live", "demo") -and
                $candidateConfig.mode -eq $candidateHealth.mode) {
                $health = $candidateHealth
                $uiConfig = $candidateConfig
                break
            }
        } catch {
            if ($server.HasExited) { throw "TruthGuard failed to start. Check the backend startup logs in $env:TEMP." }
        }
    }
    if (-not $health) { throw "TruthGuard did not become healthy within 60 seconds. Check the backend startup logs in $env:TEMP." }
    Write-Host "Server started (PID $($server.Id))."
}
else {
    Write-Host "Using the already-running TruthGuard server."
}

Write-Host "Health mode: $($health.mode)"
Write-Host "UI config llm: $($uiConfig.llm)"
Write-Host "UI config tavily_configured: $($uiConfig.tavily_configured)"
if ($health.mode -eq "demo") {
    Write-Warning "The server is in DEMO mode. Add TAVILY_API_KEY to .env for live search; the UI currently uses simulated sources."
}
Write-Host "TruthGuard: $uri"
