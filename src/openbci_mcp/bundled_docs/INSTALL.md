# Install

## Requirements

- Windows 11 (fleet host)
- Python 3.12+ via [uv](https://docs.astral.sh/uv/)
- Node.js LTS (Vite frontend)
- OpenBCI Cyton/Ganglion USB dongle or BLE

## Steps

```powershell
cd D:\Dev\repos\openbci-mcp
uv sync
cd web_sota
npm install
```

Launch full stack:

```powershell
.\start.bat
```

## MCP client (stdio)

Add to Claude Desktop / Cursor MCP config:

```json
{
  "mcpServers": {
    "openbci": {
      "command": "uv",
      "args": ["run", "--directory", "D:/Dev/repos/openbci-mcp", "openbci-mcp", "--stdio"]
    }
  }
}
```

HTTP mode: `http://127.0.0.1:10759/mcp`
