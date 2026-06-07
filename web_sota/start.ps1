Param([switch]$Headless, [switch]$BackendOnly, [switch]$NoBrowser)

if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    $relaunch = @('-NoProfile', '-File', $PSCommandPath, '-Headless')
    if ($BackendOnly) { $relaunch += '-BackendOnly' }
    if ($NoBrowser) { $relaunch += '-NoBrowser' }
    Start-Process powershell.exe -ArgumentList $relaunch -WindowStyle Hidden
    exit
}

$BackendPort = 10759
$FrontendPort = 10758
$RepoRoot = Split-Path -Parent $PSScriptRoot

Write-Host ""
Write-Host "openbci-mcp - Setup and Start" -ForegroundColor Cyan
Write-Host "Backend :$BackendPort   Frontend :$FrontendPort" -ForegroundColor DarkGray
Write-Host ""

foreach ($p in $BackendPort, $FrontendPort) {
    Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue |
        ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
}

$uvExe = (Get-Command uv -ErrorAction SilentlyContinue).Source
if (-not $uvExe) {
    Write-Host "ERROR: uv not found. Install: winget install Astral.uv" -ForegroundColor Red
    exit 1
}

Write-Host "[1/4] uv sync ..." -ForegroundColor Cyan
Set-Location $RepoRoot
& $uvExe sync
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "[2/4] import smoke test ..." -ForegroundColor Cyan
& $uvExe run python -c "import openbci_mcp.app; print('  [ok] import')"
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "[3/4] starting backend ..." -ForegroundColor Cyan
Start-Process -FilePath $uvExe -ArgumentList "run", "openbci-mcp", "--serve" -WorkingDirectory $RepoRoot -WindowStyle Hidden

for ($i = 0; $i -lt 45; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:$BackendPort/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        if ($r.StatusCode -eq 200) { break }
    } catch {}
    Start-Sleep -Seconds 1
}

if ($BackendOnly) {
    Write-Host "Backend ready at http://127.0.0.1:$BackendPort" -ForegroundColor Green
    exit 0
}

Write-Host "[4/4] starting frontend ..." -ForegroundColor Cyan
Set-Location $PSScriptRoot
if (-not (Test-Path "node_modules")) {
    npm install
}

if (-not $NoBrowser) {
    $frontendUrl = "http://127.0.0.1:$FrontendPort/"
    $pollAndOpen = "for (`$i = 0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
    Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollAndOpen
}

npm run dev
