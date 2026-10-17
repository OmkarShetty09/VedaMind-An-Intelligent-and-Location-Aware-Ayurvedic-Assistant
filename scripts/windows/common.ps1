# Shared helpers for the Windows scripts (dot-sourced; not run directly).

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

function Write-Step([string]$Message) { Write-Host "==> $Message" -ForegroundColor Cyan }
function Write-Ok([string]$Message) { Write-Host "[ok] $Message" -ForegroundColor Green }
function Write-Warn([string]$Message) { Write-Host "[!] $Message" -ForegroundColor Yellow }

# Runs a native program whose stderr is expected noise (e.g. a readiness probe). Under
# $ErrorActionPreference = "Stop", Windows PowerShell 5.1 turns any native stderr line into a
# terminating error even with 2>$null, so relax it for the duration of the call.
function Invoke-Quiet([string]$Exe, [string[]]$Arguments) {
    $previous = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try { & $Exe @Arguments 2>$null } finally { $ErrorActionPreference = $previous }
}

function Test-PortInUse([int]$Port) {
    return [bool](Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
}

# Returns @{ Exe = ...; Args = @(...) } for a Python 3.12-3.14 interpreter.
function Get-Python {
    $candidates = @(
        @{ Exe = "py"; Args = @("-3.12") }, @{ Exe = "py"; Args = @("-3.13") }, @{ Exe = "py"; Args = @("-3.14") },
        @{ Exe = "python3.12"; Args = @() }, @{ Exe = "python3.13"; Args = @() }, @{ Exe = "python3.14"; Args = @() },
        @{ Exe = "python"; Args = @() }
    )
    foreach ($c in $candidates) {
        if (-not (Get-Command $c.Exe -ErrorAction SilentlyContinue)) { continue }
        try {
            $ver = & $c.Exe @($c.Args + @("-c", "import sys; print('%d.%d' % sys.version_info[:2])")) 2>$null
        } catch { continue }
        if ($LASTEXITCODE -eq 0 -and $ver -match '^3\.(1[2-4])$') { return $c }
    }
    throw "Python 3.12, 3.13 or 3.14 is required. Install from https://www.python.org/downloads/ (tick 'Add to PATH')."
}

# Parses KEY=VALUE lines from the repo's .env (comments and blanks ignored).
function Read-DotEnv {
    $vars = @{}
    $path = Join-Path $Root ".env"
    if (-not (Test-Path $path)) { return $vars }
    foreach ($line in Get-Content $path) {
        if ($line -match '^\s*#' -or $line -notmatch '=') { continue }
        $key, $value = $line -split '=', 2
        $vars[$key.Trim()] = $value.Trim()
    }
    return $vars
}

# URL-safe random string from the OS crypto RNG (used for secrets and generated passwords).
function New-RandomSecret([int]$Bytes = 36) {
    $buffer = New-Object byte[] $Bytes
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($buffer)
    return [Convert]::ToBase64String($buffer).TrimEnd("=").Replace("+", "-").Replace("/", "_")
}

# Replaces every KEY=change-me line in the given .env with a fresh random value.
function Set-GeneratedSecrets([string]$Path) {
    $lines = Get-Content $Path
    $changed = @()
    $updated = foreach ($line in $lines) {
        if ($line -match '^([A-Z_]+)=change-me\s*$') {
            $changed += $Matches[1]
            "$($Matches[1])=$(New-RandomSecret)"
        } else { $line }
    }
    Set-Content -Path $Path -Value $updated -Encoding ASCII
    return $changed
}
