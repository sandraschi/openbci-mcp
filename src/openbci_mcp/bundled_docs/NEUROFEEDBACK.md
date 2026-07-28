# Neurofeedback — Alpha, Focus, and Zen Meters

The **most realistic** home use of OpenBCI today: closed-loop feedback from band power—especially **alpha (8–12 Hz)** and **beta (13–30 Hz)**—without building a classifier.

## What alpha actually means

| Band | Hz (approx) | Typical association | Caveats |
|------|-------------|-------------------|---------|
| **Delta** | 1–4 | Deep sleep | Eyes closed, drowsy |
| **Theta** | 4–8 | Drowsy, meditation | Mixed with artifact |
| **Alpha** | 8–12 | Relaxed wakefulness, eyes closed | **Strong occipital alpha** when visual cortex idles |
| **Beta** | 13–30 | Active thinking, focus | Jaw clench mimics beta |
| **Gamma** | 30+ | Binding, noise | Often muscle contamination |

**Alpha neurofeedback** classically trains **increased alpha** (relaxation) or **alpha/theta ratios** (some meditation protocols). It is **not** mind-reading; it is **operant conditioning** on a noisy biomarker.

## Minimal channel set

| Goal | Channels | Why |
|------|----------|-----|
| Relaxation meter | O1, O2, Oz + ref | Occipital alpha |
| Focus meter | Fp1, Fp2, Cz + ref | Frontal midline beta/theta |
| Full cap feedback | 8ch Ultracortex | Spatial patterns, less single-channel fluke |

Reference and ground placement matter; follow OpenBCI wiki for your board.

## openbci-mcp workflow

### 1. Connect and stream

```
openbci_board(operation="connect", board_key="cyton", serial_port="COM3")
openbci_stream(operation="start")
```

### 2. Live band power

```
openbci_signal(operation="band_power")
```

Returns per-channel delta/theta/alpha/beta/gamma from BrainFlow `DataFilter`.

### 3. Dashboard

`http://127.0.0.1:10758` — WebSocket draws traces + band cards when streaming.

### 4. OSC feedback (sound/light)

Add trigger rule (web **Triggers** page or MCP):

```
openbci_trigger(
  operation="add_rule",
  name="Alpha calm",
  channel="*",
  band="alpha",
  operator="gt",
  threshold=0.5,
  hold_seconds=2.0,
  osc_address="/bci/alpha/calm",
  osc_value=1.0,
)
```

Route OSC to:

- **SuperCollider / Reaper** (ambient swell)
- **Home Assistant** (warm light)
- **OBS** (overlay intensity via obs-mcp + intermediate script)

## Protocol sketches

### “Zen meter” (10 min)

1. Baseline eyes open 2 min — note beta.
2. Eyes closed 2 min — note alpha rise at occipital channels.
3. Feedback on: alpha↑ drives pleasant audio (OSC).
4. Eyes open challenge 1 min — watch alpha drop; no judgment, just signal.

### Focus training (beta/theta)

- Train **beta↑ at Cz** during focused task (breath counting).
- Use **hold_seconds** on triggers to avoid flicker from single-sample spikes.
- Session length 15–20 min; fatigue increases artifact.

## Artifact hygiene (critical)

| Artifact | Looks like | Fix |
|----------|------------|-----|
| Blink | Huge delta spike | Blink training; exclude epochs |
| Jaw clench | Broadband beta/gamma | Relax jaw; EMG hybrid gate (see HYBRID_EMG_EEG.md) |
| Neck tension | Frontal drift | Posture, electrode gel refresh |
| 50/60 Hz | Line noise | Notch filter via `openbci_signal(filter, filter_type="notch")` |

## AI in neurofeedback

Modern AI helps **smooth and personalize** thresholds (e.g. adaptive baseline per session). It does **not** remove the need for:

- Consistent electrode placement
- Per-session baseline
- User learning curve

Use LLM/MCP for **coaching copy** and **session logging**, not as the primary signal estimator—BrainFlow band power is the stable first layer.

## Realistic expectations

| Expectation | Realistic? |
|-------------|------------|
| Feel when you relax vs tense in feedback | **Yes**, most users |
| Match clinical neurofeedback clinic quality | Partial; SNR lower at home |
| Control computer by alpha alone | **No** — use alpha for **modulation**, not clicks |
| Beautiful zen app in one afternoon | **Yes** with dashboard + OSC |

## Related

- [USAGE_SCENARIOS.md](USAGE_SCENARIOS.md)
- [VR_CREATIVE.md](VR_CREATIVE.md) — same signals, artistic output
- [WEARABLE_STYLING.md](WEARABLE_STYLING.md) — wearing rig during practice
