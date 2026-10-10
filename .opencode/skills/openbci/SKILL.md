---
name: openbci
description: OpenBCI BrainFlow EEG — board connect, stream, band power, OSC triggers
---

# OpenBCI MCP Skill

Acquire and analyze EEG from OpenBCI hardware through BrainFlow.

## For agents

1. `openbci_board(operation="list_ports")` — find COM port
2. `openbci_board(operation="connect", board_key="cyton", serial_port="COM3")`
3. `openbci_stream(operation="start")`
4. `openbci_signal(operation="band_power")` — neurofeedback metrics
5. `openbci_stream(operation="snapshot")` — raw traces
6. `openbci_export(operation="streamer_multicast")` — mirror into OpenBCI GUI
7. `openbci_board(operation="disconnect")` when finished

Plan first with `openbci://boards/capabilities` (channel counts, transports, units).
Trigger timing is a fixed 10 Hz hop — see docs/OSC_INTEGRATION.md.
One board session at a time; close the OpenBCI GUI before Cyton USB; synthetic board is safe for dev.

## For humans

Dashboard on :10758, backend :10759. New here? Read docs/ONBOARDING.md first.
