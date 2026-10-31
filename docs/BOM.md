# Bill of Materials (with Amazon links)

Prices are approximate US list prices as of October 2026. Amazon third-party sellers often
mark up Raspberry Pi boards and cameras well above list price; where that was true at the
time of writing it is flagged, with an authorised-reseller alternative.

## Core parts (needed for phases 0–3)

| # | Part | Amazon link | Approx. price | Notes |
|---|---|---|---|---|
| 1 | Raspberry Pi 4 Model B, 2 GB | [Official board](https://www.amazon.com/-/es/Raspberry-SC15184-Modelo-2019-Bluetooth/dp/B07TD42S27) · [CanaKit Basic Kit 2GB](https://www.amazon.com/CanaKit-Raspberry-Basic-Kit-2GB/dp/B07TYK4RL8) · [Vilros Basic Kit 2GB](https://www.amazon.com/Vilros-Raspberry-Basic-Cover-Clear/dp/B07TKF7YJR) | $45 list | **Amazon listings were $130+ at time of writing.** Buy at list from an approved reseller instead: pishop.us, adafruit.com, canakit.com, vilros.com. A 4 GB board is fine too |
| 2 | Camera: Raspberry Pi Camera Module 3 Wide | [Official Wide](https://www.amazon.com/Raspberry-Pi-Camera-Module-Wide/dp/B0BRY757NX) · [Official standard 75°](https://www.amazon.com/Raspberry-Pi-Camera-Module/dp/B0BRY6MVXL) · [Arducam IMX708 Wide w/ case](https://www.amazon.com/Arducam-Raspberry-Camera-Autofocus-with15cm/dp/B0CLNSTV39) | $35 (Wide) / $25 (standard) | Official Wide was out of stock on Amazon at time of writing; the Arducam IMX708 120° is the same sensor and works with `libcamera` (needs one config line). Standard 75° official module is a fine fallback |
| 3 | microSD for the Pi, 32 GB A1 | [SanDisk Ultra 32GB A1](https://www.amazon.com/SanDisk-Ultra-microSDHC-Memory-Adapter/dp/B08GY9NYRM) | $9 | Comes with SD adapter |
| 4 | microSD for the EV3, 16 GB SDHC | [SanDisk Ultra 16GB](https://www.amazon.com/SanDisk-Ultra-SDSQUNS-016G-GN3MN-UHS-I-microSDHC/dp/B074B4P7KD) · [Micro Center 16GB 5-pack](https://www.amazon.com/Center-Memory-Adapter-Mobile-Storage/dp/B08HD83TFJ) | $8 | **Must be 32 GB or smaller.** A second 32 GB SanDisk Ultra from item 3 also works |
| 5 | microSD card reader (if your laptop lacks one) | [Sabrent USB-C + USB-A reader](https://www.amazon.com/SABRENT-Reader-High-Speed-Adapter-Memory/dp/B07KGR39PL) | $10 | Needed to flash both cards |
| 6 | USB power bank for the Pi, 10 000 mAh, 5 V/3 A | [Anker PowerCore 10K, 5V/3A, trickle mode](https://www.amazon.com/Anker-Portable-PowerCore-High-Speed-Technology/dp/B08TW84CR1) · [Anker 10K PowerIQ USB-C](https://www.amazon.com/Anker-Travel-Ready-Technology-High-Speed-Output%EF%BC%88Black%EF%BC%89%EF%BC%8C1pack/dp/B0D5CLSMFB) | $20–25 | Pick a bank with a **3 A output** and a **trickle-charging / low-current mode** so it never switches off under light load. Check the listing: some Anker 10K models are 2.4 A and USB-C input only |
| 7 | USB-C power cable, short, right-angle | [Umefly 1 ft right-angle USB-A to USB-C, 3-pack](https://www.amazon.com/Umefly-USB-C-Cable/dp/B0BLXD4X4G) · [USB-C to USB-C 1 ft 100 W, 3-pack](https://www.amazon.com/Braided-Charging-Compatible-MacBook-S22%EF%BC%8CPixel/dp/B0B5QJTT8M) | $8–10 | Match the plug to the bank's output port (USB-A or USB-C). Short and thick avoids under-voltage |
| 8 | USB-A to mini-USB-B cable, 1 ft (Pi → EV3) | [StarTech USB2HABM1](https://www.amazon.com/StarTech-1-Feet-Mini-USB-Cable/dp/B002L5U7N2) · [CablesOnline 1 ft](https://www.amazon.com/CablesOnline-Type-Mini-B-Shielded-USB2-A501/dp/B082791G8N) | $6 | Plugs into the EV3 "PC" port. Avoid the StarTech **Y-cable** variant |
| 9 | Heatsinks for Pi 4 | [Easycargo Pi 4 heatsink kit](https://www.amazon.com/Easycargo-Raspberry-Heatsink-Aluminum-conductive/dp/B079FV2RH3) | $7 | Passive cooling is enough for 720p streaming |
| 10 | LEGO-compatible Pi 4 case | [Pi-Blox Pi 4 case, black](https://www.amazon.com/Raspberry-Pi-Case-Pi-Blox-Enclosure/dp/B0BS79DDPH) ([red](https://www.amazon.com/Raspberry-Pi-Case-Pi-Blox-Enclosure/dp/B0BS8HTCWX), [blue](https://www.amazon.com/Raspberry-Pi-Case-Pi-Blox-Enclosure/dp/B0BS8HSTZW)) | $12 | Studded top and bottom (LEGO System studs, not Technic pins). Attaches to EV3 via a few plates/bricks. Camera cable exits through the slot |
| 11 | Hook-and-loop cable ties | [Wisdompro 4 in, 50-pack](https://www.amazon.com/Inches-Cable-Self-gripping-Fastening-Wisdompro/dp/B07WHQR2JB) | $7 | Strap the power bank down and keep every cable out of reach of teeth |
| | **Core total** | | **≈ $165–185** | Assumes Pi 4 bought at list price from a reseller |

## EV3 power

| Part | Amazon link | Approx. price | Notes |
|---|---|---|---|
| LEGO EV3 Rechargeable DC Battery 45501 | [45501](https://www.amazon.com/LEGO-Mindstorms-Rechargeable-Battery-45501/dp/B0786VPGMR) | $130–170 (discontinued, often used) | Lightest option, charges in-brick with the 10 V LEGO adapter. Expensive now that the EV3 is discontinued |
| **Or** 6× AA NiMH + charger | [Panasonic eneloop AA 8-pack + charger](https://www.amazon.com/Panasonic-eneloop-Battery-Rechargeable-Batteries/dp/B0C2362NC6) | $24 | Recommended if you don't already own the 45501. Eneloops hold 2000 mAh, similar runtime, 2 spares |

## Optional parts (phase 4)

| Part | Amazon link | Approx. price | Purpose |
|---|---|---|---|
| Camera Module 3 **NoIR** (75°) | [Official NoIR](https://www.amazon.com/Raspberry-Pi-Camera-Module-NoIR/dp/B0BRY3L9H7) · [NoIR Wide](https://www.amazon.com/Raspberry-Pi-Camera-Module-NoIR/dp/B0BRY6VLR6) · [Arducam IMX708 NoIR Wide](https://www.amazon.com/Arducam-Raspberry-Camera-Module-IMX708/dp/B0FNCY34DK) | $25–35 | Night vision. Buy *instead of* item 2 if dark rooms matter more than daytime colour accuracy |
| 850 nm IR illuminator boards | [DORHEA 3 W 850 nm, 2-pack](https://www.amazon.com/Infrared-Illuminator-Adjustable-Resistor-Raspberry/dp/B07FM6LL3V) | $10 | Pairs with the NoIR camera. Powered from the Pi's 3.3 V/5 V pins; has a light sensor so it turns on only in the dark. Gets warm: mount on the case, not the Pi |
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
