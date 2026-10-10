# Fleet Biome pre-commit hook: lint the web dashboard when present.
$ErrorActionPreference = "Stop"
$webRoots = @("web_sota", "webapp", "webapp/frontend", "web")
foreach ($rel in $webRoots) {
    $dir = Join-Path (Split-Path -Parent $PSScriptRoot) $rel
    if (Test-Path (Join-Path $dir "package.json")) {
        Push-Location $dir
        try {
            npm run biome:ci
            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        } finally {
            Pop-Location
        }
    }
}
