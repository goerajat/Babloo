# Babloo: project context for Claude Code sessions

Read this first. It is the hand-off from the design sessions and is kept current.

## What this project is

A phone-controlled robot with a camera for checking on pets when nobody is home.
LEGO EV3 brick with two large motors drives; a Raspberry Pi 4 on top does camera, video
streaming, the web control UI and remote access. Full details:

- `docs/DESIGN.md`: architecture, software stack, safety design, phased build plan, code sketches
- `docs/BOM.md`: every part, with Amazon links, prices, and what has been bought
- `docs/WIRING.md` and `docs/wiring.svg`: every physical connection
- `downloads/`: scripts that fetch Imager, Pi OS, ev3dev, MediaMTX onto the laptop

## Decisions already made (do not re-open without asking)

| Area | Decision | Why |
|---|---|---|
| Brick OS | **ev3dev** on microSD, stock firmware untouched | Full Linux, Python motor control, on-brick watchdog |
| Pi | **Raspberry Pi 4 Model B 1 GB** from pishop.us, $35 | Hardware H.264 encoder; 1 GB is ample; 2 GB is $67.50 after Oct 2026 price rise; Pi Zero 2 W sold out; Pi 5 has no HW encoder |
| Camera | **Arducam Day-Night Vision, OV5647, 130° diag, motorised IR-cut, IR LEDs included** (B07X1VGQSL) | Correct daytime colour plus real night vision. Not auto-detected: needs `camera_auto_detect=0` and `dtoverlay=ov5647` |
| Pi power | **Amazon Basics 20 000 mAh 3-port bank** (B0FFM4BY6C), fed from a USB-C port | 5 V/3 A on USB-C; ~12–14 h runtime. INIU 10 Ah is the lighter alternative |
| Pi ↔ EV3 | USB-A to mini-USB-B cable, Ethernet-over-USB, Pi is host, Pi shares `usb0` via NetworkManager (`ipv4.method shared`) | No Wi-Fi dongle or Bluetooth pairing |
| Video | **MediaMTX** `rpiCamera` source → **WebRTC** in the phone browser, 1280×720 @ 25 fps, 1.5 Mbps | Sub-second latency, no custom code |
| Control | **FastAPI + uvicorn** on the Pi, WebSocket from a nipple.js joystick page, UDP JSON `{left,right}` to a ~50-line `motor_server.py` on the EV3 using `ev3dev2.motor.MoveTank` | Simple, two independent 500 ms dead-man timers |
| Remote access | **Tailscale** on Pi and phone; services bind to the Tailscale interface; no port forwarding | Private, WebRTC passes through |
| Motors | Left → port **B**, right → port **C**; speed cap ~35 % | Pet safety |
| Case | Pi-Blox LEGO-studded Pi 4 case | Attaches to the EV3 with plates |
| Soldering | None anywhere in the build | |

## Status (as of 2 Nov 2026)

Done:
- Design, BOM, wiring guide written and committed.
- EV3 chassis built; motors on B and C verified on stock firmware.
- Tailscale installed on phone and laptop.
- Ordered and in hand or arriving: Arducam Day-Night camera, Amazon Basics 20 Ah bank, Pi-Blox case, Sabrent card reader, Pi 4 1 GB (pishop.us).
- Owned: 2× Lexar 32 GB A1 microSDHC (one for Pi, one for EV3), EV3 kit.

Waiting on delivery: Pi 4, camera, card reader.

Still to buy: USB-A to mini-USB cable (1 ft), Pi 4 heatsinks, hook-and-loop ties,
6× AA NiMH + charger unless the LEGO 45501 pack is available.

## Next steps, in order

1. On the user's PC: run `downloads\download.ps1` (Windows) or `downloads/download.sh` to fetch
   Imager, Pi OS Lite 64-bit, the ev3dev EV3 image and MediaMTX. Not yet run.
2. **Write the software** (no hardware needed), into the layout proposed in `docs/DESIGN.md` §6:
   - `ev3/motor_server.py` + `ev3/babloo-motors.service`: UDP listener, MoveTank, 500 ms watchdog, stop on any error
   - `pi/control_server.py`: FastAPI, serves `pi/static/index.html`, WebSocket at 20 Hz, joystick→tank mixing with speed cap, 500 ms dead-man → send stop, forwards UDP to EV3 at 10.42.0.x (discover via `ip neigh` or fixed lease)
   - `pi/static/index.html`: MediaMTX WebRTC player (`http://<pi>:8889/cam`) embedded + nipple.js joystick + big STOP button; mobile-first, `playsinline muted`
   - `pi/mediamtx.yml`, `pi/systemd/*.service`, `pi/requirements.txt`
   - `pi/setup.sh`: installs MediaMTX, Tailscale, python deps, NetworkManager shared connection for `usb0`, enables services, writes the two camera lines to `/boot/firmware/config.txt`
   - `ev3/setup.sh`: copies motor server, enables service
3. When hardware arrives: flash both cards with Imager (ev3dev via "Use custom"), label them,
   boot, run `pi/setup.sh`, confirm video on the phone (phase 0), then drive (phase 1), then
   Tailscale-only access (phase 2). Phases are detailed in `docs/DESIGN.md` §7.

## Conventions

- Work on branch `claude/pet-monitor-robot-design-28m7hd` unless told otherwise; commit and push there.
- Keep docs in sync with decisions: when a part or approach changes, update `docs/BOM.md` and
  `docs/DESIGN.md` in the same commit.
- Prices in docs are approximate USD; note the date when adding availability information.
- No soldering, no GPIO wiring. Every connection is a plug or a screw.
- Safety features (speed cap, both dead-man timers, STOP button) are not optional and must not
  be removed to "simplify".

## Environment notes

- The user's PC is Windows ("mini-pc"). Cloud sessions cannot attach to it via Remote Control;
  work on it from a local Claude Code session started in the `Babloo` folder.
- Cloud sessions in this project have had no network access to amazon.com, raspberrypi.com,
  ev3dev.org or GitHub release downloads; use web search for availability, and don't try to
  download images in the cloud. Images are hundreds of MB and must never be committed
  (`downloads/files/` is gitignored).
