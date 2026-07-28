# Usage Scenarios — Master Guide

This document maps **everything you can realistically do** with OpenBCI + `openbci-mcp`, from meditation neurofeedback to hybrid EMG+EEG control. Read the linked deep-dives for each path.

## Quick decision tree

```
What do you want?
│
├─ Calm / focus / meditation feedback     → NEUROFEEDBACK.md
├─ Look cool while wearing sensors        → WEARABLE_STYLING.md
├─ VR, art, lights, music reacts to brain → VR_CREATIVE.md + OSC_INTEGRATION.md
├─ Move cursor / click / assistive UI     → BCI_CONTROL.md
├─ Combine fist/wrist + brain signals     → HYBRID_EMG_EEG.md
└─ Research, logging, MCP automation      → TOOLS.md + DEVELOPMENT.md
```

## Scenario matrix

| Scenario | EEG paradigm | Channels needed | Training | Latency | openbci-mcp role |
|----------|--------------|-----------------|----------|---------|------------------|
| Alpha relaxation feedback | Band power (alpha↑) | 2–8 | Minutes | Real-time | `openbci_signal(band_power)` + dashboard |
| Focus / beta neurofeedback | Beta/theta ratio | 4–8 | Minutes | Real-time | Trigger rules → OSC |
| Meditation “zen meter” | Alpha + theta trends | 4+ | None | Smooth 1–5 s | WebSocket dashboard |
| VR avatar mood | Band power thresholds | 4–8 | Tune thresholds | ~100 ms | OSC → Resonite / VRChat |
| Live art / lights | Any band or raw | 1–8 | Per-install | ~100 ms | `openbci_trigger` |
| Motor imagery mouse | MI classifier | C3, Cz, C4 + refs | **Per session** 15–30 min | 200–500 ms | Stream + export to classifier |
| P300 speller / click grid | Event-related potential | 8+ (Pz, Oz, parietal) | Calibration blocks | 1–2 s/choice | Markers + CSV export |
| SSVEP menu | Steady-state VEP | Occipital (O1,O2,Oz) | Map flicker freqs | ~300 ms | Sync with flicker UI |
| Hybrid “clench + focus” | EMG gate + EEG | Wrist EMG + EEG | Per user | ~150 ms | OSC fusion layer |
| Research logging | Raw + markers | 8–16 | Study design | N/A | CSV / multicast stream |

## What is *not* realistic (yet)

- Seamless “think the Chrome icon” with no training, no special UI, consumer-grade accuracy.
- Medical diagnosis or clinical EEG interpretation.
- Invisible sensors with lab-grade SNR inside a sweaty bike helmet with no tradeoffs.
- Replacing a mouse for all-day office work without fatigue and recalibration.

## Hardware tiers

| Tier | Gear | Best for |
|------|------|----------|
| **Starter** | Ganglion (4ch) + simple headband | Neurofeedback, demos, BLE wearable |
| **Standard** | Cyton (8ch) + Ultracortex Mark IV | Research, VR, MI experiments |
| **Dense** | Cyton+Daisy (16ch) | P300, SSVEP, publications |
| **Hybrid** | Cyton + EMG wristband(s) | Clench-gated BCI, expressive control |

## Software stack (this repo)

```
OpenBCI board
    → BrainFlow (openbci-mcp board_manager)
    → openbci-mcp (stream, band_power, triggers, OSC)
    → Your layer: classifier / VR / mouse / meditation UI
```

## Recommended reading order

1. [WEARABLE_STYLING.md](WEARABLE_STYLING.md) — how it looks and feels on a human
2. [NEUROFEEDBACK.md](NEUROFEEDBACK.md) — alpha, zen, focus meters
3. [VR_CREATIVE.md](VR_CREATIVE.md) — OSC, installations, performance
4. [BCI_CONTROL.md](BCI_CONTROL.md) — mouse, speller, assistive paradigms
5. [HYBRID_EMG_EEG.md](HYBRID_EMG_EEG.md) — wristbands + EEG fusion
6. [OSC_INTEGRATION.md](OSC_INTEGRATION.md) — fleet wiring to osc-mcp

## Session checklist (any scenario)

1. Clean skin contact (gel for wet electrodes; wipe for dry).
2. Close OpenBCI GUI if using USB serial directly.
3. `openbci_board(connect)` → `openbci_stream(start)`.
4. Wait 30–60 s for impedance to settle; ignore first minute of data.
5. Log markers for events (`openbci_stream(marker=...)`).
6. `disconnect` when done — boards overheat if left streaming in a pouch.
