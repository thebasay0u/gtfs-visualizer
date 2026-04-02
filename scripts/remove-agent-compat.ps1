[CmdletBinding()]
param()

$repoRoot = Split-Path -Parent $PSScriptRoot
$legacyPath = Join-Path $repoRoot ".agent"

if (-not (Test-Path -LiteralPath $legacyPath)) {
    Write-Host "No compatibility alias found at: $legacyPath"
    exit 0
}

$item = Get-Item -LiteralPath $legacyPath -Force
if (-not $item.Attributes.ToString().Contains("ReparsePoint")) {
    throw "Refusing to remove '$legacyPath' because it is not a junction/symlink."
}

Remove-Item -LiteralPath $legacyPath -Force
Write-Host "Removed compatibility alias: $legacyPath"
