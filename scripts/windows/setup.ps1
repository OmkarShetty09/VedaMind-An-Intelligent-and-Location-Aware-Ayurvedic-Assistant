<#
.SYNOPSIS
  One-time setup for running VedaMind on Windows without Docker.

.DESCRIPTION
  Creates backend\.venv and rag\.venv, installs Python dependencies, installs the
  frontend's npm packages and creates .env from .env.example if it does not exist.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\windows\setup.ps1
#>
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\common.ps1"

$py = Get-Python
$pyVersion = & $py.Exe @($py.Args + @("--version"))
Write-Ok "Using $pyVersion ($($py.Exe) $($py.Args -join ' '))"

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    throw "Node.js 20 or newer is required: https://nodejs.org/ (LTS installer)."
}
$nodeMajor = [int]((node --version).TrimStart("v").Split(".")[0])
if ($nodeMajor -lt 20) { throw "Node.js 20+ is required (found $(node --version))." }
Write-Ok "Using Node.js $(node --version)"

foreach ($service in @("backend", "rag")) {
    $dir = Join-Path $Root $service
    $venvPython = Join-Path $dir ".venv\Scripts\python.exe"
    if (-not (Test-Path $venvPython)) {
        Write-Step "Creating $service\.venv"
        & $py.Exe @($py.Args + @("-m", "venv", (Join-Path $dir ".venv")))
    }
    Write-Step "Installing $service Python packages (a few minutes the first time)"
    & $venvPython -m pip install --disable-pip-version-check -q --upgrade pip
    & $venvPython -m pip install --disable-pip-version-check -q -r (Join-Path $dir "requirements\dev.txt")
    if ($LASTEXITCODE -ne 0) { throw "pip install failed for $service" }
    Write-Ok "$service dependencies installed"
}

Write-Step "Installing frontend npm packages"
Push-Location (Join-Path $Root "frontend")
try {
    npm ci --no-audit --no-fund
    if ($LASTEXITCODE -ne 0) { throw "npm ci failed" }
} finally { Pop-Location }
Write-Ok "frontend dependencies installed"

$envFile = Join-Path $Root ".env"
if (-not (Test-Path $envFile)) {
    Copy-Item (Join-Path $Root ".env.example") $envFile
    $generated = Set-GeneratedSecrets $envFile
    Write-Ok "Created .env from .env.example (random values generated for: $($generated -join ', '))"
}
$vars = Read-DotEnv
if (-not $vars["GEMINI_API_KEY"] -or $vars["GEMINI_API_KEY"] -like "your-*") {
    Write-Warn "Open .env and set GEMINI_API_KEY (free: https://aistudio.google.com/apikey) before starting."
}
Write-Host ""
Write-Ok "Setup complete. Next: powershell -ExecutionPolicy Bypass -File scripts\windows\start.ps1"
