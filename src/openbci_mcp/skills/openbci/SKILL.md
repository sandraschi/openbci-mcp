# OpenBCI MCP Skill

Use this server to acquire and analyze EEG from OpenBCI hardware through BrainFlow.

## Typical Cyton workflow

1. `openbci_board(operation="list_ports")` - find COM port
2. `openbci_board(operation="connect", board_key="cyton", serial_port="COM3")`
3. `openbci_stream(operation="start")`
4. `openbci_signal(operation="band_power")` for neurofeedback metrics
5. `openbci_stream(operation="snapshot")` for raw traces
6. `openbci_export(operation="streamer_multicast")` to mirror into OpenBCI GUI
7. `openbci_board(operation="disconnect")` when finished

## Safety

- One board session at a time; disconnect before switching boards
- Close OpenBCI GUI direct serial access before connecting via MCP
- Synthetic board (`board_key="synthetic"`) is safe for dev without hardware

## Integration

- Multicast stream pairs with OpenBCI GUI streaming board mode
- Band power → OSC via `openbci_trigger` (default 127.0.0.1:9000, see docs/OSC_INTEGRATION.md)
- Multi-step flows: `agentic_openbci_workflow`
