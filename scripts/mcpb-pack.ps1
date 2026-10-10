# Fleet MCPB pack shim — delegates to the canonical fleet pack script.
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File scripts/mcpb-pack.ps1
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$fleetPack = "D:\Dev\repos\mcp-central-docs\scripts\fleet-mcpb-pack.ps1"
if (-not (Test-Path $fleetPack)) {
    Write-Host "ERROR: fleet pack script not found: $fleetPack" -ForegroundColor Red
    exit 1
}
& $fleetPack -RepoName "openbci-mcp" -RepoRoot $repoRoot
exit $LASTEXITCODE
