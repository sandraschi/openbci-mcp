# Changelog

## 0.1.0 — 2026-10-10 (assfix)

- Security: CORS `allow_origins=["*"]` replaced with explicit origins + Tailnet/LAN regex + Tauri schemes; bare `/mcp` path rewrite middleware.
- Issue #1: new `openbci://boards/capabilities` MCP resource (board id, channels, transport, units, rate) + documented OSC trigger timing (fixed 10 Hz hop, `hold_seconds` gating).
- New `openbci_shutdown` MCP tool + `POST /api/shutdown` (fleet launcher contract); new `GET /api/capabilities`, `GET /api/v1/diagnostics`, `GET /api/skills`, `GET /api/llm/discover` alias; `/health` now returns `status: ok`.
- All tools: `## Return Format` + `## Examples` docstrings, `message` key in every response, `logger.exception` in error paths; removed dead `transport.py` (`run_http_async` path).
- Prompts: `openbci-quickstart`, `openbci-osc-recipe`.
- Webapp: same-origin `/api` by default (absolute backend URL only behind Tauri gate); Tauri `frontendDist` fixed to `../web_sota/dist`; CSP covers 10758/10759; `@tauri-apps/api` dependency; onboarding cue under dashboard hero.
- Meta: `docs/ONBOARDING.md`, `CLAUDE.md`, `.cursorrules`/`.windsurfrules`/copilot instructions, Claude Code + OpenCode + Antigravity skills, `.pre-commit-config.yaml` + Biome hook, `.gitattributes`, `.mcpbignore`, `mcpb-pack` shim, Windows CI (`ci.yml`), `pyrightconfig.json`, coverage gate (>=40), refreshed `glama.json`/`llms.txt`/`llms-full.txt`, expanded domain skill.
- Prior-session backlog landed: `\\?\`-prefix strip (backend.rs), FleetStartMode BOM/SkipRestart/console titles, web_sota launcher migration, `.bak` dross cleanup.
