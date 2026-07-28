set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]
import 'scripts/just/fleet.just'

# ── Dashboard ─────────────────────────────────────────────────────────────────

# Open the interactive recipe dashboard in the browser
default:
    @just --list

# ── Quality ───────────────────────────────────────────────────────────────────

# Execute Ruff linting and Biome CI on web_sota
lint:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check src tests
    Set-Location '{{justfile_directory()}}\web_sota'
    npm run biome:ci

# Execute Ruff fix/format and Biome write
fix:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check src tests --fix --unsafe-fixes
    uv run ruff format src tests
    Set-Location '{{justfile_directory()}}\web_sota'
    npm run biome

# Run Python tests
test:
    Set-Location '{{justfile_directory()}}'
    uv run pytest tests/ -q

# Lint and test (fleet check recipe)
check: lint test

# ── Runtime ───────────────────────────────────────────────────────────────────

# Install dependencies and sync environment
sync:
    uv sync --all-extras

# Run REST + MCP HTTP + WebSocket backend (port 10759)
serve:
    Set-Location '{{justfile_directory()}}'
    uv run openbci-mcp --serve

# Run MCP stdio transport
stdio:
    Set-Location '{{justfile_directory()}}'
    uv run openbci-mcp --stdio

# Start Vite dashboard (port 10758)
web:
    Set-Location '{{justfile_directory()}}\web_sota'
    npm run dev

# Build production web dashboard
webapp:
    Set-Location '{{justfile_directory()}}\web_sota'
    npm run build

# Sync, lint, and test
dev: sync lint test

# ── Hardening ─────────────────────────────────────────────────────────────────

# Execute Bandit security audit
check-sec:
    Set-Location '{{justfile_directory()}}'
    uv run bandit -r src/

# Execute safety audit of dependencies
audit-deps:
    Set-Location '{{justfile_directory()}}'
    uv run safety check

# Playwright fleet audit (requires backend + web running)
e2e:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\Dev\repos\mcp-central-docs\scripts\playwright-audit.ps1" -RepoPath "{{justfile_directory()}}"
