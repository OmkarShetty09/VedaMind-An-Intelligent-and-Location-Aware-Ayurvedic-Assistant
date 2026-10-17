<#
.SYNOPSIS
  Builds the RAG knowledge base: data\raw -> chunks -> Gemini embeddings -> pgvector.

.DESCRIPTION
  Needs PostgreSQL running (infra.ps1 / start.ps1) and GEMINI_API_KEY in .env.
  Safe to re-run: chunks are upserted. On the free Gemini tier it takes ~5 minutes
  because of rate limits (the script waits and retries automatically).

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\windows\ingest.ps1
  powershell -ExecutionPolicy Bypass -File scripts\windows\ingest.ps1 -Corpus charaka_samhita
#>
param([string]$Corpus = "")

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\common.ps1"

$ragPy = Join-Path $Root "rag\.venv\Scripts\python.exe"
if (-not (Test-Path $ragPy)) { throw "Run scripts\windows\setup.ps1 first." }

Push-Location (Join-Path $Root "rag")
try {
    & $ragPy -m app.ingestion validate
    if ($LASTEXITCODE -ne 0) { throw "Corpus validation failed (see above)." }
    $ingestArgs = @("-m", "app.ingestion", "ingest")
    if ($Corpus) { $ingestArgs += @("--corpus", $Corpus) }
    & $ragPy @ingestArgs
    if ($LASTEXITCODE -ne 0) { throw "Ingestion failed (see above). Is GEMINI_API_KEY set in .env and PostgreSQL running?" }
    & $ragPy -m app.ingestion report
} finally { Pop-Location }
