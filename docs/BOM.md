# Bill of Materials (with Amazon links)

Prices are approximate US list prices as of October 2026. Amazon third-party sellers often
mark up Raspberry Pi boards and cameras well above list price; where that was true at the
time of writing it is flagged, with an authorised-reseller alternative.

## Core parts (needed for phases 0–3)

| # | Part | Amazon link | Approx. price | Notes |
|---|---|---|---|---|
| 1 | Raspberry Pi 4 Model B, 1 GB or 2 GB | pishop.us · seeedstudio.com · canakit.com | $67.50 (2 GB, Oct 2026 list); 1 GB cheaper and sufficient | **Amazon listings are $130+.** Buy from an approved reseller. 1 GB is enough for MediaMTX + the control server |
| 2 | Camera: **Arducam Day-Night Vision, OV5647, 130° (D) × 100° (H), auto IR-cut, IR LEDs included** | [Arducam Day-Night B07X1VGQSL](https://www.amazon.com/gp/product/B07X1VGQSL) | $24 | **Chosen.** Motorised IR-cut filter gives correct daytime colour and real night vision with the included LED boards. Needs `dtoverlay=ov5647` in the Pi boot config. Alternative for a sharper daytime-only image: [Arducam IMX708 Wide](https://www.amazon.com/Arducam-Raspberry-Camera-Autofocus-with15cm/dp/B0CLNSTV39), ~$30 |
| 3 | microSD for the Pi, 32 GB A1 | [SanDisk Ultra 32GB A1](https://www.amazon.com/SanDisk-Ultra-microSDHC-Memory-Adapter/dp/B08GY9NYRM) | $9 | Comes with SD adapter |
| 4 | microSD for the EV3, 16 GB SDHC | [SanDisk Ultra 16GB](https://www.amazon.com/SanDisk-Ultra-SDSQUNS-016G-GN3MN-UHS-I-microSDHC/dp/B074B4P7KD) · [Micro Center 16GB 5-pack](https://www.amazon.com/Center-Memory-Adapter-Mobile-Storage/dp/B08HD83TFJ) | $8 | **Must be 32 GB or smaller.** A second 32 GB SanDisk Ultra from item 3 also works |
| 5 | microSD card reader (if your laptop lacks one) | [Sabrent USB-C + USB-A reader](https://www.amazon.com/SABRENT-Reader-High-Speed-Adapter-Memory/dp/B07KGR39PL) | $10 | Needed to flash both cards |
| 6 | USB power bank for the Pi | **[Amazon Basics 20 000 mAh, 2× USB-C 20 W + USB-A](https://www.amazon.com/gp/product/B0FFM4BY6C)** · lighter alternative: [Anker PowerCore 10K 5V/3A](https://www.amazon.com/Anker-Travel-Ready-Technology-High-Speed-Output%EF%BC%88Black/dp/B0DP6XF8J2) | $32 (often $13–20 on deal) | **Chosen.** Power the Pi from a **USB-C port** with the included USB-C to USB-C cable to get 5 V/3 A; the USB-A port is only 2.4 A. ~400 g, so strap it low and central. Roughly 12–14 h of streaming |
| 7 | USB-C power cable | Included with the Amazon Basics bank (1 ft USB-C to USB-C) | $0 | If you want a right-angle one later, any basic 60 W USB-C to USB-C cable; avoid 100 W+ e-marked cables with early Pi 4 boards |
| 8 | USB-A to mini-USB-B cable, 1 ft (Pi → EV3) | [CablesOnline 1 ft](https://www.amazon.com/CablesOnline-Type-Mini-B-Shielded-USB2-A501/dp/B082791G8N) · [CableWholesale 1 ft](https://www.amazon.com/CableWholesale-1-Feet-Mini-B-Cable-10UM-02101BK/dp/B002WPML2G) | $5 | Plugs into the EV3 "PC" port |
| 9 | Heatsinks for Pi 4 | [Easycargo Pi 4 heatsink kit](https://www.amazon.com/Easycargo-Raspberry-Heatsink-Aluminum-conductive/dp/B079FV2RH3) | $7 | Passive cooling is enough for 720p streaming |
| 10 | LEGO-compatible Pi 4 case | **[Pi-Blox Pi 4 case, black](https://www.amazon.com/Raspberry-Pi-Case-Pi-Blox-Enclosure/dp/B0BS79DDPH)** ([red](https://www.amazon.com/Raspberry-Pi-Case-Pi-Blox-Enclosure/dp/B0BS8HTCWX), [blue](https://www.amazon.com/Raspberry-Pi-Case-Pi-Blox-Enclosure/dp/B0BS8HSTZW)) | $7.70 | **Chosen.** If there is no slot for the camera ribbon, route it between lid and base | Studded top and bottom (LEGO System studs, not Technic pins). Attaches to EV3 via a few plates/bricks. Camera cable exits through the slot |
| 11 | Hook-and-loop cable ties | [Wisdompro 4 in, 50-pack](https://www.amazon.com/Inches-Cable-Self-gripping-Fastening-Wisdompro/dp/B07WHQR2JB) | $7 | Strap the power bank down and keep every cable out of reach of teeth |
| | **Core total** | | **≈ $175–200** | Pi 4 at Oct 2026 list price from a reseller |

## Items already selected (31 Oct 2026, all in stock on Amazon)

| Item | Price seen |
|---|---|
| Arducam Day-Night Vision camera, 130° (D) × 100° (H), IR-cut, B07X1VGQSL | $23.99 |
| Amazon Basics 20 000 mAh 3-port power bank, B0FFM4BY6C | $32.39 |
| Pi-Blox Raspberry Pi 4 case, black, B0BS79DDPH | $7.70 |
| Sabrent USB-C & USB-A SD/microSD reader, CR-BCA2 | $9.49 |

Still to buy: Raspberry Pi 4 (reseller), 32 GB and 16 GB microSD cards, USB-A to mini-USB cable,
heatsinks, hook-and-loop ties, and AA NiMH cells + charger for the EV3 unless you own the LEGO pack.

## EV3 power

| Part | Amazon link | Approx. price | Notes |
|---|---|---|---|
| LEGO EV3 Rechargeable DC Battery 45501 | [45501](https://www.amazon.com/LEGO-Mindstorms-Rechargeable-Battery-45501/dp/B0786VPGMR) | $130–170 (discontinued, often used) | Lightest option, charges in-brick with the 10 V LEGO adapter. Expensive now that the EV3 is discontinued |
| **Or** 6× AA NiMH + charger | [Panasonic eneloop AA 8-pack + charger](https://www.amazon.com/Panasonic-eneloop-Battery-Rechargeable-Batteries/dp/B0C2362NC6) | $24 | Recommended if you don't already own the 45501. Eneloops hold 2000 mAh, similar runtime, 2 spares |

## Optional parts (phase 4)

| Part | Amazon link | Approx. price | Purpose |
|---|---|---|---|
| USB speakerphone (mic + speaker) | [Anker PowerConf S330](https://www.amazon.com/Speakerphone-Conference-Speaker-Business-Microphone/dp/B08XWZ81CW) · [Compact USB speakerphone](https://www.amazon.com/Conference-Microphone-Omnidirectional-Microphones-Reduction/dp/B0B4D1TJ79) | $25–60 | Two-way audio: hear the pet, talk to it. Plug-and-play on Linux (USB Audio Class) |
| Raspberry Pi Zero 2 W (budget alternative to Pi 4) | [Pi Zero 2 W](https://www.amazon.com/Raspberry-Zero-Bluetooth-RPi-2W/dp/B09LH5SBPS) | $15 list | Lighter and 3× longer battery life, but needs a micro-USB OTG hub and a 15-to-22-pin camera adapter cable |

## Already owned (no purchase)

- LEGO EV3 brick, 2 large motors, wheels, Technic beams and pins for the chassis.
- EV3 touch sensor and ultrasonic sensor if your kit included them (bumper and obstacle sensing in phase 4).
- A phone with a modern browser.

## Not needed

- EV3 Wi-Fi dongle: the Pi provides the network; the EV3 talks to it over the USB cable.
- Pi power supply: the power bank replaces it. You will want a USB-C charger to recharge the bank, but any phone charger works.
- Pi Build HAT: that is for driving LEGO Powered Up / SPIKE motors directly from a Pi; EV3 motors use a different connector, so stick with the EV3 brick as the motor controller.

## Availability check (31 Oct 2026, second pass)

Direct product pages could not be opened from this environment, so this is built from cached
Amazon search snapshots plus reseller and news pages. Confirm on the live page before ordering.

**Headline changes since the first draft**

- Raspberry Pi raised list prices on 1 Oct 2026 because of memory costs. The **Pi 4 2 GB is now
  $67.50** (was $45) and the Pi 5 2 GB is $77.50. The 1 GB Pi 4 was not raised. Raspberry Pi
  says the increases are temporary.
- The **Pi Zero 2 W is largely sold out** at major retailers. Treat it as unavailable.
- The **official Camera Module 3 is unavailable on Amazon in every variant** (standard, Wide,
  NoIR, NoIR Wide). The Arducam IMX708 modules are the practical choice.
- Core total is now **≈ $190–210** with a Pi 4 2 GB at list price.

| Part | Status | Action |
|---|---|---|
| Pi 4 Model B 2 GB | List price $67.50. pishop.us and seeedstudio.com list it at $67.50; Seeed shows in stock; Adafruit and SparkFun out of stock. Amazon third-party sellers $130–150 | Buy from pishop.us or seeedstudio.com. A **1 GB Pi 4 is enough** for this project (MediaMTX + a small Python server) and was not price-raised, so take it if offered cheaper |
| Pi 5 2 GB (fallback) | $77.50 at pishop.us and canakit.com, shown in stock | Works, but no hardware H.264 encoder and about twice the power draw. Only if no Pi 4 can be found |
| Pi Zero 2 W | Sold out at most retailers; Amazon listings up to $87 | Drop from the plan |
| Arducam IMX708 Wide with case (B0CLNSTV39) | Listed; no price captured | **Primary camera.** Open the page to confirm price (historically ~$30) |
| Official Camera Module 3, all variants | Currently unavailable on Amazon | Skip. If you want the official part, buy from pishop.us or adafruit.com |
| Arducam IMX708 NoIR Wide (B0FNCY34DK) | Listed; no price captured | Night-vision alternative to the above |
| Anker PowerCore 10K 5 V/3 A (B0DP6XF8J2) | $23.74, listed | OK |
| SanDisk Ultra 32 GB A1 (B08GY9NYRM) | Listed, Amazon best seller | OK |
| SanDisk Ultra 16 GB (B074B4P7KD) | About $7, 500+ sold last month | OK |
| Sabrent CR-BCA2 reader | In stock, about $7 | OK |
| CablesOnline 1 ft mini-USB (B082791G8N) | Listed; no price captured. Sibling CableWholesale 1 ft cable in stock at $4.98 (B002WPML2G) | Either works |
| Umefly right-angle USB-C 3-pack | Listed, 50+ sold last month | OK |
| Easycargo heatsink kit | Listed; no price captured | Commodity, any Pi 4 heatsink set works |
| Pi-Blox Pi 4 case (B0BS79DDPH) | Listed with "click to see price"; stock unclear | Try it; fallback below |
| Official Pi 4 case (B07WQ5G6YY) | No featured offer on Amazon | Buy the official case from pishop.us instead, or any Pi 4 case plus straps |
| Wisdompro hook-and-loop ties | No featured offer | Any 4 in hook-and-loop ties |
| Eneloop AA 8-pack + charger | Bundle B0C234GGG4 at $19.17; batteries alone $22.79 | OK |
| LEGO 45501 battery | Used stock only, $130+ | Use eneloops |
| DORHEA IR boards | Listed; no price captured | OK, optional |
| Anker PowerConf S330 (B09FJ7LWX4) | Listed; only a bundle price seen ($60 with webcam) | OK, optional |
