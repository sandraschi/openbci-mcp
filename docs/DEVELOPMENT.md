# Development

```powershell
uv sync --all-extras
uv run pytest
uv run ruff check src tests
uv run openbci-mcp --serve
cd web_sota; npm run dev
```

Synthetic board tests do not require hardware.
