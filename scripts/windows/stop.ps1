<#
.SYNOPSIS
  Stops the VedaMind services (ports 8000, 8001, 5173 by default) and the local PostgreSQL/Redis from infra.ps1.

.PARAMETER KeepInfra
  Leave PostgreSQL and Redis running.

.PARAMETER BackendPort
  Use the same port values that were given to start.ps1.
#>
param([switch]$KeepInfra, [int]$BackendPort = 8000, [int]$RagPort = 8001, [int]$FrontendPort = 5173)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\common.ps1"

# The terminal window start.ps1 opened for a server (title "VedaMind <name>"), if any, is an ancestor
# of the listening process (powershell -> venv launcher -> python [-> reloader child], or -> npm.cmd -> node ...).
# Ending that window ends the whole tree.
function Get-StartWindow([int]$ProcessId) {
    $current = Get-CimInstance Win32_Process -Filter "ProcessId=$ProcessId"
    for ($depth = 0; $current -and $depth -lt 10; $depth++) {
        if ($current.Name -eq "powershell.exe" -and $current.CommandLine -match "VedaMind (backend|rag|frontend)") {
            return $current.ProcessId
        }
        $current = Get-CimInstance Win32_Process -Filter "ProcessId=$($current.ParentProcessId)"
    }
    return $null
}

# True when the process or one of its parents was started from this project folder. The listening
# process itself may be the base interpreter (a venv's python.exe is a launcher that spawns it).
function Test-VedaMindProcess([int]$ProcessId) {
    $current = Get-CimInstance Win32_Process -Filter "ProcessId=$ProcessId"
    for ($depth = 0; $current -and $depth -lt 10; $depth++) {
        $cmd = [string]$current.CommandLine
        if ($cmd.IndexOf($Root, [StringComparison]::OrdinalIgnoreCase) -ge 0 -or $cmd -match "VedaMind (backend|rag|frontend)") {
            return $true
        }
        $current = Get-CimInstance Win32_Process -Filter "ProcessId=$($current.ParentProcessId)"
    }
    return $false
}

foreach ($port in $BackendPort, $RagPort, $FrontendPort) {
    Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique |
        ForEach-Object {
            if (-not (Test-VedaMindProcess $_)) {
                Write-Warn "Port $port is used by another program (not VedaMind); left it running."
                return
            }
            $target = Get-StartWindow $_
            if (-not $target) { $target = $_ }
            Invoke-Quiet "taskkill" @("/PID", "$target", "/T", "/F") | Out-Null
            Write-Ok "Stopped VedaMind on port $port"
        }
}
if (-not $KeepInfra) { & "$PSScriptRoot\infra.ps1" stop }
