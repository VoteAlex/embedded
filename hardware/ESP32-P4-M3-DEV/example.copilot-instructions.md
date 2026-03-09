# Copilot Instructions — JC-ESP32P4-M3-DEV

> Copy to `.github/copilot-instructions.md` in your project and customise `[TODO]` sections.

## Context

This project targets the **Guition JC-ESP32P4-M3-DEV** development board — a high-performance IoT/HMI board based on the ESP32-P4 with a MIPI display, 100 Mbps Ethernet, dual USB, and an ESP32-C6 co-processor for Wi-Fi 6 / BLE.

[TODO] Describe your project purpose here.

---

### Processors

| | |
|-|-|
| **Main MCU** | ESP32-P4 — dual-core RISC-V @ 400 MHz, 16 MB flash, 32 MB PSRAM (in-package) |
| **Co-processor** | ESP32-C6-MINI — Wi-Fi 6 (802.11ax) + Bluetooth 5 / BLE, connected via SDIO |
| **Framework** | [TODO] ESP-IDF v5.5+ / Arduino Core v3.2.1+ / ESPHome |

---

### Peripherals

| Peripheral | Details |
|-----------|---------|
| Display | MIPI 2-lane DSI · JD9365 driver · 800 × 1280 px · backlight GPIO23 |
| Touch | GT911 capacitive · I2C · SDA=GPIO7, SCL=GPIO8 |
| Audio codec | ES8311 · I2C addr 0x18 · I2S on GPIO9-13, GPIO48 · amp enable GPIO11 |
| Microphone | Onboard MEMS, I2S DIN=GPIO48 |
| Speaker | 8 Ω / 2 W header, amp enable=GPIO11 |
| Ethernet | IP101 PHY · 100 Mbps · MDC=GPIO31, MDIO=GPIO52, PWR=GPIO51, CLK=GPIO50 |
| SD / TF card | SDIO 3.0 · D0-D3=GPIO39-42, CMD=GPIO44, CLK=GPIO43 |
| RS485 / UART | UART1 · TX=GPIO26, RX=GPIO27 · MX1.25 connector · 115200 bps |
| USB | USB 2.0 OTG HS + USB 1.1 OTG FS (both Type-C) |
| Battery | JST Li-Ion · ADC2 channel 4 for voltage monitoring |
| Debug / Flash | CH340 UART · USB Type-C · ≥ 500 mA supply required |

---

### GPIO Pin Assignments

| GPIO | Function |
|------|----------|
| 7 | I2C SDA — GT911 touch + ES8311 codec |
| 8 | I2C SCL — GT911 touch + ES8311 codec |
| 9 | I2S DOUT — speaker (ES8311 TX) |
| 10 | I2S WS / LCLK — ES8311 |
| 11 | Power amplifier enable (HIGH = on) |
| 12 | I2S BCLK — ES8311 |
| 13 | I2S MCLK — ES8311 |
| 14 | ESP32-C6 SDIO D0 |
| 15 | ESP32-C6 SDIO D1 |
| 16 | ESP32-C6 SDIO D2 |
| 17 | ESP32-C6 SDIO D3 |
| 18 | ESP32-C6 SDIO CLK |
| 19 | ESP32-C6 SDIO CMD |
| 23 | Display backlight (LEDC PWM) |
| 26 | RS485 / UART1 TX |
| 27 | RS485 / UART1 RX |
| 31 | Ethernet MDC |
| 39 | SD card D0 |
| 40 | SD card D1 |
| 41 | SD card D2 |
| 42 | SD card D3 |
| 43 | SD card CLK |
| 44 | SD card CMD |
| 48 | I2S DIN — onboard microphone |
| 50 | Ethernet RMII CLK (input from IP101) |
| 51 | Ethernet PHY power / reset |
| 52 | Ethernet MDIO |
| 54 | ESP32-C6 reset |

> Display backlight (GPIO23) and reset (NC) — reset is not connected on this board.
