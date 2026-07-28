# Wearable Styling — Helmets, Caps, and the Superbike Look

OpenBCI is **visible by design**. That can be a feature: you look like a cyborg athlete, a superbike pit crew member, or a cyberpunk concert performer—not a hidden medical patient.

## The honest aesthetic

| Component | Visibility | Style notes |
|-----------|------------|-------------|
| **Ultracortex / EEG cap** | High | 3D-printed frame, electrode posts (“spikes”), wires — unmistakably *tech* |
| **Wet electrode cups** | Medium | Gel in hair; reads as “lab” or “pro athlete telemetry” |
| **Dry tips** | Medium–low | Less mess; slightly more sci-fi head-spine |
| **Cyton + USB dongle** | Medium (on body) | Usually belt pouch, small backpack, or cap-mounted enclosure |
| **Ganglion (BLE)** | Lower on-body | Smaller board; still a headband/cap |

Modern **aero road helmets** and **MTB full-face** shells already make people look like superbike aliens. An EEG rig **under or over** that silhouette reads as *telemetry*, not illness—especially with intentional industrial design (matte black, cyan accent LEDs, braided cable).

## Three physical layouts

### Layout A — “Research chic” (stock OpenBCI)

```
     [ Ultracortex frame + electrode posts ]
              │ 8–16 short leads
     [ Cyton in hip pouch ] ──USB──► [ dongle in laptop bag ]
```

- **Pros:** Best signal, standard electrode positions, reproducible science.
- **Cons:** Not discreet; gel hair; laptop nearby.

### Layout B — “Pit lane telemetry” (styled wearable)

```
  [ Aero helmet OVER printed minimal EEG strip ]
       OR
  [ Open face + Ultracortex as intentional costume ]

  [ Cyton in ventilated back-of-head mount / collar pack ]
       BLE or short USB run down spine
  [ Phone or RPi Zero in jersey pocket ] ──WiFi──► openbci-mcp server
```

- **Pros:** Strong visual identity; mobile; great for demos, streams, cycling lab.
- **Cons:** Helmet pressure on electrodes; sweat artifacts; custom mechanical design required.

### Layout C — “Concert / VR performer”

```
  [ Mark IV cap, dry electrodes, dyed hair matching rig ]
  [ Cyton in matte-black 3D-printed spine clip ]
  [ Braided USB up back into stage laptop or wireless bridge ]
  OSC ──► lights / Resonite / OBS overlay
```

- **Pros:** Audience reads it as **part of the show**; pairs with EMG wrist lights.
- **Cons:** Movement muscle noise; needs per-show calibration.

## Mounting the board

**Do not** seal the Cyton inside a closed helmet foam cavity long-term:

- Heat from streaming + radio dongle
- No access to reset / battery swap
- USB strain on micro connectors

**Better mounts:**

| Location | Use when |
|----------|----------|
| **Hip belt pouch** | Default; cable run up back |
| **Upper back spine clip** | Short cable to cap; mobile VR |
| **Handlebar / stem bag (bike lab)** | Stationary turbo trainer demos only |
| **Stage floor pack** | Tethered performance; cable as costume |

Use **strain relief**, **right-angle USB**, and a **quick-disconnect** between cap and pack.

## Cable routing that looks intentional

- **Spine channel:** Run flat ribbon or braided sleeve from occipital posts down center back (motorcycle suit vibe).
- **Color code:** Cyan/violet sleeve matching dashboard UI (matches openbci-mcp webapp).
- **Breakaway:** Magnetic USB-C or JST at shoulder for emergency helmet removal.
- **No dangling loops:** Tape service loops inside helmet edge or under jersey.

## Helmet + EEG integration notes

If combining with a **road/aero helmet**:

1. **Dry electrodes** or **small flex strip** at Fp1/Fp2/AFz/Cz only (4ch minimalist) — fewer posts piercing the helmet silhouette.
2. **Cut foam relief** at electrode sites; too much pressure = noise and headache.
3. **Sweat management:** Coban wrap, absorbent pads; expect **motion artifact** when nodding.
4. **Safety:** EEG rig must not block helmet fit or retention system; never drill structural foam without understanding impact rating (most builders use **cap outside** or **helmet over cap** for demos only).

For **turbo trainer / static superbike** sessions, helmet is optional—cap alone with fan and “pit lane” lighting sells the aesthetic.

## Visibility as UX

Users and audiences **forgive latency and calibration** when the rig reads as deliberate:

- Label channels on printed cap rails (“ALPHA”, “FOCUS”).
- Live band-power bar on phone strapped to bars (second screen).
- OSC-driven helmet LED ring (beta↑ = brighter cyan).

`openbci-mcp` dashboard on a handlebar tablet: `/api/ws/eeg` + Triggers page = pit-wall telemetry.

## Parts list (styled mobile rig)

| Item | Role |
|------|------|
| OpenBCI Cyton + dongle | EEG acquisition |
| Ultracortex Mark IV (or 4ch flex strip custom) | Electrodes |
| 3D-printed spine enclosure | Board + strain relief |
| Belt / jersey pocket phone | BLE/WiFi bridge to PC or run server on phone (advanced) |
| Optional aero helmet | Superbike silhouette |
| Optional addressable LED strip | OSC-driven from `openbci_trigger` |

## Next steps

- Signal use cases: [NEUROFEEDBACK.md](NEUROFEEDBACK.md), [VR_CREATIVE.md](VR_CREATIVE.md)
- Add wrist EMG: [HYBRID_EMG_EEG.md](HYBRID_EMG_EEG.md)
