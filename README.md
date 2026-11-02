# Babloo

A phone-controlled pet-monitoring robot: LEGO EV3 drive base + Raspberry Pi camera.

- **Design document:** [docs/DESIGN.md](docs/DESIGN.md) — components, software stack,
  architecture, safety, and the phased build plan.

## Summary

| Part | Choice |
|---|---|
| Drive base | LEGO EV3 brick with 2 large motors, running **ev3dev** |
| Brain + camera | **Raspberry Pi 4 (2 GB)** + **Camera Module 3 Wide**, on its own USB power bank |
| Pi ↔ EV3 | USB cable, Ethernet over USB, tiny UDP motor server on the brick |
| Video | **MediaMTX** → WebRTC in the phone browser (sub-second latency) |
| Controls | **FastAPI** + WebSocket + on-screen joystick (nipple.js) |
| Remote access | **Tailscale** (no port forwarding) |
| Safety | Speed cap + two independent 500 ms dead-man stops |
- **Bill of materials:** [docs/BOM.md](docs/BOM.md) — every part with Amazon links and prices.
- **Wiring:** [docs/WIRING.md](docs/WIRING.md) — every connection, with a schematic.
- **Downloads:** [downloads/](downloads/README.md) — one script fetches Imager, Pi OS, ev3dev and MediaMTX.
