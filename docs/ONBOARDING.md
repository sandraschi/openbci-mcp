# Onboarding: openbci-mcp

Get from zero to live EEG in ~10 minutes. No hardware? Use the synthetic board — every step below works without a device.

## 1. What this is

MCP server + dashboard for OpenBCI EEG headsets (Cyton, Ganglion, Galea) via BrainFlow. Agents connect, stream, compute band power, and fire OSC triggers (VRChat, Reaper, osc-mcp). Humans watch the live trace on the dashboard.

## 2. Install

```powershell
cd D:\Dev\repos\openbci-mcp
uv sync
.\start.bat   # backend :10759 + dashboard :10758
```

No wrappee to install for the synthetic path. Real hardware needs the BrainFlow native libs (bundled via pip) and, for Cyton, a USB serial driver.

## 3. First run (no hardware)

1. Dashboard: http://127.0.0.1:10758 — you should see the hero + board status (disconnected).
2. Probe: `openbci_board(operation="probe", board_key="synthetic")` — expect `success: true`.
3. Connect: `openbci_board(operation="connect", board_key="synthetic")`.
4. Stream: `openbci_stream(operation="start")`, then `openbci_signal(operation="band_power")` — expect delta..gamma per channel.
5. OSC test: `openbci_trigger(operation="fire_test", osc_address="/bci/test")` — expect `success: true` (UDP to 127.0.0.1:9000; no listener needed).
6. Disconnect: `openbci_board(operation="disconnect")`.

Sanity = steps 2-5 all `success: true`. If step 4 fails, the stream is not running — start it first.

## 4. First run (Cyton USB)

1. Plug in the dongle, note the COM port (dashboard shows ports, or `list_ports`).
2. CLOSE the OpenBCI GUI — it holds the serial port and connect will fail while it runs.
3. `openbci_board(operation="connect", board_key="cyton", serial_port="COM3")` (your COM port).
4. Same stream/band-power steps as above.

## 5. Pitfalls

- "port busy / access denied" on connect: OpenBCI GUI (or another session) holds the COM port. Close it, retry.
- Ganglion BLE on Windows is flaky — prove your flow on synthetic first, then switch board_key.
- Triggers evaluate on a fixed 10 Hz hop with `hold_seconds` gating (see docs/OSC_INTEGRATION.md) — they are not sample-locked.
- One board session at a time; disconnect before switching boards.

## 6. Next

- docs/USAGE_SCENARIOS.md (pick your path), docs/OSC_INTEGRATION.md (osc-mcp pairing), docs/NEUROFEEDBACK.md.
- `openbci://boards/capabilities` resource: channel counts/transports before you connect.
