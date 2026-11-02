#!/usr/bin/env python3
"""Babloo control server: runs on the Raspberry Pi.

* Serves the phone page (static/index.html) with optional HTTP basic auth.
* Accepts joystick + tilt input over a WebSocket at ~20 Hz:
      {"x": -1..1, "y": -1..1, "tilt": -1|0|1}        (y forward positive)
      {"stop": true}                                   (big red button)
      {"tilt_home": true}
  and sends back a status object every few ticks.
* Mixes joystick into tank speeds, clamps to MAX_SPEED, and sends UDP JSON
  to the EV3 motor server at a fixed 20 Hz.

SAFETY (do not remove):
* Dead-man: if no joystick message arrives for DEADMAN_S, the Pi sends
  stop packets. The EV3 has its own, independent timer (ev3/motor_server.py).
* Speed cap MAX_SPEED (percent). Default 35.
* STOP latches: after a stop, movement is ignored until the joystick has
  been released (x = y = 0 and tilt = 0 received) once.

Configuration via environment (see pi/setup.sh, /etc/babloo/control.env):
  BABLOO_BIND        address to listen on (default 0.0.0.0; setup.sh --lockdown sets the Tailscale IP)
  BABLOO_PORT        HTTP port (default 8000)
  BABLOO_EV3_HOST    EV3 address; default: learned from the EV3's status packets on UDP 5006
  BABLOO_EV3_PORT    default 5005
  BABLOO_MAX_SPEED   default 35
  BABLOO_USER / BABLOO_PASS   enable basic auth on the page when both set
  BABLOO_WEBRTC_PORT MediaMTX WebRTC port shown to the page (default 8889)
"""
import asyncio
from contextlib import asynccontextmanager
import json
import logging
import os
import secrets
import socket
import time
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect, status
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles

# ---- configuration --------------------------------------------------------
BIND = os.environ.get("BABLOO_BIND", "0.0.0.0")
PORT = int(os.environ.get("BABLOO_PORT", "8000"))
EV3_HOST_FIXED = os.environ.get("BABLOO_EV3_HOST") or None
EV3_PORT = int(os.environ.get("BABLOO_EV3_PORT", "5005"))
STATUS_PORT = int(os.environ.get("BABLOO_STATUS_PORT", "5006"))
MAX_SPEED = max(5, min(60, int(os.environ.get("BABLOO_MAX_SPEED", "35"))))
WEBRTC_PORT = int(os.environ.get("BABLOO_WEBRTC_PORT", "8889"))
AUTH_USER = os.environ.get("BABLOO_USER") or None
AUTH_PASS = os.environ.get("BABLOO_PASS") or None

SEND_HZ = 20
DEADMAN_S = 0.5          # no joystick message for this long -> stop
EV3_LOST_S = 2.0         # no status from the EV3 for this long -> "link lost"
STATIC_DIR = Path(__file__).resolve().parent / "static"

log = logging.getLogger("babloo")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


# ---- joystick -> tank mixing ----------------------------------------------
def joystick_to_tank(x: float, y: float, max_speed: int = MAX_SPEED) -> tuple[int, int]:
    """x, y in -1..1 (right / forward positive) -> (left, right) percent, capped."""
    x = max(-1.0, min(1.0, float(x)))
    y = max(-1.0, min(1.0, float(y)))
    left = (y + x) * max_speed
    right = (y - x) * max_speed
    scale = max(1.0, abs(left) / max_speed, abs(right) / max_speed)
    return int(round(left / scale)), int(round(right / scale))


def sign(v) -> int:
    try:
        v = float(v)
    except (TypeError, ValueError):
        return 0
    return 1 if v > 0 else (-1 if v < 0 else 0)


# ---- shared robot state ---------------------------------------------------
class State:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.tilt = 0
        self.last_input = 0.0        # monotonic time of last joystick message
        self.estop = False           # latched until joystick released
        self.tilt_home_pending = False
        self.ev3_addr = (EV3_HOST_FIXED, EV3_PORT) if EV3_HOST_FIXED else None
        self.ev3_status: dict = {}
        self.ev3_last_seen = 0.0
        self.sent = (0, 0, 0)
        self.clients: set[WebSocket] = set()

    def set_input(self, x, y, tilt):
        self.x, self.y, self.tilt = x, y, sign(tilt)
        self.last_input = time.monotonic()
        if self.estop and self.x == 0 and self.y == 0 and self.tilt == 0:
            self.estop = False
            log.info("STOP released")

    def stop(self, reason: str):
        self.x = self.y = 0.0
        self.tilt = 0
        if not self.estop:
            log.warning("STOP (%s)", reason)
        self.estop = True

    def command(self) -> dict:
        """What to send to the EV3 right now."""
        if self.tilt_home_pending:
            self.tilt_home_pending = False
            return {"left": 0, "right": 0, "tilt_home": True}
        stale = (time.monotonic() - self.last_input) > DEADMAN_S
        if self.estop or stale:
            return {"left": 0, "right": 0, "tilt": 0}
        left, right = joystick_to_tank(self.x, self.y)
        return {"left": left, "right": right, "tilt": self.tilt}

    def ev3_ok(self) -> bool:
        return (time.monotonic() - self.ev3_last_seen) < EV3_LOST_S

    def public(self) -> dict:
        stale = (time.monotonic() - self.last_input) > DEADMAN_S
        return {
            "ev3": "ok" if self.ev3_ok() else "lost",
            "ev3_addr": self.ev3_addr[0] if self.ev3_addr else None,
            "estop": self.estop,
            "deadman": stale,
            "left": self.sent[0], "right": self.sent[1], "tilt": self.sent[2],
            "max_speed": MAX_SPEED,
            "tilt_pos": self.ev3_status.get("tilt_pos"),
            "tilt_min": self.ev3_status.get("tilt_min"),
            "tilt_max": self.ev3_status.get("tilt_max"),
            "batt_v": self.ev3_status.get("batt_v"),
            "clients": len(self.clients),
        }


state = State()
WS_TOKEN = secrets.token_urlsafe(24)   # page gets it after basic auth; WebSocket must present it


# ---- UDP link to the EV3 --------------------------------------------------
class Ev3Link(asyncio.DatagramProtocol):
    """One socket bound to STATUS_PORT: we send commands from it and receive
    status packets (replies and the EV3's 1 Hz announcements) on it."""

    def __init__(self):
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        try:
            msg = json.loads(data.decode("utf-8"))
        except ValueError:
            return
        if not isinstance(msg, dict) or msg.get("babloo") != "ev3":
            return
        if not EV3_HOST_FIXED and (state.ev3_addr is None or state.ev3_addr[0] != addr[0]):
            log.info("EV3 found at %s", addr[0])
        if not EV3_HOST_FIXED:
            state.ev3_addr = (addr[0], EV3_PORT)
        state.ev3_status = msg
        state.ev3_last_seen = time.monotonic()

    def send(self, cmd: dict):
        if self.transport is None or state.ev3_addr is None:
            return
        try:
            self.transport.sendto(json.dumps(cmd).encode("utf-8"), state.ev3_addr)
        except OSError as e:
            log.debug("sendto failed: %s", e)


link = Ev3Link()


async def sender_loop():
    """Fixed-rate command stream to the EV3 (feeds its dead-man timer only
    while a phone is connected) plus status pushes to connected pages."""
    tick = 0
    period = 1.0 / SEND_HZ
    while True:
        cmd = state.command()
        if state.clients or cmd != {"left": 0, "right": 0, "tilt": 0} or tick % SEND_HZ == 0:
            link.send(cmd)
        state.sent = (cmd.get("left", 0), cmd.get("right", 0), cmd.get("tilt", 0))
        tick += 1
        if tick % 5 == 0 and state.clients:           # 4 Hz status to the page
            payload = json.dumps({"status": state.public()})
            for ws in list(state.clients):
                try:
                    await ws.send_text(payload)
                except Exception:
                    state.clients.discard(ws)
        await asyncio.sleep(period)


# ---- web app --------------------------------------------------------------
@asynccontextmanager
async def lifespan(_app: FastAPI):
    loop = asyncio.get_running_loop()
    await loop.create_datagram_endpoint(lambda: link, local_addr=("0.0.0.0", STATUS_PORT),
                                        reuse_port=hasattr(socket, "SO_REUSEPORT"))
    task = asyncio.create_task(sender_loop())
    log.info("Babloo control on http://%s:%d  max_speed=%d%%  ev3=%s  auth=%s",
             BIND, PORT, MAX_SPEED, EV3_HOST_FIXED or "auto", "on" if AUTH_USER else "off")
    try:
        yield
    finally:
        task.cancel()
        for _ in range(3):                       # leave the robot stopped
            link.send({"left": 0, "right": 0, "tilt": 0})
            await asyncio.sleep(0.05)


app = FastAPI(title="Babloo", docs_url=None, redoc_url=None, lifespan=lifespan)
basic = HTTPBasic(auto_error=False)


def require_auth(request: Request, creds: HTTPBasicCredentials | None = Depends(basic)):
    if not (AUTH_USER and AUTH_PASS):
        return
    ok = creds is not None and secrets.compare_digest(creds.username, AUTH_USER) \
        and secrets.compare_digest(creds.password, AUTH_PASS)
    if not ok:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "auth required",
                            headers={"WWW-Authenticate": 'Basic realm="Babloo"'})


@app.get("/", response_class=HTMLResponse, dependencies=[Depends(require_auth)])
async def index():
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    cfg = {"token": WS_TOKEN, "webrtcPort": WEBRTC_PORT, "maxSpeed": MAX_SPEED, "sendHz": SEND_HZ}
    return html.replace("__BABLOO_CONFIG__", json.dumps(cfg))


@app.get("/api/status", dependencies=[Depends(require_auth)])
async def api_status():
    return JSONResponse(state.public())


@app.post("/api/stop", dependencies=[Depends(require_auth)])
async def api_stop():
    state.stop("http")
    return JSONResponse(state.public())


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket, token: str = ""):
    if not secrets.compare_digest(token, WS_TOKEN):
        await ws.close(code=4401)
        return
    await ws.accept()
    state.clients.add(ws)
    log.info("phone connected (%d)", len(state.clients))
    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except ValueError:
                continue
            if not isinstance(msg, dict):
                continue
            if msg.get("stop"):
                state.stop("button")
            elif msg.get("tilt_home"):
                state.tilt_home_pending = True
                state.set_input(0, 0, 0)
            else:
                try:
                    state.set_input(float(msg.get("x", 0)), float(msg.get("y", 0)), msg.get("tilt", 0))
                except (TypeError, ValueError):
                    state.stop("bad message")
    except WebSocketDisconnect:
        pass
    finally:
        state.clients.discard(ws)
        if not state.clients:
            state.stop("phone disconnected")
        log.info("phone disconnected (%d left)", len(state.clients))


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=BIND, port=PORT, log_level="info")
