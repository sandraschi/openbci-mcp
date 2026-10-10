# Copilot instructions (openbci-mcp)

FastMCP+BrainFlow EEG server (`src/openbci_mcp/`), dashboard in `web_sota/`, Tauri in `native/`.
Run `just gates` before finishing. Tools: `openbci_board`, `openbci_stream`, `openbci_signal`,
`openbci_export`, `openbci_trigger`, `openbci_help`, `openbci_shutdown`; resource
`openbci://boards/capabilities`. Trigger timing: fixed 10 Hz hop — see docs/OSC_INTEGRATION.md.
