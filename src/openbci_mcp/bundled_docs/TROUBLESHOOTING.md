# Troubleshooting

## Cannot connect to COM port

- Close OpenBCI GUI and other apps using the dongle
- Run `openbci_board(operation='list_ports')`
- Try a different USB port

## Empty EEG buffer

- Call `openbci_stream(operation='start')` after connect
- Wait 1-2 seconds before snapshot

## BrainFlow DLL errors on Windows

- Re-run `uv sync` to fetch brainflow wheels for your platform
