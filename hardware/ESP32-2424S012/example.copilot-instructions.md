# Copilot Instructions — ESP32-2424S012

> Copy to `.github/copilot-instructions.md` in your project and customise `[TODO]` sections.

## Context

This project targets the **ESP32-2424S012** development board — a compact 1.28″ round TFT IoT/smart-watch module based on the ESP32-C3, with a circular capacitive touchscreen and built-in Li-Ion battery charging.

[TODO] Describe your project purpose here.

---

### Processors

| | |
|-|-|
| **MCU** | ESP32-C3-MINI-1U — single-core RISC-V @ 160 MHz, 4 MB flash |
| **Wi-Fi** | 802.11 b/g/n (2.4 GHz) |
| **Bluetooth** | BLE 5.0 |
| **Framework** | [TODO] Arduino / ESP-IDF / ESPHome |

---

### Peripherals

| Peripheral | Details |
|-----------|---------|
| Display | 1.28″ circular IPS TFT · 240 × 240 px · GC9A01 driver · SPI · 80 MHz write |
| Touch | CST816D capacitive · I2C addr 0x15 · SDA=GPIO4, SCL=GPIO5 |
| Backlight | LED · GPIO3 (HIGH = on) via AO3402 MOSFET |
| Power | USB Type-C · TP4054 Li-Ion charger · 3.3 V DC-DC |
| Battery | JST 1.25-2P · single-cell Li-Ion |
| Debug / Flash | USB full-speed (native ESP32-C3 USB-JTAG, no separate chip) |

---

### GPIO Pin Assignments

| GPIO | Function |
|------|----------|
| 0 | Touch INT — interrupt (active low, input) |
| 1 | Touch RST — reset (output, LOW 10 ms → HIGH 300 ms) |
| 2 | Display DC — data/command select (output) |
| 3 | Display BL — backlight enable (HIGH = on, output) |
| 4 | I2C SDA — CST816D touch controller |
| 5 | I2C SCL — CST816D touch controller |
| 6 | SPI CLK — GC9A01 display clock |
| 7 | SPI MOSI — GC9A01 display data |
| 8 | User button / BOOT mode |
| 9 | BOOT button |
| 10 | SPI CS — GC9A01 chip select (active low) |
| 18 | USB D− (native USB) |
| 19 | USB D+ (native USB) |
| 20 | UART RX |
| 21 | UART TX |

> MISO is not connected (−1) — the display is write-only.
