# BCI Control — Mouse, Speller, and Assistive Interfaces

Moving a cursor or “clicking” with EEG is **possible in prototype form**. It is **not** plug-and-play like a mouse. This doc separates paradigms, sets expectations, and shows where `openbci-mcp` fits in the pipeline.

## Paradigm comparison

| Paradigm | What user does | EEG signature | Bits/min | Training | Best UI |
|----------|----------------|---------------|--------|----------|---------|
| **Motor imagery (MI)** | Imagine left/right hand, feet | Mu/beta ERD at C3/C4/Cz | Low | **Heavy** per session | 2D cursor, game |
| **P300** | Count flashes on desired cell | P300 ~300 ms post-flash | Medium | Moderate calibration | Grid speller, menus |
| **SSVEP** | Look at flickering target | Steady-state at flicker freq | Medium–high | Map frequencies once | On-screen flicker menu |
| **Band power switch** | Relax vs focus | Alpha/beta thresholds | Very low | Light | Two-choice switch |
| **Hybrid EMG gate** | Clench wrist + MI/SSVEP | EMG burst + EEG | Medium | Moderate | See HYBRID_EMG_EEG.md |

**Alpha alone does not drive a mouse.** Use alpha for gating or modulating speed; use MI, P300, or SSVEP for **intent**.

## Motor imagery mouse (research-grade home lab)

### Channels

- **C3, C4, Cz** (sensorimotor cortex)
- **Reference:** earlobe or mastoid per OpenBCI tutorial
- Optional: full 8ch for artifact rejection

### Pipeline

```
openbci-mcp stream (250 Hz)
    → epoch windows (0.5–2 s)
    → CSP or Riemannian classifier (MNE-Python / sklearn)
    → left / right / idle classes
    → mouse: pyautogui / AutoHotkey / winops
```

`openbci-mcp` provides **acquisition + markers + CSV export**:

```
openbci_export(operation="streamer_file", file_path="D:/sessions/mi_run.csv")
openbci_stream(operation="marker", marker="imagery_left")
```

Classifier runs **outside** the MCP server (Python notebook or dedicated service)—by design.

### Session flow

1. **Calibration (15–30 min):** 20–40 trials per class (left hand, right hand, rest).
2. **Train classifier** on saved CSV.
3. **Online loop:** predict every 500 ms; move cursor 10 px per decision.
4. **Recalibrate** when accuracy drops (fatigue, electrode shift, hydration).

### Realistic performance

| User | Good day | Bad day |
|------|----------|---------|
| Experienced BCI user | 70–85% 3-class | 55–65% |
| First-time hobbyist | 55–65% | Near chance |

AI (deep nets, transfer learning) **helps** but does not eliminate daily recalibration.

## P300 speller / discrete click

### Requirements

- **8+ channels**, parietal coverage (Pz, POz, Oz)
- **Stimulus software** that flashes rows/columns or grid cells
- Sync markers with `openbci_stream(marker=...)`

### Flow

1. Show 6×6 grid of letters.
2. Flash rows/columns; user counts target flashes.
3. Detect P300 latency peak → infer row/column intersection.
4. ~1–2 seconds per character with good SNR.

**Use case:** Assistive communication prototype, not fast typing.

## SSVEP menu

### Requirements

- Occipital electrodes (O1, O2, Oz)
- On-screen targets flicker at unique rates (e.g. 6, 7.5, 8.57, 10 Hz)
- Classify which frequency power peaks

**Use case:** 4–8 choice menu without motor imagery training; **requires visible flicker** (VR/AR must implement flicker carefully).

## “AI mouse” hype vs practice (2026)

| Claim | Reality |
|-------|---------|
| “LLM reads EEG and clicks Chrome” | **No** — LLM does not replace calibrated ERP/MI pipeline |
| “Foundation model on EEG” | Emerging research; not OpenBCI drop-in |
| “Copilot + band power” | **Yes** — MCP agent helps design session, log results |
| `agentic_openbci_workflow` | Orchestrates connect/stream/analyze; **not** a magic mouse driver |

Recommended architecture:

```
EEG features (band power / CSP / CNN)
    → small fast classifier (Python)
    → intent: {left, right, click, idle}
    → OS input layer (AHK, pyautogui, accessibility API)
```

LLM layer: **session coach + config**, not millisecond classifier.

## Assistive / accessibility framing

- Design **large targets**, **error correction**, **dwell click**, **undo**.
- Target **switch scanning** + EEG as one input among many.
- Document fatigue; sessions often **under 30 min**.

## openbci-mcp tools map

| Step | Tool |
|------|------|
| Connect | `openbci_board(connect)` |
| Stream | `openbci_stream(start)` |
| Mark trials | `openbci_stream(marker=...)` |
| Features | `openbci_signal(band_power)` or export raw |
| Record | `openbci_export(streamer_file)` |
| Prototype switch | `openbci_trigger(evaluate)` with threshold rules |
| Multi-step setup | `agentic_openbci_workflow` |

## Example: two-choice switch (no ML)

1. Rule: beta at Cz **gt** threshold → OSC `/bci/select/a`
2. Rule: alpha at Oz **gt** threshold → OSC `/bci/select/b`
3. Host app listens on OSC; **not** a mouse—reliable for demos.

## Next steps

- Hybrid with wrist EMG: [HYBRID_EMG_EEG.md](HYBRID_EMG_EEG.md)
- Performance / VR output: [VR_CREATIVE.md](VR_CREATIVE.md)
- Wearable rig: [WEARABLE_STYLING.md](WEARABLE_STYLING.md)
