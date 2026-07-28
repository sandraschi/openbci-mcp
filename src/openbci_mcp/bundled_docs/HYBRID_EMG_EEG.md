# Hybrid EMG + EEG — Wristbands, Clench, and Fusion

**Muscle sensing complements brain sensing.** EMG is faster, sharper, and easier to classify for “do something now.” EEG carries **context** (focus, calm, error monitoring). Together they beat either alone for expressive control.

## Why combine?

| Modality | Strength | Weakness |
|----------|----------|----------|
| **EEG (OpenBCI)** | Affective state, MI, P300, SSVEP | Slow, noisy, artifact-prone |
| **EMG (wristband)** | On/off, gesture timing, high SNR | No “thought”; fatigue |
| **Fusion** | Clench **gates** EEG decisions; EMG **clicks**, EEG **modulates** | More wiring, sync logic |

Example: **Clench fist = confirm click**; **beta level = cursor speed**.

## Compatible gadgets (non-exhaustive)

| Device | Signals | Interface | Notes |
|--------|---------|-----------|-------|
| **Myo armband (legacy)** | 8 EMG | BLE (discontinued; used hardware) | Strong gesture SDK history |
| **OpenBCI EMG / Cyton aux** | EMG on same board | Cyton auxiliary channel | Single stack, best sync |
| **Thalmic / Ultraleap alternatives** | EMG variants | Vendor SDK | Check BrainFlow support |
| **Consumer “gesture wristbands”** | EMG/heuristic | BLE GATT | Often closed SDK—OSC bridge yourself |
| **OpenBCI Ganglion + EMG snap** | 4ch EEG+EMG mix | BLE | Compact wearable |
| **DIY EMG** | 1–2 channels | Arduino → serial | Cheap; you own filtering |

BrainFlow supports multiple board types—check [Supported Boards](https://brainflow.readthedocs.io/en/stable/SupportedBoards.html) before buying.

## Architecture patterns

### Pattern 1 — EMG gate, EEG brain

```
IF wrist_emg > threshold (clench)
    THEN read EEG MI classifier → action
ELSE
    ignore EEG (prevent idle drift)
```

Prevents false positives when user is talking, walking, or blinking.

### Pattern 2 — EMG discrete, EEG analog

```
EMG: fist = click, double pulse = back
EEG: alpha = scroll speed, beta = pressure
```

Good for **creative** and **assistive** UIs.

### Pattern 3 — Independent OSC buses

```
EEG  → openbci-mcp → OSC port 9000  (/bci/*)
EMG  → wrist bridge → OSC port 9001  (/emg/*)
Host → fusion script → VR / mouse
```

Keeps vendors decoupled; fusion in Python or TouchDesigner.

## Sync and timing

| Issue | Mitigation |
|-------|------------|
| BLE vs USB latency skew | Timestamp events; fuse on host clock |
| EMG leads EEG by ~20–50 ms | Accept or align with cross-correlation |
| Single BrainFlow session | Prefer **Cyton with EMG on aux** when possible |

`openbci_stream(marker=...)` for EMG events if you log both into one experiment CSV via external merger.

## Wristband placement aesthetics

- Matches **superbike telemetry** narrative: EEG cap + ** forearm telemetry cuffs**.
- LED rings on cuff driven by same OSC bus as helmet strip.
- Symmetry: left wrist = confirm, right wrist = cancel (configurable).

## Example fusion pseudo-logic (host script)

```python
# Pseudocode — runs beside openbci-mcp, not inside it
while True:
    eeg = fetch_band_power()  # from /api/status or local BrainFlow
    emg = read_wrist_ble()  # your bridge

    if emg.clench_strength > CLENCH_ON:
        armed = True

    if armed and eeg.beta_cz > FOCUS_THRESHOLD:
        send_osc("/cursor/move", [dx, dy])
        armed = False  # one-shot until next clench
```

## openbci-mcp role in hybrid stacks

| Function | Tool |
|----------|------|
| EEG stream | `openbci_board`, `openbci_stream` |
| Band features | `openbci_signal(band_power)` |
| EEG triggers | `openbci_trigger` |
| Log synchronized session | export CSV + parallel EMG log; merge in post |
| MCP orchestration | `agentic_openbci_workflow` |

EMG wristband integration is **intentionally external**—vendor SDKs differ. Document your bridge in repo-local `docs/MY_WRIST.md` if you build one.

## Use case recipes

### “Superbike pit lane” demo

- EEG alpha → breathing coach overlay on tablet.
- EMG clench → lap marker + OBS scene bump.
- Helmet + dual wrist cuffs = full **telemetry hero** look.

### VR social

- EEG beta → avatar “focus eyes.”
- EMG clench → emote / grab.

### Assistive switch

- EMG = primary click.
- EEG P300 = word selection when clench held 2 s.

## Safety and comfort

- EMG wristbands tight enough to sense, not tourniquet.
- EEG gel + wrist sweat — plan breaks; hydrate.
- Do not run stimulation devices on same arm without medical guidance.

## Related docs

- [BCI_CONTROL.md](BCI_CONTROL.md) — EEG paradigms for clicks
- [VR_CREATIVE.md](VR_CREATIVE.md) — OSC performance routing
- [WEARABLE_STYLING.md](WEARABLE_STYLING.md) — helmet + cuff visual design
- [USAGE_SCENARIOS.md](USAGE_SCENARIOS.md) — master index
