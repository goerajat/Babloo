# Downloads

Everything you need on your laptop before the parts arrive. Run **one** of the scripts below
from this folder and it fetches the current version of each file into `downloads/files/`.
The downloaded files are ignored by git, since the OS images are several hundred megabytes.

| File | Purpose | Size |
|---|---|---|
| Raspberry Pi Imager | Flashes the Pi card **and** the EV3 card ("Use custom" image). Pre-configures Wi-Fi, SSH and user for the Pi | ~30 MB |
| Raspberry Pi OS Lite (64-bit) | The Pi's operating system. Imager can also download this itself, but having it locally makes re-flashing faster | ~450 MB |
| ev3dev-stretch EV3 image | The EV3's operating system. Latest stable is the 2020-04-10 release. The scripts also extract the bare `.img` from the zip: **flash the `.img`, not the zip**, because the zip nests the image in a folder and Imager writes nothing from it | ~300 MB zip, 1.8 GB img |
| MediaMTX (linux arm64) | Video streaming server. Copied to the Pi during setup | ~15 MB |
| balenaEtcher (optional) | Alternative flashing tool. Only needed if Imager's custom-image option misbehaves | ~150 MB |

Tailscale is **not** downloaded here. It installs on the Pi with one command during setup
(`curl -fsSL https://tailscale.com/install.sh | sh`) and on your phone and laptop from the app store.

## Run

macOS, Linux or Windows WSL:

```bash
cd downloads
./download.sh
```

Windows PowerShell:

```powershell
cd downloads
.\download.ps1
```

Both scripts skip files that are already present, print SHA-256 checksums, and verify the
Raspberry Pi OS image against the published checksum.

## If a download fails

The scripts use "latest" links so they keep working as versions change. If one breaks:

- Imager: https://www.raspberrypi.com/software/
- Pi OS Lite 64-bit: https://www.raspberrypi.com/software/operating-systems/ (choose *Raspberry Pi OS Lite, 64-bit*)
- ev3dev: https://www.ev3dev.org/downloads/ (choose the **EV3** image, not rpi or bone)
- MediaMTX: https://github.com/bluenviron/mediamtx/releases (asset ending in `linux_arm64.tar.gz` or `linux_arm64v8.tar.gz`)
- Etcher: https://etcher.balena.io/
