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
