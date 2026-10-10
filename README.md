# openbci-mcp

FastMCP MCP server and web dashboard for **OpenBCI** hardware via **BrainFlow**.

## Stack

Python 3.12+ (`uv`), FastMCP `>=3.4.4,<4`, Starlette REST + WebSocket backend,
React 19 + Vite + TailwindCSS + react-router dashboard (`web_sota/`), Tauri 2 native shell (`native/`).

## Features

- Portmanteau MCP tools: board connect, stream, signal processing, export, OSC triggers, shutdown
- Machine-readable board capabilities: `openbci://boards/capabilities` resource
- Prompt templates: `openbci-quickstart`, `openbci-osc-recipe`
- REST + WebSocket dashboard with live EEG trace and band power
- Cyton (serial), Ganglion (BLE), Galea, synthetic, and GUI streaming board modes
- Fleet ports: frontend **10758**, backend **10759**

## Tool table

| Tool | Operations |
|---|---|
| `openbci_board` | connect, disconnect, status, list_ports, list_boards, probe |
| `openbci_stream` | start, stop, snapshot, marker |
| `openbci_signal` | band_power, filter |
| `openbci_export` | streamer_add, streamer_file, streamer_multicast |
| `openbci_trigger` | send_osc, list_rules, add_rule, remove_rule, evaluate, history, fire_test |
| `agentic_openbci_workflow` | multi-step sampling workflow |
| `openbci_help` | overview, quickstart, ports |
| `openbci_shutdown` | graceful shutdown |

Every tool returns `{success, message, ...}`. Trigger timing is a fixed 10 Hz hop —
see [OSC integration](docs/OSC_INTEGRATION.md).

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

New here? Read [docs/ONBOARDING.md](docs/ONBOARDING.md) — synthetic probe to live EEG in 10 minutes.

## Claude Desktop config

```json
{
  "mcpServers": {
    "openbci": {
      "command": "uv",
      "args": ["run", "--project", "D:\\Dev\\repos\\openbci-mcp", "openbci-mcp", "--stdio"]
    }
  }
}
```

## Hardware (Cyton)

1. Plug in USB dongle, note COM port (Device Manager or `openbci_board(operation='list_ports')`)
2. Close OpenBCI GUI if it holds the serial port
3. Connect: `openbci_board(operation='connect', board_key='cyton', serial_port='COM3')`
4. `openbci_stream(operation='start')`

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENBCI_MCP_HOST` | 127.0.0.1 | Backend bind |
| `OPENBCI_MCP_PORT` | 10759 | Backend port |
| `OPENBCI_SERIAL_PORT` | (empty) | Default COM port |
| `OPENBCI_BOARD_ID` | 0 | BrainFlow board id hint |
| `OPENBCI_PROBE` | 0 | Run synthetic probe at startup |
| `OPENBCI_OSC_HOST` | 127.0.0.1 | Default OSC trigger target |
| `OPENBCI_OSC_PORT` | 9000 | Default OSC UDP port (osc-mcp / VRChat) |
| `OPENBCI_TRIGGERS_FILE` | ~/.openbci-mcp/triggers.json | Persisted trigger rules |

## Ports

Backend 10759 (REST + MCP HTTP `/mcp` + WebSocket), frontend 10758. OSC out 127.0.0.1:9000.

## Documentation

| Guide | Topic |
|-------|--------|
| [Onboarding](docs/ONBOARDING.md) | First run, synthetic probe, pitfalls |
| [Usage scenarios](docs/USAGE_SCENARIOS.md) | Master index — pick your path |
| [Wearable styling](docs/WEARABLE_STYLING.md) | Helmet, cap, superbike look, cable routing |
| [Neurofeedback](docs/NEUROFEEDBACK.md) | Alpha, zen, focus meters |
| [BCI control](docs/BCI_CONTROL.md) | Mouse, P300, motor imagery, AI reality check |
| [VR and creative](docs/VR_CREATIVE.md) | OSC, Resonite, streaming, stage |
| [Hybrid EMG + EEG](docs/HYBRID_EMG_EEG.md) | Wristbands, clench gating, fusion |
| [OSC integration](docs/OSC_INTEGRATION.md) | osc-mcp pairing + trigger timing |

Webapp **Help** page (`http://127.0.0.1:10758/help`) loads these via `/api/help`.

## Links

- [OpenBCI](https://openbci.com/)
- [BrainFlow docs](https://brainflow.readthedocs.io/)
- [OpenBCI GUI](https://github.com/OpenBCI/OpenBCI_GUI)
- [OSC integration](docs/OSC_INTEGRATION.md) (osc-mcp pairing)
- [Changelog](CHANGELOG.md)
