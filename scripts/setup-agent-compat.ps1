[CmdletBinding()]
param()

$repoRoot = Split-Path -Parent $PSScriptRoot
$legacyPath = Join-Path $repoRoot ".agent"
$canonicalPath = Join-Path $repoRoot ".agents"

if (-not (Test-Path -LiteralPath $canonicalPath)) {
    throw "Canonical path missing: $canonicalPath"
}

if (Test-Path -LiteralPath $legacyPath) {
    Write-Host "Legacy path already exists: $legacyPath"
    exit 0
}

New-Item -ItemType Junction -Path $legacyPath -Target $canonicalPath | Out-Null
Write-Host "Created compatibility junction: $legacyPath -> $canonicalPath"
