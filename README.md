# openbci-mcp

FastMCP 3.2 MCP server and web dashboard for **OpenBCI** hardware via **BrainFlow**.

## Features

- Portmanteau MCP tools: board connect, stream, signal processing, export
- REST + WebSocket dashboard with live EEG trace and band power
- Cyton (serial), Ganglion (BLE), Galea, synthetic, and GUI streaming board modes
- Fleet ports: frontend **10758**, backend **10759**

## Quick start

```powershell
cd D:\Dev\repos\openbci-mcp
.\start.bat
```

Or stdio for Claude Desktop:

```powershell
uv sync
uv run openbci-mcp --stdio
```

## Hardware (Cyton)

1. Plug in USB dongle, note COM port (Device Manager or `openbci_board(operation='list_ports')`)
2. Close OpenBCI GUI if it holds the serial port
3. Connect: `openbci_board(operation='connect', board_key='cyton', serial_port='COM3')`
4. `openbci_stream(operation='start')`

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENBCI_MCP_PORT` | 10759 | Backend port |
| `OPENBCI_SERIAL_PORT` | (empty) | Default COM port |
| `OPENBCI_BOARD_ID` | 0 | BrainFlow board id hint |
| `OPENBCI_PROBE` | 0 | Run synthetic probe at startup |

## Links

- [OpenBCI](https://openbci.com/)
- [BrainFlow docs](https://brainflow.readthedocs.io/)
- [OpenBCI GUI](https://github.com/OpenBCI/OpenBCI_GUI)
