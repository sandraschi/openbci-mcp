param([switch]$Headless, [switch]$BackendOnly, [switch]$NoBrowser)
& (Join-Path $PSScriptRoot "web_sota\start.ps1") @PSBoundParameters
exit $LASTEXITCODE
