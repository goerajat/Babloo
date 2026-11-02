#!/bin/sh
# Install the Babloo motor server on the EV3 brick (ev3dev).
#
# From your laptop, with the brick on the Pi's USB link or on your Wi-Fi:
#     scp -r ev3/ robot@ev3dev.local:babloo-src
#     ssh robot@ev3dev.local 'sudo sh babloo-src/setup.sh'
# Default ev3dev password is "maker". Safe to re-run.
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
DEST=/home/robot/babloo

if [ "$(id -u)" -ne 0 ]; then
  echo "run with sudo"; exit 1
fi

mkdir -p "$DEST"
install -m 0755 -o robot -g robot "$SRC/motor_server.py" "$DEST/motor_server.py"
install -m 0644 "$SRC/babloo-motors.service" /etc/systemd/system/babloo-motors.service

python3 -m py_compile "$DEST/motor_server.py"
systemctl daemon-reload
systemctl enable babloo-motors.service
systemctl restart babloo-motors.service
sleep 2
systemctl --no-pager --lines=5 status babloo-motors.service || true

echo
echo "Motor server installed. Follow its log with:  journalctl -u babloo-motors -f"
echo "It listens on UDP 5005 and stops all motors if no packet arrives for 0.5 s."
