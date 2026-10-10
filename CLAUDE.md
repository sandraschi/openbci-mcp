# CLAUDE.md (openbci-mcp)

FastMCP+BrainFlow OpenBCI server. Package `openbci_mcp` under `src/`.

- Backend 10759 (`uv run openbci-mcp --serve`), frontend 10758 (`npm --prefix web_sota run dev`), launcher `web_sota/start.ps1` (root `start.bat` delegates).
- Gates: `just gates` (ruff + pyright + pytest). Web: `npm --prefix web_sota run biome:ci`, `npm --prefix web_sota run build`.
- Standards: fleet AGENTS.md chain; no `allow_origins=["*"]` ever; same-origin `/api` in webapp (Tauri gate only exception); every tool returns `message`.
- Key files: `src/openbci_mcp/app.py`, `board_manager.py`, `trigger_engine.py`, `resources.py`, `tools/`, `prompts.py`, `docs/OSC_INTEGRATION.md` (timing!), `docs/ONBOARDING.md`.
- Hardware: synthetic board for tests (`probe`); close OpenBCI GUI before Cyton USB; triggers evaluate on a fixed 10 Hz hop (see OSC_INTEGRATION.md).
