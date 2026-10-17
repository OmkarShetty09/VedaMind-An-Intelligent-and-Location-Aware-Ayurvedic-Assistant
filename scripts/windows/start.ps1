<#
.SYNOPSIS
  Starts VedaMind on Windows: database + Redis, migrations + demo data, then backend, RAG and frontend.

.PARAMETER SkipInfra
  Use your own PostgreSQL/Redis (already running, configured in .env) instead of scripts\windows\infra.ps1.

.PARAMETER Background
  Run the three services hidden, logging to .localdev\logs, instead of opening three terminal windows.

.PARAMETER BackendPort
  Port for the Django backend (default 8000). The RAG and frontend services are pointed at it.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\windows\start.ps1
  powershell -ExecutionPolicy Bypass -File scripts\windows\start.ps1 -BackendPort 8010 -RagPort 8011
#>
param(
    [switch]$SkipInfra,
    [switch]$Background,
    [int]$BackendPort = 8000,
    [int]$RagPort = 8001,
    [int]$FrontendPort = 5173
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\common.ps1"

$backendPy = Join-Path $Root "backend\.venv\Scripts\python.exe"
$ragPy = Join-Path $Root "rag\.venv\Scripts\python.exe"
if (-not (Test-Path $backendPy) -or -not (Test-Path $ragPy) -or -not (Test-Path (Join-Path $Root "frontend\node_modules"))) {
    throw "Run scripts\windows\setup.ps1 first."
}
if (-not (Test-Path (Join-Path $Root ".env"))) { throw ".env is missing - run setup.ps1 (it copies .env.example)." }

if (-not $SkipInfra) { & "$PSScriptRoot\infra.ps1" start }

foreach ($port in $BackendPort, $RagPort, $FrontendPort) {
    if (Test-PortInUse $port) {
        throw "Port $port is already in use (VedaMind already running? then scripts\windows\stop.ps1; another app? pick other ports, e.g. -BackendPort 8010 -RagPort 8011)"
    }
}
# Child processes inherit these; they take precedence over the URLs in .env.
$env:RAG_SERVICE_URL = "http://127.0.0.1:$RagPort"
$env:BACKEND_GUARDRAIL_URL = "http://127.0.0.1:$BackendPort/api/v1/guardrails/check"
$env:VITE_API_PROXY_TARGET = "http://127.0.0.1:$BackendPort"

Write-Step "Applying database migrations and demo data"
Push-Location (Join-Path $Root "backend")
try {
    & $backendPy manage.py migrate --noinput
    if ($LASTEXITCODE -ne 0) { throw "migrate failed - check the POSTGRES_* / DATABASE_URL values in .env" }
    & $backendPy manage.py seed_demo_data
    & $backendPy manage.py create_superuser
} finally { Pop-Location }

$services = @(
    @{ Name = "backend"; Dir = "backend"; Exe = $backendPy; Args = @("manage.py", "runserver", "127.0.0.1:$BackendPort") },
    @{ Name = "rag"; Dir = "rag"; Exe = $ragPy; Args = @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "$RagPort") },
    @{ Name = "frontend"; Dir = "frontend"; Exe = "npm.cmd"; Args = @("run", "dev", "--", "--port", "$FrontendPort", "--strictPort") }
)
$logs = Join-Path $Root ".localdev\logs"
New-Item -ItemType Directory -Force -Path $logs | Out-Null

foreach ($s in $services) {
    $dir = Join-Path $Root $s.Dir
    if ($Background) {
        Start-Process -FilePath $s.Exe -ArgumentList $s.Args -WorkingDirectory $dir -WindowStyle Hidden `
            -RedirectStandardOutput (Join-Path $logs "$($s.Name).log") -RedirectStandardError (Join-Path $logs "$($s.Name).err.log")
    } else {
        $command = "`$Host.UI.RawUI.WindowTitle = 'VedaMind $($s.Name)'; & '$($s.Exe)' $($s.Args -join ' ')"
        Start-Process -FilePath "powershell.exe" -WorkingDirectory $dir -ArgumentList @("-NoExit", "-Command", $command)
    }
    Write-Ok "Started $($s.Name)"
}

Write-Step "Waiting for the services to answer"
for ($i = 0; $i -lt 60; $i++) {
    $up = (Test-PortInUse $BackendPort) -and (Test-PortInUse $RagPort) -and (Test-PortInUse $FrontendPort)
    if ($up) { break }
    Start-Sleep -Seconds 1
}
if (-not $up) { Write-Warn "Not all services are listening yet - check their windows (or .localdev\logs)." }

# The knowledge base must be ingested once (it lives in PostgreSQL).
$vars = Read-DotEnv
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:$RagPort/api/v1/health" -Headers @{ "X-RAG-Admin-Token" = $vars["RAG_ADMIN_TOKEN"] } -TimeoutSec 10
    if ($health.rag_chunks -eq 0) {
        Write-Warn "Knowledge base is empty. Run once:  powershell -ExecutionPolicy Bypass -File scripts\windows\ingest.ps1"
    } else {
        Write-Ok "Knowledge base: $($health.rag_chunks) chunks"
    }
} catch {
    Write-Warn "Could not query the RAG service health yet ($($_.Exception.Message))."
}

Write-Host ""
Write-Ok "VedaMind is running:  http://localhost:$FrontendPort"
Write-Host "    Backend API  http://127.0.0.1:$BackendPort/api/v1   (health: http://127.0.0.1:$BackendPort/healthz)"
Write-Host "    RAG docs     http://127.0.0.1:$RagPort/docs"
if ($vars["DEMO_EMAIL"]) { Write-Host "    Admin        http://localhost:$FrontendPort/admin   $($vars['DEMO_EMAIL']) / $($vars['DEMO_PASSWORD'])" }
if ($vars["DEMO_USER_EMAIL"]) { Write-Host "    Demo user    $($vars['DEMO_USER_EMAIL']) / $($vars['DEMO_USER_PASSWORD'])   (credentials from .env)" }
$portArgs = if ($BackendPort -ne 8000 -or $RagPort -ne 8001 -or $FrontendPort -ne 5173) { " -BackendPort $BackendPort -RagPort $RagPort -FrontendPort $FrontendPort" } else { "" }
Write-Host "    Stop with    powershell -ExecutionPolicy Bypass -File scripts\windows\stop.ps1$portArgs"
