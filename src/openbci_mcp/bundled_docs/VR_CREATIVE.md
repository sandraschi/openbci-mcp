# VR, Creative, and Live Performance

Turn band power and events into **visible, audible, shareable** experiences—where OpenBCI shines for hobbyists and performers.

## Why VR/creative fits EEG well

- Audience **expects** visible gear (see [WEARABLE_STYLING.md](WEARABLE_STYLING.md)).
- **Latency ~100 ms** is fine for mood, lighting, avatar parameters—not for competitive FPS aim.
- **OSC** is the lingua franca of VR, VJ, and stage tools—`openbci-mcp` triggers map cleanly.

## Architecture

```
OpenBCI Cyton
    → openbci-mcp (band_power, triggers)
    → OSC UDP (default 127.0.0.1:9000)
    → osc-mcp / Resonite / VRChat / TouchDesigner / Reaper
```

See [OSC_INTEGRATION.md](OSC_INTEGRATION.md) for fleet ports and pairing.

## Mapping ideas

| Brain metric | Creative parameter | Example OSC address |
|--------------|-------------------|---------------------|
| Alpha ↑ | Calm sky / slow particles | `/world/calm` |
| Beta ↑ | Avatar emissive intensity | `/avatar/focus` |
| Theta ↑ | Dreamy post-processing | `/fx/blur` |
| Raw burst (artifact gated) | Beat drop trigger | `/dj/strobe` |
| Marker event | Scene change | `/scene/next` |

Use **hold_seconds** on triggers to avoid epileptic flicker from noise.

## Resonite / VRChat

1. Run **osc-mcp** listener or in-world OSC bridge.
2. Map `/bci/focus` → avatar parameter or particle rate.
3. Wear cap **outside** VR headset strap where possible; pressure shifts electrodes.

**Tip:** SSVEP menus in VR require **controlled flicker** in UI—test comfort first.

## OBS / streaming (“pit lane” stream)

| Signal | OBS use |
|--------|---------|
| Band power bars | Browser dock or obs-mcp overlay |
| Trigger events | Scene switch, source visibility |
| Synthetic board | Rehearse layout without hardware |

Dashboard at `:10758` + OBS capture of band-power panel = **telemetry overlay** for superbike aesthetic streams.

## Live music

```
openbci_trigger → OSC → Reaper (reaper-mcp) or SuperCollider
```

- Alpha drives **filter cutoff** ( mellow ).
- Beta drives **rhythm density**.
- EMG clench (hybrid) triggers **one-shot samples**.

## Installation art

- Multicast stream to multiple consumers:

```
openbci_export(operation="streamer_multicast")
```

- Gallery PC runs classifier + projection mapping.
- Markers from phone app (`/api/board` POST) for curator events.

## Session design for performances

1. **Rehearsal on synthetic board** — layout triggers without fatigue.
2. **Show-day baseline** — 5 min eyes closed; retune thresholds.
3. **Fallback preset** — if SNR collapses, OSC manual override.
4. **Cable choreography** — braid as costume (WEARABLE_STYLING.md).

## openbci-mcp checklist

| Task | How |
|------|-----|
| Live dashboard | `start.bat` → port 10758 |
| Auto OSC | Triggers page rules |
| Manual test pulse | `openbci_trigger(send_osc)` |
| Log show | `openbci_export(streamer_file)` |
| Agent setup | `agentic_openbci_workflow` |

## Related

- [NEUROFEEDBACK.md](NEUROFEEDBACK.md) — same signals, personal feedback
- [HYBRID_EMG_EEG.md](HYBRID_EMG_EEG.md) — fist gestures + brain mood
- [BCI_CONTROL.md](BCI_CONTROL.md) — when you need discrete choices, not vibes
