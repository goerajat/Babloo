#!/usr/bin/env bash
# Fetch every file needed to set up Babloo. Safe to re-run; existing files are skipped.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p files && cd files

OS="$(uname -s)"
ARCH="$(uname -m)"

fetch() { # fetch <url> <outfile>
  if [ -s "$2" ]; then echo "  already have $2"; return; fi
  echo "  downloading $2"
  curl -fL --retry 3 --progress-bar -o "$2.part" "$1" && mv "$2.part" "$2"
}
gh_latest_asset() { # gh_latest_asset <owner/repo> <grep-pattern>  -> prints asset URL
  curl -fsSL "https://api.github.com/repos/$1/releases/latest" \
    | grep -o '"browser_download_url": *"[^"]*"' | cut -d'"' -f4 | grep -E "$2" | head -1
}

echo "== Raspberry Pi Imager"
case "$OS" in
  Darwin) fetch https://downloads.raspberrypi.org/imager/imager_latest.dmg imager_latest.dmg ;;
  Linux)  fetch https://downloads.raspberrypi.org/imager/imager_latest_amd64.deb imager_latest_amd64.deb ;;
  *)      fetch https://downloads.raspberrypi.org/imager/imager_latest.exe imager_latest.exe ;;
esac

echo "== Raspberry Pi OS Lite (64-bit)"
fetch https://downloads.raspberrypi.com/raspios_lite_arm64_latest raspios_lite_arm64_latest.img.xz
fetch https://downloads.raspberrypi.com/raspios_lite_arm64_latest.sha256 raspios_lite_arm64_latest.img.xz.sha256 || true
if [ -s raspios_lite_arm64_latest.img.xz.sha256 ]; then
  want="$(awk '{print $1}' raspios_lite_arm64_latest.img.xz.sha256)"
  have="$(shasum -a 256 raspios_lite_arm64_latest.img.xz | awk '{print $1}')"
  [ "$want" = "$have" ] && echo "  checksum OK" || { echo "  CHECKSUM MISMATCH: delete the file and re-run"; exit 1; }
fi

echo "== ev3dev (EV3 image)"
EV3_URL="https://github.com/ev3dev/ev3dev/releases/download/ev3dev-stretch-2020-04-10/ev3dev-stretch-ev3-generic-2020-04-10.zip"
if ! fetch "$EV3_URL" ev3dev-stretch-ev3-generic-2020-04-10.zip; then
  echo "  pinned URL failed, asking GitHub for the latest EV3 image"
  u="$(gh_latest_asset ev3dev/ev3dev 'ev3-generic.*\.(zip|img\.xz)$')"
  fetch "$u" "$(basename "$u")"
fi

# The zip nests the .img inside a folder with metadata; Imager needs the bare .img.
if ! ls ev3dev-*.img >/dev/null 2>&1; then
  echo "  extracting .img (Imager cannot use the nested zip)"
  unzip -o -j -q ev3dev-*.zip "*/*.img" -d .
fi

echo "== MediaMTX (linux arm64, for the Pi)"
u="$(gh_latest_asset bluenviron/mediamtx 'linux_arm64(v8)?\.tar\.gz$')"
fetch "$u" "$(basename "$u")"

echo "== balenaEtcher (optional)"
case "$OS" in
  Darwin) pat='\.dmg$' ;;
  Linux)  pat='x86_64\.AppImage$' ;;
  *)      pat='Setup.*\.exe$' ;;
esac
u="$(gh_latest_asset balena-io/etcher "$pat" || true)"
[ -n "${u:-}" ] && fetch "$u" "$(basename "$u")" || echo "  skipped (could not resolve asset)"

echo
echo "== Checksums"
shasum -a 256 * 2>/dev/null | grep -v '\.sha256$' || sha256sum *
echo
echo "Done. Files are in $(pwd)"
