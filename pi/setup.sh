#!/bin/bash
# Babloo Raspberry Pi setup. Run ON THE PI, as root, from a copy of the pi/ folder:
#
#     scp -r pi/ downloads/files/mediamtx_*_linux_arm64.tar.gz <user>@<pi>:
#     ssh <user>@<pi> 'sudo bash pi/setup.sh'
#
# Idempotent: re-run after changing any file. Options:
#     --lockdown     bind the control page and WebRTC to the Tailscale IP only (phase 2)
#     --open         back to 0.0.0.0 (phase 0/1, home Wi-Fi)
#     --auth USER    set basic-auth user; prompts for the password
#
# What it does:
#   1. apt packages (python3-venv, network-manager, rpicam-apps, libcamera)
#   2. /opt/babloo: venv + control_server.py + static/
#   3. MediaMTX binary -> /usr/local/bin, config -> /etc/babloo/mediamtx.yml
#   4. NetworkManager "babloo-usb" shared connection on usb0 (EV3 gets 10.42.0.x)
#   5. camera lines in /boot/firmware/config.txt (Arducam OV5647 is not auto-detected)
#   6. Tailscale (installed if missing; you still run `tailscale up` once)
#   7. systemd units enabled and (re)started
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
APP=/opt/babloo
ETC=/etc/babloo
ENVF=$ETC/control.env
CONFIG_TXT=/boot/firmware/config.txt
[ -f "$CONFIG_TXT" ] || CONFIG_TXT=/boot/config.txt

if [ "$(id -u)" -ne 0 ]; then echo "run with sudo"; exit 1; fi

MODE=""; AUTH_USER=""
while [ $# -gt 0 ]; do
  case "$1" in
    --lockdown) MODE=lockdown ;;
    --open) MODE=open ;;
    --auth) AUTH_USER="$2"; shift ;;
    *) echo "unknown option $1"; exit 1 ;;
  esac
  shift
done

say() { printf '\n== %s\n' "$*"; }

# ---- 1. packages ------------------------------------------------------------
say "apt packages"
apt-get update -qq
# rpicam-apps-lite is preinstalled on Pi OS Lite; never pin a libcamera version (it moves between releases).
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq python3-venv python3-pip network-manager rpicam-apps-lite curl

# ---- 2. app ----------------------------------------------------------------
say "control server -> $APP"
id -u babloo >/dev/null 2>&1 || useradd --system --home "$APP" --shell /usr/sbin/nologin babloo
mkdir -p "$APP/static" "$ETC"
install -m 0644 "$SRC/control_server.py" "$APP/control_server.py"
install -m 0644 "$SRC/static/index.html" "$APP/static/index.html"
install -m 0644 "$SRC/requirements.txt" "$APP/requirements.txt"
[ -d "$APP/venv" ] || python3 -m venv "$APP/venv"
"$APP/venv/bin/pip" install -q --upgrade pip
"$APP/venv/bin/pip" install -q -r "$APP/requirements.txt"
chown -R babloo:babloo "$APP"

if [ ! -f "$ENVF" ]; then
  cat >"$ENVF" <<'EOF'
# Babloo control server settings. Edit, then: sudo systemctl restart babloo-control
BABLOO_BIND=0.0.0.0
BABLOO_PORT=8000
BABLOO_MAX_SPEED=35
BABLOO_WEBRTC_PORT=8889
# BABLOO_EV3_HOST=10.42.0.2     # normally learned automatically from the EV3's status packets
# BABLOO_USER=
# BABLOO_PASS=
EOF
fi
chmod 0640 "$ENVF"; chown root:babloo "$ENVF"

if [ -n "$AUTH_USER" ]; then
  read -r -s -p "password for $AUTH_USER: " PW; echo
  sed -i '/^#\? *BABLOO_USER=/d; /^#\? *BABLOO_PASS=/d' "$ENVF"
  printf 'BABLOO_USER=%s\nBABLOO_PASS=%s\n' "$AUTH_USER" "$PW" >>"$ENVF"
fi

# ---- 3. MediaMTX -------------------------------------------------------------
say "MediaMTX"
TARBALL="$(ls "$SRC"/../mediamtx_*_linux_arm64*.tar.gz "$HOME"/mediamtx_*_linux_arm64*.tar.gz "$SRC"/mediamtx_*_linux_arm64*.tar.gz 2>/dev/null | head -n1 || true)"
if [ ! -x /usr/local/bin/mediamtx ] || [ -n "$TARBALL" ]; then
  if [ -z "$TARBALL" ]; then
    echo "  no local tarball, downloading latest linux_arm64 release"
    URL="$(curl -fsSL https://api.github.com/repos/bluenviron/mediamtx/releases/latest \
      | grep -o 'https://[^"]*linux_arm64\(v8\)\?\.tar\.gz' | head -n1)"
    TARBALL=/tmp/mediamtx.tar.gz; curl -fsSL -o "$TARBALL" "$URL"
  fi
  tmp="$(mktemp -d)"; tar -xzf "$TARBALL" -C "$tmp"
  install -m 0755 "$tmp/mediamtx" /usr/local/bin/mediamtx
  rm -rf "$tmp"
fi
install -m 0644 "$SRC/mediamtx.yml" "$ETC/mediamtx.yml"
/usr/local/bin/mediamtx --version 2>/dev/null || true

# ---- 4. USB network to the EV3 ---------------------------------------------
say "NetworkManager shared connection on usb0"
if ! nmcli -t -f NAME con show | grep -qx babloo-usb; then
  nmcli con add type ethernet ifname usb0 con-name babloo-usb \
    ipv4.method shared ipv4.addresses 10.42.0.1/24 connection.autoconnect yes >/dev/null
else
  nmcli con mod babloo-usb ipv4.method shared ipv4.addresses 10.42.0.1/24 connection.autoconnect yes
fi
nmcli con up babloo-usb >/dev/null 2>&1 || echo "  (usb0 not present yet: it comes up when the EV3 is plugged in)"

# ---- 5. camera overlay -------------------------------------------------------
say "camera overlay in $CONFIG_TXT"
if rpicam-hello --list-cameras 2>/dev/null | grep -q ov5647; then
  echo "  camera already detected (ov5647), leaving $CONFIG_TXT alone"
elif ! grep -q '^# babloo camera' "$CONFIG_TXT"; then
  sed -i 's/^camera_auto_detect=1/#camera_auto_detect=1  # disabled by babloo/' "$CONFIG_TXT"
  printf '\n# babloo camera: Arducam Day-Night (OV5647) is not auto-detected\ncamera_auto_detect=0\ndtoverlay=ov5647\n' >>"$CONFIG_TXT"
  echo "  added; REBOOT needed before the camera works"
else
  echo "  already present"
fi

# ---- 6. Tailscale ------------------------------------------------------------
say "Tailscale"
if ! command -v tailscale >/dev/null; then
  curl -fsSL https://tailscale.com/install.sh | sh
fi
TS_IP="$(tailscale ip -4 2>/dev/null | head -n1 || true)"
if [ -z "$TS_IP" ]; then
  echo "  not connected yet. Run:  sudo tailscale up   then re-run this script with --lockdown"
else
  echo "  Tailscale IP: $TS_IP"
fi

# ---- bind mode ---------------------------------------------------------------
if [ "$MODE" = lockdown ]; then
  [ -n "$TS_IP" ] || { echo "cannot lock down: no Tailscale IP"; exit 1; }
  say "lockdown: binding to $TS_IP only"
  sed -i "s/^BABLOO_BIND=.*/BABLOO_BIND=$TS_IP/" "$ENVF"
  sed -i "s/^webrtcAddress: .*/webrtcAddress: $TS_IP:8889/" "$ETC/mediamtx.yml"
elif [ "$MODE" = open ]; then
  say "open: binding to all interfaces"
  sed -i "s/^BABLOO_BIND=.*/BABLOO_BIND=0.0.0.0/" "$ENVF"
  sed -i "s/^webrtcAddress: .*/webrtcAddress: :8889/" "$ETC/mediamtx.yml"
elif grep -q '^BABLOO_BIND=100\.' "$ENVF" 2>/dev/null; then
  # keep an existing lockdown across re-runs
  B="$(sed -n 's/^BABLOO_BIND=//p' "$ENVF")"; sed -i "s/^webrtcAddress: .*/webrtcAddress: $B:8889/" "$ETC/mediamtx.yml"
fi

# ---- 7. services -------------------------------------------------------------
say "systemd"
install -m 0644 "$SRC/systemd/mediamtx.service" /etc/systemd/system/mediamtx.service
install -m 0644 "$SRC/systemd/babloo-control.service" /etc/systemd/system/babloo-control.service
systemctl daemon-reload
systemctl enable mediamtx.service babloo-control.service >/dev/null
systemctl restart mediamtx.service babloo-control.service
sleep 2
systemctl --no-pager --lines=0 status mediamtx.service babloo-control.service || true

IP="$(hostname -I | awk '{print $1}')"
cat <<EOF

Done.
  Control page:  http://${TS_IP:-$IP}:$(sed -n 's/^BABLOO_PORT=//p' "$ENVF")/
  Raw video:     http://${TS_IP:-$IP}:8889/cam/
  Logs:          journalctl -u babloo-control -f     journalctl -u mediamtx -f
EOF
