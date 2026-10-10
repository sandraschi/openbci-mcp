# OSC integration

openbci-mcp sends OSC via `openbci_trigger` and the dashboard **Triggers** page.

## Default target

- Host: `127.0.0.1` (`OPENBCI_OSC_HOST`)
- Port: `9000` (`OPENBCI_OSC_PORT`)

Point this at any UDP OSC listener: **osc-mcp**, VRChat, Reaper, Resonite, etc.

## osc-mcp pairing

1. Start osc-mcp dashboard (ports 10766/10767)
2. Start an OSC listener on port 9000 or set `OPENBCI_OSC_PORT` to match your listener
3. Add a trigger rule: beta &gt; threshold → `/bci/focus`
4. Connect Cyton, start stream; rules evaluate on each WebSocket frame

## Trigger timing (issue #1 — fixed hop, not packet cadence)

Live rules do **not** evaluate on BrainFlow's native packet cadence. They evaluate on a
**fixed 10 Hz hop** in the `/api/ws/eeg` loop (`src/openbci_mcp/app.py`):

1. Loop iteration sleeps `0.1 s`.
2. `get_board_data(max_samples=64)` snapshots the latest samples.
3. `band_power(max_samples=128)` runs when the snapshot holds >= 32 samples.
4. `TriggerEngine.evaluate_bands(bands)` checks every enabled rule.

A rule fires only after its condition holds continuously for `hold_seconds`
(default `0.5 s`). After firing, that rule's hold timer resets to now, so the minimum
retrigger interval is also `hold_seconds`. Event payloads carry the evaluated band
value plus the rule's configured OSC value: `[rule.osc_value, value]`.

Consequences for agents that want reproducible event streams:

- Prefer `openbci_trigger(operation="evaluate")` for on-demand, single-shot checks
  against the current snapshot — same engine, no loop timing involved.
- Live-loop firings are reproducible only up to the 100 ms hop: two runs of the same
  rule can differ by one hop in fire time.
- Short `hold_seconds` (< 0.2 s) on noisy bands can double-fire across adjacent hops;
  raise the hold or the threshold instead of debouncing downstream.

## MCP examples

```
openbci_trigger(operation="send_osc", osc_address="/bci/focus", osc_values=[1.0])
openbci_trigger(
  operation="add_rule",
  name="Beta focus",
  channel="*",
  band="beta",
  operator="gt",
  threshold=0.5,
  hold_seconds=1.0,
  osc_address="/bci/focus",
)
```

## Agentic workflow

```
agentic_openbci_workflow(
  workflow_prompt="Connect synthetic board, stream, add beta OSC rule, evaluate",
  available_tools=["openbci_board", "openbci_stream", "openbci_trigger"],
)
```
