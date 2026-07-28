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
| `OPENBCI_OSC_HOST` | 127.0.0.1 | Default OSC trigger target |
| `OPENBCI_OSC_PORT` | 9000 | Default OSC UDP port (osc-mcp / VRChat) |
| `OPENBCI_TRIGGERS_FILE` | ~/.openbci-mcp/triggers.json | Persisted trigger rules |

## Documentation

| Guide | Topic |
|-------|--------|
| [Usage scenarios](docs/USAGE_SCENARIOS.md) | Master index — pick your path |
| [Wearable styling](docs/WEARABLE_STYLING.md) | Helmet, cap, superbike look, cable routing |
| [Neurofeedback](docs/NEUROFEEDBACK.md) | Alpha, zen, focus meters |
| [BCI control](docs/BCI_CONTROL.md) | Mouse, P300, motor imagery, AI reality check |
| [VR and creative](docs/VR_CREATIVE.md) | OSC, Resonite, streaming, stage |
| [Hybrid EMG + EEG](docs/HYBRID_EMG_EEG.md) | Wristbands, clench gating, fusion |
| [OSC integration](docs/OSC_INTEGRATION.md) | osc-mcp pairing |

Webapp **Help** page (`http://127.0.0.1:10758/help`) loads these via `/api/help`.

## Links

- [OpenBCI](https://openbci.com/)
- [BrainFlow docs](https://brainflow.readthedocs.io/)
- [OpenBCI GUI](https://github.com/OpenBCI/OpenBCI_GUI)
- [OSC integration](docs/OSC_INTEGRATION.md) (osc-mcp pairing)
