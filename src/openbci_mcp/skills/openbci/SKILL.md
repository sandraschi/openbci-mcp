# OpenBCI MCP Skill

Use this server to acquire and analyze EEG from OpenBCI hardware through BrainFlow.

## Who is reading this

- **Agents**: follow the tool workflows below. Plan channel counts and transports with
  `openbci://boards/capabilities` BEFORE `connect`. Respect the OSC timing section.
- **Humans**: dashboard on :10758, backend on :10759. Start at docs/ONBOARDING.md.

## Tool catalog

| Tool | Operations |
|---|---|
| `openbci_board` | connect, disconnect, status, list_ports, list_boards, probe |
| `openbci_stream` | start, stop, snapshot, marker |
| `openbci_signal` | band_power, filter |
| `openbci_export` | streamer_add, streamer_file, streamer_multicast |
| `openbci_trigger` | send_osc, list_rules, add_rule, remove_rule, evaluate, history, fire_test |
| `agentic_openbci_workflow` | multi-step sampling workflow (needs MCP client with sampling) |
| `openbci_help` | overview, quickstart, ports |
| `openbci_shutdown` | graceful shutdown (grace_ms) |

Resource: `openbci://boards/capabilities` — BrainFlow board id, EEG channel count,
transport (serial/ble/udp/none), units (microvolts), sampling rate. Null fields mean
"read `status` after connect", never defaults to trust.

## Workflow 1 — Typical Cyton session

1. `openbci_board(operation="list_ports")` — find COM port
2. `openbci_board(operation="connect", board_key="cyton", serial_port="COM3")`
3. `openbci_stream(operation="start")`
4. `openbci_signal(operation="band_power")` for neurofeedback metrics
5. `openbci_stream(operation="snapshot")` for raw traces
6. `openbci_export(operation="streamer_multicast")` to mirror into OpenBCI GUI
7. `openbci_board(operation="disconnect")` when finished

## Workflow 2 — Hardware-free dev loop

1. `openbci_board(operation="probe", board_key="synthetic")` — smoke test, no device
2. `openbci_board(operation="connect", board_key="synthetic")`
3. `openbci_stream(operation="start")` then `openbci_signal(operation="band_power")`
4. `openbci_trigger(operation="fire_test", osc_address="/bci/test")` — proves the OSC path

## Workflow 3 — Focus-gated OSC event

1. `openbci_trigger(operation="add_rule", name="focus", channel="*", band="beta", operator="gt", threshold=2.5, osc_address="/bci/focus")`
2. `openbci_trigger(operation="fire_test", osc_address="/bci/focus")` — verify downstream hears it
3. Stream and watch `history`. Tune `threshold`/`hold_seconds` from observed band ranges.

## OSC trigger timing (read before building reproducible streams)

Live rules evaluate on a FIXED 10 Hz hop, not BrainFlow packet cadence: the
`/api/ws/eeg` loop sleeps 0.1 s, snapshots <=64 samples, computes band power over
<=128 samples, and calls `TriggerEngine.evaluate_bands`. A rule fires only after its
condition holds continuously for `hold_seconds` (default 0.5 s); the timer resets on
fire, so the retrigger interval is also `hold_seconds`. For agent-driven,
reproducible event checks, call `openbci_trigger(operation="evaluate")` on demand
instead of relying on the live loop. Full detail: docs/OSC_INTEGRATION.md.

## Safety

- One board session at a time; disconnect before switching boards
- Close OpenBCI GUI direct serial access before connecting via MCP (port contention)
- Synthetic board (`board_key="synthetic"`) is safe for dev without hardware
- Ganglion BLE on Windows is flaky — prove flows on synthetic first

## Integration

- Multicast stream pairs with OpenBCI GUI streaming board mode
- Band power -> OSC via `openbci_trigger` (default 127.0.0.1:9000, see docs/OSC_INTEGRATION.md)
- Multi-step flows: `agentic_openbci_workflow`

## Troubleshooting

- `connect` fails access-denied: GUI or another session holds the port — close it, retry.
- `band_power` empty: stream is not running — `openbci_stream(operation="start")` first.
- No OSC arrives: `fire_test` first; check host/port and that a listener (osc-mcp, VRChat, Reaper) is up.
- `filter` needs `channel_name` — read names from `status` (`eeg_channel_names`).
