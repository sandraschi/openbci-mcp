set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]
import 'scripts/just/fleet.just'

# --- Dashboard ---

# Open the interactive recipe dashboard in the browser
default:
    @just --list

# --- Quality ---

# Execute Ruff linting and Biome CI on web_sota
lint:
    uv run --project {{justfile_directory()}} ruff check src tests; npm --prefix {{justfile_directory()}}\web_sota run biome:ci

# Execute Ruff fix/format and Biome write
fix:
    uv run --project {{justfile_directory()}} ruff check src tests --fix --unsafe-fixes; uv run --project {{justfile_directory()}} ruff format src tests; npm --prefix {{justfile_directory()}}\web_sota run biome

# Ruff format only
fmt:
    uv run --project {{justfile_directory()}} ruff format src tests

# Run Python tests
test:
    uv run --project {{justfile_directory()}} pytest tests/ -q

# Python typecheck (pyright, see pyrightconfig.json)
typecheck:
    uv run --project {{justfile_directory()}} pyright src

# Lint and test (fleet check recipe)
check: lint test

# Lint, typecheck, and test (all gates)
gates: lint typecheck test

# --- Runtime ---

# Install dependencies and sync environment
sync:
    uv sync --all-extras

# Run REST + MCP HTTP + WebSocket backend (port 10759)
serve:
    uv run --project {{justfile_directory()}} openbci-mcp --serve

# Run MCP stdio transport
stdio:
    uv run --project {{justfile_directory()}} openbci-mcp --stdio

# Start Vite dashboard (port 10758)
web:
    npm --prefix {{justfile_directory()}}\web_sota run dev

# Build production web dashboard
webapp:
    npm --prefix {{justfile_directory()}}\web_sota run build

# Sync, lint, and test
dev: sync lint test

# --- Hardening ---

# Execute Bandit security audit
check-sec:
    uv run --project {{justfile_directory()}} bandit -r src/

# Execute safety audit of dependencies
audit-deps:
    uv run --project {{justfile_directory()}} safety check

# Playwright fleet audit (requires backend + web running)
e2e:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\Dev\repos\mcp-central-docs\scripts\playwright-audit.ps1" -RepoPath "{{justfile_directory()}}"

# CUA webapp test: stack start + connected badge + title-matching nav walk
cua-webapp-test:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{{justfile_directory()}}\scripts\just\cua-webapp-test.ps1"

# CUA NSIS test: install, launch, health, nav walk, uninstall
cua-nsis-test:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{{justfile_directory()}}\scripts\just\cua-nsis-test.ps1"

# Build the Tauri native shell (NSIS)
build-native:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{{justfile_directory()}}\native\build.ps1"

# Pack the Claude Desktop bundle (.mcpb + install.ps1)
mcpb-pack:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{{justfile_directory()}}\scripts\mcpb-pack.ps1"

# Bootstrap: install dev deps + pre-commit hook (optional-dependencies layout: --extra, not --group)
bootstrap:
    uv sync --extra dev; uv run --project {{justfile_directory()}} pre-commit install; Write-Host "Pre-commit hooks installed." -ForegroundColor Green
