# Install the desktop half of hermes-redteam on Windows (Hermes desktop client).
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$hermesHome = if ($env:HERMES_HOME) { $env:HERMES_HOME } else { Join-Path $env:USERPROFILE ".hermes" }
$dest = Join-Path $hermesHome "desktop-plugins\hermes-redteam"

New-Item -ItemType Directory -Force -Path $dest | Out-Null
Copy-Item (Join-Path $root "desktop\plugin.js") (Join-Path $dest "plugin.js") -Force
$marker = Join-Path $dest ".hermes-package.json"
if (Test-Path $marker) { Remove-Item $marker -Force }

Write-Host "desktop half installed: $dest\plugin.js"
Write-Host ""
Write-Host "Next:"
Write-Host "  1) Hermes desktop -> Ctrl+K -> Reload desktop plugins"
Write-Host "  2) Capabilities -> Plugins -> hermes-redteam -> enable"
Write-Host "  3) Right sidebar -> RedTeam"
