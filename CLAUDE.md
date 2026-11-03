# Babloo: project context for Claude Code sessions

Read this first. It is the hand-off from the design sessions and is kept current.

## What this project is

A phone-controlled robot with a camera for checking on pets when nobody is home.
LEGO EV3 brick with two large motors drives and a third motor tilts the camera; a Raspberry Pi 4
on top does camera, video streaming, the web control UI and remote access. Full details:

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
| Control | **FastAPI + uvicorn** on the Pi, WebSocket from a self-contained joystick page, UDP JSON `{left,right,tilt}` to a small `motor_server.py` on the EV3 using `ev3dev2.motor.MoveTank` plus a tilt `Motor` | Simple, two independent 500 ms dead-man timers |
| Remote access | **Tailscale** on Pi and phone; services bind to the Tailscale interface; no port forwarding | Private, WebRTC passes through |
| Motors | Left drive → port **B**, right drive → port **D**, camera tilt → port **A**; both drive motors mounted the same way (no inversion), no gearing; brake on stop; drive speed cap ~35 % | Pet safety; user-confirmed 2 Nov 2026 |
| Camera tilt | Motor on **A** tilts the camera up/down; UP/DOWN buttons on the web page; slow (~20 %), position-limited, stops when released and on dead-man | Camera is front-mounted; tilt lets you look at the floor or the sofa |
| Case | Pi-Blox LEGO-studded Pi 4 case | Attaches to the EV3 with plates |
| Soldering | None anywhere in the build | |

## Status (as of 2 Nov 2026)

Done:
- Design, BOM, wiring guide written and committed.
- EV3 chassis built; drive motors on B and D verified on stock firmware; tilt motor on A.
- Tailscale installed on phone and laptop.
- Ordered and in hand or arriving: Arducam Day-Night camera, Amazon Basics 20 Ah bank, Pi-Blox case, Sabrent card reader, Pi 4 1 GB (pishop.us).
- Owned: 2× Lexar 32 GB A1 microSDHC (one for Pi, one for EV3), EV3 kit.

All ordered parts arrived 2 Nov 2026.

**Phase 0 done (2 Nov 2026 evening):** Pi flashed (user `babloo`, key-only SSH from this PC, hostname
`babloo.local`, Wi-Fi 192.168.1.245), `pi/setup.sh` run, MediaMTX streaming 1280x720 H.264 via the hardware
encoder, verified live in a browser at `http://192.168.1.245:8889/cam/`. Camera auto-detected on Pi OS Trixie
without config.txt changes. Tailscale installed but not logged in. `sudo` on the Pi needs the user's password,
so anything with sudo runs in the user's own terminal, not from Claude.

**Phase 1 bring-up (2 Nov 2026, late):** EV3 card flashed from the extracted `.img` (Imager wrote nothing
from the nested zip). ev3dev boots; the USB link had to be connected once from the brick's menu
(Wireless and Networks > All Network Connections > Wired > Connect). Brick is `10.42.0.99` on `usb0`,
hostname `ev3dev`, Python 3.5.3, large motors detected on A, B, D. Motor server installed and active;
control server reports `ev3: ok`, battery 8.27 V. Reach the brick from this PC with
`ssh -J babloo@babloo.local robot@10.42.0.99` (key auth; `sudo` there still needs password `maker`).
Both services can be restarted without sudo by killing their main PID (systemd restarts them).
First drive from the phone not yet done.

Still to buy: USB-A to mini-USB cable (1 ft), Pi 4 heatsinks, hook-and-loop ties,
6× AA NiMH + charger unless the LEGO 45501 pack is available.

## Software (written 2 Nov 2026, tested against a fake EV3 on the PC, not yet on hardware)

| File | Role |
|---|---|
| `ev3/motor_server.py` | UDP 5005 listener on the brick. `{"left","right","tilt"}` → `MoveTank(B, D)` + tilt `Motor(A)`. Brake on stop, tilt holds, soft tilt limits ±60°, 500 ms dead-man, back button exits. Replies with a status packet and announces itself to `10.42.0.1:5006` every second so the Pi learns its address. Python 3.5 compatible |
| `ev3/babloo-motors.service`, `ev3/setup.sh` | systemd unit (user `robot`) and installer: `scp -r ev3/ robot@ev3dev.local:babloo-src && ssh robot@ev3dev.local 'sudo sh babloo-src/setup.sh'` |
| `pi/control_server.py` | FastAPI + uvicorn. Serves the page (optional basic auth), WebSocket `/ws?token=` (token injected into the page), 20 Hz UDP sender, speed cap 35 %, 500 ms dead-man, STOP latch (ignores joystick until released), EV3 auto-discovery on UDP 5006. Config via `/etc/babloo/control.env` |
| `pi/static/index.html` | Self-contained page: MediaMTX WebRTC iframe (`http://<host>:8889/cam/`), hand-rolled pointer-event joystick (no nipple.js dependency, works offline), hold-to-tilt ▲ ▼ and ⦿ centre buttons, STOP, status bar (link, EV3, battery, L/R). Keyboard WASD / Q E / space for laptop testing |
| `pi/mediamtx.yml` | `rpiCamera` 1280×720 @ 25 fps, 1.5 Mbps, WebRTC only, everything else off |
| `pi/systemd/*.service`, `pi/requirements.txt`, `pi/setup.sh` | Installer run as root on the Pi: packages, `/opt/babloo` venv, MediaMTX binary, `babloo-usb` shared connection, camera overlay lines, Tailscale, services. `--lockdown` binds everything to the Tailscale IP, `--open` reverts, `--auth USER` sets basic auth |

Test harness used on the PC (not committed): a fake `ev3dev2` package plus a websocket client
that checked mixing (35/35 forward, 35/−35 spin), both dead-man paths, the STOP latch, tilt and
tilt-home, and token rejection. Page layout checked at phone size in both orientations.

## Next steps, in order

1. ~~Flash the Pi card, run setup, phase 0 video~~ done.
2. Flash the EV3 card with Imager ("Use custom", the ev3dev zip), label it. Re-copy `pi/mediamtx.yml`
   to the Pi and `sudo systemctl restart mediamtx` (moq disabled, H264 level key renamed).
3. EV3: plug in USB, run `ev3/setup.sh` as above, open `http://<pi>:8000/`, confirm the EV3 dot
   turns green, drive (phase 1). Verify on the bench: pulling the USB cable stops the motors
   within 0.5 s; closing the browser tab stops them; STOP latches until the stick is released.
   If "up" tilts the camera down, set `INVERT_TILT = True`; tune `TILT_MIN_DEG` / `TILT_MAX_DEG`.
4. `sudo tailscale up`, then `sudo bash pi/setup.sh --lockdown --auth <user>` (phase 2); test on
   mobile data with Wi-Fi off.

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
