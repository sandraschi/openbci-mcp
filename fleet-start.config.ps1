# Per-repo fleet start config for openbci-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'openbci-mcp'
    BackendPort  = 10759
    FrontendPort = 10758
    HealthPath   = '/health'
    WebRoot      = 'web_sota'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'openbci_mcp.app:app'
        SyncExtras    = @('dev')
        SyncOnStart  = $true
        Env           = @{ WEB_PORT = '10759' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
