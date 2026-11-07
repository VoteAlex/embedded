# CANable 2.0 Pro — Hardware Reference

> Compact, galvanically-isolated USB-to-CAN / CAN-FD adapter built around an STM32G4 with a built-in FDCAN controller. Open-source firmware → plug-and-play with Linux SocketCAN.

- **Product:** CANable 2.0 Pro (a.k.a. MKS CANable V2.0 Pro)
- **Manufacturer:** Makerbase (MKS) — CANable 2.0 open-hardware design by Openlight Labs
- **Form Factor:** USB-C dongle, ~45 × 16 mm
- **Amazon (DE):** https://www.amazon.de/dp/B0DRYT4TKV
- **Project page:** https://canable.io/
- **Vendor product page:** https://makerbase3d.com/product/makerbase-canable-v2/
- **Hardware repo (MKS):** https://github.com/makerbase-mks/CANable-MKS
- **Reference notes (isolated PRO):** https://github.com/SebKuzminsky/mks-canable-2.0-pro

> ⚠️ **Pro vs non-Pro:** The **Pro** version has 2.5 kV galvanic isolation between USB and the CAN bus. The plain **CANable 2.0** has *no* isolation. This sheet documents the **isolated Pro** variant.

---

## Table of Contents

1. [Specifications](#specifications)
2. [Connectors & Pinout](#connectors--pinout)
3. [Termination](#termination)
4. [Firmware Options](#firmware-options)
5. [Flashing (DFU Bootloader)](#flashing-dfu-bootloader)
6. [Linux / SocketCAN Usage](#linux--socketcan-usage)
7. [slcan Usage (Windows / macOS / Linux)](#slcan-usage-windows--macos--linux)
8. [Test Tools](#test-tools)
9. [Python (python-can)](#python-python-can)
10. [Known Hardware Quirk — Fast Reset](#known-hardware-quirk--fast-reset)
11. [SWD Debug Header](#swd-debug-header)

---

## Specifications

| Specification | Value |
|---------------|-------|
| **MCU** | STM32G431C8T6 — Arm Cortex-M4F @ up to 170 MHz |
| **CAN controller** | STM32G4 built-in **FDCAN** peripheral |
| **CAN classic** | CAN 2.0A / 2.0B, up to **1 Mbit/s** |
| **CAN FD** | Up to **5 Mbit/s** data phase (flexible data-rate, BRS) |
| **Transceiver** | Isolated CAN-FD transceiver |
| **Isolation** | **2.5 kV** galvanic isolation (USB ↔ CAN) |
| **Host interface** | USB 2.0 Full-Speed, **USB Type-C** |
| **CAN connector** | 4-pin screw terminal — CANH, CANL, GND, 5 V |
| **Termination** | Onboard 120 Ω, switch/jumper selectable |
| **Bootloader** | STM32 system DFU (BOOT jumper) |
| **Debug** | SWD pads (SWDIO / SWCLK / GND / 3.3 V) |
| **OS support** | Linux (SocketCAN, native), Windows, macOS |
| **Dimensions** | ≈ 45 × 16 mm |
| **Firmware (as shipped)** | `canable2-fw` @ commit [`b158aa7`](https://github.com/normaldotcom/canable2-fw/commit/b158aa7ab106bc018715cd4d5f02f544f9de1830) (slcan, factory default) — reported via USB `iProduct` string; this is the latest commit on `master` |

---

## Connectors & Pinout

### USB
- USB Type-C → host PC / Raspberry Pi / SBC. Provides power to the USB side of the isolator.

### CAN screw terminal (4-pin)

| Pin | Signal | Description |
|-----|--------|-------------|
| 1 | CANH | CAN bus high |
| 2 | CANL | CAN bus low |
| 3 | GND | Isolated CAN-side ground |
| 4 | 5V | Isolated 5 V out (bus power, current-limited) |

> The 5 V / GND on the CAN side are on the **isolated** domain — do not tie them to USB-side ground, or you defeat the isolation.

---

## Termination

A CAN bus must be terminated with **120 Ω** at each physical end. The board has an onboard 120 Ω resistor enabled via a jumper/switch:

- **Adapter at the end of the bus** → enable termination.
- **Adapter tapped into the middle of an already-terminated bus** → disable termination.

---

## Firmware Options

The CANable 2.0 Pro is open firmware. Two common choices:

| Firmware | Interface | Best for |
|----------|-----------|----------|
| **candleLight** (`gs_usb`) | Native Linux SocketCAN device (`canX`) | Linux — best performance, CAN-FD, `candump`/`cansend` |
| **slcan** (`canable2-fw`) | Serial-line CAN (`/dev/ttyACMx`) | Windows / macOS, cross-platform tools |

- candleLight FW (multichannel branch supports this board): https://github.com/pgreenland/candleLight_fw (`multichannel` branch) — upstream: https://github.com/candle-usb/candleLight_fw
- slcan FW (ships from factory): https://github.com/normaldotcom/canable2-fw

**Checking the installed firmware version:** when plugged in, the board reports its firmware build via the USB product string. On macOS:
```bash
ioreg -p IOUSB -l -w0 | grep "USB Product Name"
# e.g. "CANable2 b158aa7 github_com_nor..." → running canable2-fw commit b158aa7
```

USB IDs:
- candleLight: `1d50:606f` (OpenMoko / Geschwister Schneider CAN adapter)
- DFU mode: `0483:df11` (STMicroelectronics DFU)

---

## Flashing (DFU Bootloader)

1. Unplug from USB.
2. Install the **BOOT** jumper (or hold BOOT button).
3. Plug back into USB — verify it enumerates in DFU mode:
   ```
   $ lsusb
   Bus 001 Device 101: ID 0483:df11 STMicroelectronics STM Device in DFU Mode
   ```
4. Flash with `dfu-util` (or the firmware repo's `make flash-...` target):
   ```bash
   dfu-util -a 0 -s 0x08000000:leave -D firmware.bin
   ```
5. Unplug, **remove the BOOT jumper**, reconnect. With candleLight it should appear as:
   ```
   Bus 001 Device 102: ID 1d50:606f OpenMoko, Inc. Geschwister Schneider CAN adapter
   ```

Build deps for the firmware: `sudo apt install gcc-arm-none-eabi dfu-util cmake`.

---

## Linux / SocketCAN Usage

With **candleLight** firmware, the adapter is a native SocketCAN interface — no daemon required.

```bash
# Bring up classic CAN @ 500 kbit/s
sudo ip link set can0 type can bitrate 500000
sudo ip link set can0 up

# Sniff traffic
candump can0

# Send a frame
cansend can0 123#DEADBEEF
```

CAN-FD with bit-rate switching (e.g. 500 k nominal / 2 M data):

```bash
sudo ip link set can0 type can bitrate 500000 dbitrate 2000000 fd on
sudo ip link set can0 up
```

---

## slcan Usage (Windows / macOS / Linux)

With **slcan** firmware the device is a USB CDC serial port. On Linux you can attach it to SocketCAN with `slcand`:

```bash
sudo slcand -o -c -f -s6 /dev/ttyACM0 can0   # -s6 = 500 kbit/s
sudo ip link set can0 up
```

Speed codes: `-s0`=10k `-s1`=20k `-s2`=50k `-s3`=100k `-s4`=125k `-s5`=250k `-s6`=500k `-s7`=800k `-s8`=1M.

On Windows/macOS, use cross-platform tools (e.g. cangaroo, SavvyCAN, python-can `slcan` backend) pointed at the COM/tty port.

---

## Test Tools

Ready-to-run sniffer / bitrate-scanner scripts (uv, no venv needed) live in
[`tools/`](tools/) — see [`tools/README.md`](tools/README.md).

```bash
uv run tools/can_scan.py  /dev/cu.usbmodem<id>        # auto-detect bitrate (passive)
uv run tools/can_sniff.py /dev/cu.usbmodem<id> 125000 # live frame sniffer
```

---

## Python (python-can)

```python
import can

# candleLight (Linux SocketCAN)
bus = can.Bus(interface="socketcan", channel="can0", bitrate=500000)

# slcan (any OS) — point at the serial port
# bus = can.Bus(interface="slcan", channel="/dev/ttyACM0", bitrate=500000)

bus.send(can.Message(arbitration_id=0x123, data=[0xDE, 0xAD, 0xBE, 0xEF], is_extended_id=False))

for msg in bus:
    print(msg)
```

---

## Known Hardware Quirk — Fast Reset

The MKS CANable 2.0 Pro has a hardware bug where rebooting/resetting too quickly can drop it back into the DFU bootloader instead of the application. See: https://github.com/makerbase-mks/CANable-MKS/issues/6

Workarounds:
- Leave the board powered down for ~2 s on any reset, **or**
- Reprogram the STM32 Flash Option Bytes via SWD (OpenOCD) so it always boots the application regardless of reset timing.

---

## SWD Debug Header

For option-byte fixes or custom firmware development, connect an SWD probe (e.g. SEGGER J-Link / ST-Link):

| Probe | CANable pad |
|-------|-------------|
| Vtref / 3.3 V | 3.3V |
| GND | GND |
| SWDIO | SWD |
| SWCLK | SWC |

Target config for OpenOCD: `-f target/stm32g4x.cfg`.

---

*Project: [`canable.io`](https://canable.io/) · Vendor: [`makerbase3d.com`](https://makerbase3d.com/product/makerbase-canable-v2/) · Firmware: [`candleLight_fw`](https://github.com/candle-usb/candleLight_fw) / [`canable2-fw`](https://github.com/normaldotcom/canable2-fw)*
