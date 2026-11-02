#!/usr/bin/env python3
"""Babloo motor server: runs on the EV3 brick under ev3dev.

Listens for UDP JSON packets from the Raspberry Pi and drives the motors:

    {"left": -100..100, "right": -100..100, "tilt": -1|0|1}

* left / right are percentages of full speed for the two drive motors.
* tilt is a direction for the camera-tilt motor: +1 up, -1 down, 0 hold.
  It can also be an integer in -100..100 (interpreted as a direction).
* {"tilt_home": true} returns the camera to its power-on angle.

Every packet is answered with a status packet, and a status packet is also
broadcast to the Pi (10.42.0.1) once a second so the Pi learns our address:

    {"babloo": "ev3", "left": .., "right": .., "tilt_pos": .., "batt_v": ..}

SAFETY (do not remove):
* Dead-man: if no packet arrives for TIMEOUT_S, every motor is stopped.
  This is independent of the identical timer on the Pi.
* Any exception stops every motor.
* Drive motors brake when stopped; the tilt motor holds its position.
* The tilt motor is kept within TILT_MIN_DEG..TILT_MAX_DEG of its start angle.
* The EV3 back button stops the motors and exits (systemd restarts it).

Python 3.5 compatible (ev3dev-stretch ships 3.5): no f-strings, no dataclasses.
"""
import json
import socket
import sys
import time

from ev3dev2.motor import MoveTank, Motor, OUTPUT_A, OUTPUT_B, OUTPUT_D, SpeedPercent

# ---- wiring (see docs/WIRING.md) ------------------------------------------
LEFT_PORT = OUTPUT_B
RIGHT_PORT = OUTPUT_D
TILT_PORT = OUTPUT_A
INVERT_LEFT = False     # both drive motors are mounted the same way
INVERT_RIGHT = False
INVERT_TILT = False     # set True if "up" on the page tilts the camera down

# ---- behaviour ------------------------------------------------------------
UDP_PORT = 5005
TIMEOUT_S = 0.5         # dead-man: stop if silent for this long
MAX_DRIVE_PCT = 50      # hard ceiling on the brick; the Pi applies the real (lower) cap
TILT_SPEED_PCT = 20     # slow, so the camera does not slam against its stops
TILT_MIN_DEG = -60      # soft travel limits, degrees of motor shaft from power-on angle
TILT_MAX_DEG = 60
STATUS_HOST = "10.42.0.1"   # the Pi, as seen over the shared USB link
STATUS_PORT = 5006
STATUS_PERIOD_S = 1.0


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def to_int(v, default=0):
    try:
        return int(round(float(v)))
    except (TypeError, ValueError):
        return default


class Robot(object):
    def __init__(self):
        self.tank = MoveTank(LEFT_PORT, RIGHT_PORT)
        self.tilt = Motor(TILT_PORT)
        self.tilt.stop_action = Motor.STOP_ACTION_HOLD
        self.tilt.position = 0          # power-on angle is the reference
        self.left = 0
        self.right = 0
        self.tilt_dir = 0
        self.moving = False
        try:
            from ev3dev2.power import PowerSupply
            self.power = PowerSupply()
        except Exception:
            self.power = None
        try:
            from ev3dev2.button import Button
            self.button = Button()
        except Exception:
            self.button = None
        self.stop_all(force=True)

    # -- drive --------------------------------------------------------------
    def drive(self, left, right):
        left = clamp(to_int(left), -MAX_DRIVE_PCT, MAX_DRIVE_PCT)
        right = clamp(to_int(right), -MAX_DRIVE_PCT, MAX_DRIVE_PCT)
        self.left, self.right = left, right
        if left == 0 and right == 0:
            if self.moving:
                self.tank.off(brake=True)
                self.moving = False
            return
        l = -left if INVERT_LEFT else left
        r = -right if INVERT_RIGHT else right
        self.tank.on(SpeedPercent(l), SpeedPercent(r))
        self.moving = True

    # -- camera tilt --------------------------------------------------------
    def tilt_to(self, direction):
        d = to_int(direction)
        d = 1 if d > 0 else (-1 if d < 0 else 0)
        pos = self.tilt.position
        if d > 0 and pos >= TILT_MAX_DEG:
            d = 0
        if d < 0 and pos <= TILT_MIN_DEG:
            d = 0
        if d == 0:
            if self.tilt_dir != 0:
                self.tilt.stop()        # STOP_ACTION_HOLD keeps the angle
            self.tilt_dir = 0
            return
        if d == self.tilt_dir:
            return                      # already moving that way; limits re-checked above
        speed = TILT_SPEED_PCT * d * (-1 if INVERT_TILT else 1)
        self.tilt.on(SpeedPercent(speed))
        self.tilt_dir = d

    def tilt_home(self):
        self.tilt_dir = 0
        self.tilt.on_to_position(SpeedPercent(TILT_SPEED_PCT), 0, brake=True, block=False)

    # -- safety -------------------------------------------------------------
    def stop_all(self, force=False):
        """Stop every motor. Idempotent: an idle brick is not re-stopped twice a
        second, but force=True (startup, errors, exit) always sends the commands."""
        if not force and not self.moving and self.tilt_dir == 0:
            return
        self.left = self.right = self.tilt_dir = 0
        self.moving = False
        try:
            self.tank.off(brake=True)
        finally:
            self.tilt.stop()

    def back_pressed(self):
        try:
            return self.button is not None and self.button.backspace
        except Exception:
            return False

    # -- status -------------------------------------------------------------
    def status(self):
        batt = None
        if self.power is not None:
            try:
                batt = round(self.power.measured_volts, 2)
            except Exception:
                batt = None
        try:
            tpos = self.tilt.position
        except Exception:
            tpos = None
        return {"babloo": "ev3", "left": self.left, "right": self.right,
                "tilt_pos": tpos, "tilt_min": TILT_MIN_DEG, "tilt_max": TILT_MAX_DEG,
                "batt_v": batt, "t": round(time.time(), 2)}


def main():
    robot = Robot()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", UDP_PORT))
    sock.settimeout(TIMEOUT_S)
    print("babloo motor server: UDP %d, dead-man %.1f s, L=%s R=%s tilt=%s"
          % (UDP_PORT, TIMEOUT_S, LEFT_PORT, RIGHT_PORT, TILT_PORT))
    sys.stdout.flush()

    last_status = 0.0
    stopped_by_timeout = True
    try:
        while True:
            if robot.back_pressed():
                print("back button: stopping and exiting")
                break
            try:
                data, addr = sock.recvfrom(512)
            except socket.timeout:
                if not stopped_by_timeout:
                    print("dead-man: no packet for %.1f s, motors stopped" % TIMEOUT_S)
                    sys.stdout.flush()
                robot.stop_all()
                stopped_by_timeout = True
                addr = None
            else:
                try:
                    cmd = json.loads(data.decode("utf-8"))
                    if not isinstance(cmd, dict):
                        raise ValueError("not an object")
                    if cmd.get("tilt_home"):
                        robot.tilt_home()
                    else:
                        robot.tilt_to(cmd.get("tilt", 0))
                    robot.drive(cmd.get("left", 0), cmd.get("right", 0))
                    stopped_by_timeout = False
                except Exception as e:      # bad packet or motor error: stop
                    print("bad packet from %s: %r (%s)" % (addr, data[:80], e))
                    sys.stdout.flush()
                    robot.stop_all(force=True)
                    stopped_by_timeout = True

            now = time.time()
            if addr is not None or now - last_status >= STATUS_PERIOD_S:
                payload = json.dumps(robot.status()).encode("utf-8")
                if addr is not None:
                    try:
                        sock.sendto(payload, addr)
                    except OSError:
                        pass
                if now - last_status >= STATUS_PERIOD_S:
                    last_status = now
                    try:
                        sock.sendto(payload, (STATUS_HOST, STATUS_PORT))
                    except OSError:
                        pass
    finally:
        robot.stop_all(force=True)
        print("motors stopped, exiting")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
