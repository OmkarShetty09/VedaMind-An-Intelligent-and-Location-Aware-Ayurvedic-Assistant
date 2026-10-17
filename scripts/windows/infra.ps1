<#
.SYNOPSIS
  Local PostgreSQL 16 (+ pgvector) and Redis for VedaMind on Windows - no Docker, no admin rights.

.DESCRIPTION
  Everything lives in <repo>\.localdev (git-ignored):
    - PostgreSQL 16.2 + pgvector 0.6 from the `pgserver` Python package (bundled binaries)
    - Redis for Windows (portable build from github.com/redis-windows/redis-windows)
  First start creates the database, role and the `vector` extension using the
  POSTGRES_DB / POSTGRES_USER / POSTGRES_PASSWORD values from .env.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\windows\infra.ps1 start
  powershell -ExecutionPolicy Bypass -File scripts\windows\infra.ps1 status
  powershell -ExecutionPolicy Bypass -File scripts\windows\infra.ps1 stop
#>
param([ValidateSet("start", "stop", "status")][string]$Action = "start")

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\common.ps1"

$Dev = Join-Path $Root ".localdev"
$PgVenv = Join-Path $Dev "pgvenv"
$PgHome = Join-Path $PgVenv "Lib\site-packages\pgserver\pginstall"
$PgBin = Join-Path $PgHome "bin"
$PgData = Join-Path $Dev "pgdata"
$RedisVersion = "8.8.3"
$RedisDir = Join-Path $Dev "Redis-$RedisVersion-Windows-x64-msys2"
$RedisUrl = "https://github.com/redis-windows/redis-windows/releases/download/$RedisVersion/Redis-$RedisVersion-Windows-x64-msys2.zip"

function Install-Postgres {
    if (Test-Path (Join-Path $PgBin "postgres.exe")) { return }
    Write-Step "Installing PostgreSQL 16 + pgvector into .localdev (one time, ~60 MB)"
    $py = Get-Python
    & $py.Exe @($py.Args + @("-m", "venv", $PgVenv))
    & (Join-Path $PgVenv "Scripts\python.exe") -m pip install --disable-pip-version-check -q "pgserver==0.1.4" tzdata
    if ($LASTEXITCODE -ne 0) { throw "pip install pgserver failed" }
    # The bundled build lacks timezone data; without it Postgres rejects even TimeZone='UTC'.
    $tz = Join-Path $PgHome "share\postgresql\timezone"
    if (-not (Test-Path $tz)) {
        Copy-Item (Join-Path $PgVenv "Lib\site-packages\tzdata\zoneinfo") $tz -Recurse
    }
}

function Install-Redis {
    if (Test-Path (Join-Path $RedisDir "redis-server.exe")) { return }
    Write-Step "Downloading Redis $RedisVersion for Windows (one time, ~14 MB)"
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $zip = Join-Path $Dev "redis.zip"
    Invoke-WebRequest -Uri $RedisUrl -OutFile $zip -UseBasicParsing
    Expand-Archive -Path $zip -DestinationPath $Dev -Force
    Remove-Item $zip
}

function Wait-Until([scriptblock]$Check, [string]$What, [int]$Seconds = 30) {
    for ($i = 0; $i -lt $Seconds; $i++) {
        if (& $Check) { return }
        Start-Sleep -Seconds 1
    }
    throw "$What did not become ready within $Seconds s (see logs in .localdev)"
}

function Test-PgReady {
    Invoke-Quiet (Join-Path $PgBin "pg_isready.exe") @("-h", "127.0.0.1", "-p", "5432", "-U", "postgres", "-q") | Out-Null
    return $LASTEXITCODE -eq 0
}

function Invoke-Psql([string]$Database, [string]$Sql) {
    $env:PGOPTIONS = "--client-min-messages=warning"  # hide "already exists, skipping" notices
    & (Join-Path $PgBin "psql.exe") -h 127.0.0.1 -p 5432 -U postgres -d $Database -v ON_ERROR_STOP=1 -q -c $Sql
    if ($LASTEXITCODE -ne 0) { throw "psql failed: $Sql" }
}

function Start-Postgres {
    Install-Postgres
    $fresh = -not (Test-Path (Join-Path $PgData "PG_VERSION"))
    if ($fresh) {
        Write-Step "Initialising a new database cluster"
        & (Join-Path $PgBin "initdb.exe") -D $PgData -U postgres --auth=trust -E UTF8 --locale=C | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "initdb failed" }
    }
    if (Test-PgReady) {
        Write-Ok "PostgreSQL already running on 127.0.0.1:5432"
    } else {
        if (Test-PortInUse 5432) { throw "Port 5432 is used by another program (an installed PostgreSQL?). Stop it or use that server instead (see README)." }
        Start-Process -FilePath (Join-Path $PgBin "postgres.exe") -WindowStyle Hidden `
            -ArgumentList @("-D", "`"$PgData`"", "-p", "5432", "-c", "listen_addresses=127.0.0.1") `
            -RedirectStandardError (Join-Path $Dev "postgres.log")
        Wait-Until { Test-PgReady } "PostgreSQL"
    }
    Initialize-Database
}

# Idempotent: role, database and the vector extension, from the POSTGRES_* values in .env.
function Initialize-Database {
    $envVars = Read-DotEnv
    $db = $envVars["POSTGRES_DB"]; if (-not $db) { $db = "vedamind" }
    $user = $envVars["POSTGRES_USER"]; if (-not $user) { $user = "vedamind" }
    $pass = $envVars["POSTGRES_PASSWORD"]; if (-not $pass) { $pass = "vedamind" }
    $roleExists = & (Join-Path $PgBin "psql.exe") -h 127.0.0.1 -U postgres -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$user'"
    if ($roleExists -ne "1") {
        Write-Step "Creating role '$user' and database '$db'"
        Invoke-Psql "postgres" "CREATE ROLE `"$user`" LOGIN CREATEDB PASSWORD '$($pass.Replace("'", "''"))';"
    }
    $dbExists = & (Join-Path $PgBin "psql.exe") -h 127.0.0.1 -U postgres -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$db'"
    if ($dbExists -ne "1") { Invoke-Psql "postgres" "CREATE DATABASE `"$db`" OWNER `"$user`";" }
    Invoke-Psql $db "CREATE EXTENSION IF NOT EXISTS vector;"
    Write-Ok "PostgreSQL 16 + pgvector running on 127.0.0.1:5432 (db '$db', user '$user')"
}

function Test-RedisReady {
    $out = Invoke-Quiet (Join-Path $RedisDir "redis-cli.exe") @("-h", "127.0.0.1", "-p", "6379", "ping")
    return $out -eq "PONG"
}

function Start-Redis {
    Install-Redis
    if (Test-RedisReady) { Write-Ok "Redis already running on 127.0.0.1:6379"; return }
    if (Test-PortInUse 6379) { throw "Port 6379 is used by another program (Memurai / another Redis?). Stop it or keep using it." }
    Start-Process -FilePath (Join-Path $RedisDir "redis-server.exe") -WindowStyle Hidden -WorkingDirectory $RedisDir `
        -ArgumentList @("--port", "6379", "--bind", "127.0.0.1", "--save", "`"`"", "--appendonly", "no") `
        -RedirectStandardOutput (Join-Path $Dev "redis.log")
    Wait-Until { Test-RedisReady } "Redis"
    Write-Ok "Redis running on 127.0.0.1:6379"
}

function Stop-All {
    if (Test-Path (Join-Path $PgBin "pg_ctl.exe")) {
        if (Test-PgReady) {
            & (Join-Path $PgBin "pg_ctl.exe") -D $PgData stop -m fast | Out-Null
            Write-Ok "PostgreSQL stopped"
        }
    }
    if ((Test-Path (Join-Path $RedisDir "redis-cli.exe")) -and (Test-RedisReady)) {
        Invoke-Quiet (Join-Path $RedisDir "redis-cli.exe") @("-h", "127.0.0.1", "-p", "6379", "shutdown", "nosave") | Out-Null
        Write-Ok "Redis stopped"
    }
}

New-Item -ItemType Directory -Force -Path $Dev | Out-Null
switch ($Action) {
    "start" { Start-Postgres; Start-Redis }
    "stop" { Stop-All }
    "status" {
        if (Test-PortInUse 5432) { Write-Ok "PostgreSQL: listening on 5432" } else { Write-Warn "PostgreSQL: not running" }
        if (Test-PortInUse 6379) { Write-Ok "Redis: listening on 6379" } else { Write-Warn "Redis: not running" }
    }
}
