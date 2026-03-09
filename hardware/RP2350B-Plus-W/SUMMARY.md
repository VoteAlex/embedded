# Waveshare RP2350B-Plus-W

> Raspberry Pi RP2350B development board with Wi-Fi 6 and Bluetooth 5.2 — Pico-compatible form factor

- **Product page:** https://www.waveshare.com/rp2350b-plus-w.htm
- **Wiki / docs:** https://www.waveshare.com/wiki/RP2350B-Plus-W
- **Schematic:** available on the Waveshare wiki page above

---

## Specifications

| | |
|-|-|
| **MCU** | Raspberry Pi RP2350B |
| **Architecture** | Dual-core — selectable: 2× Arm Cortex-M33 **or** 2× Hazard3 RISC-V @ 150 MHz |
| **SRAM** | 520 KB on-chip |
| **Flash** | 16 MB external QSPI |
| **PSRAM** | Footprint on bottom side (not populated by default) |
| **Wireless** | Infineon CYW43439 via Raspberry Pi Radio Module 2 |
| **Wi-Fi** | Wi-Fi 4 (802.11n, 2.4 GHz) |
| **Bluetooth** | Bluetooth 5.2 (BLE) |
| **USB** | USB 1.1 host/device — USB Type-C |
| **Power input** | 3.6 V–6.5 V via USB-C |
| **Regulator** | LDO 800 mA |
| **GPIO** | 41 multi-function GPIO (2×20 Pico-compatible header + 1 bottom pad) |
| **ADC** | 6× 12-bit channels |
| **PIO** | 12 programmable I/O state machines (3 PIO blocks × 4 SM) |
| **PWM** | 22 channels |
| **Interfaces** | 2× SPI · 2× I2C · 2× UART · HSTX |
| **Onboard** | 2× user LEDs (WiFi + MCU) · BOOT + RESET buttons · temperature sensor |
| **Dimensions** | 41.4 × 21 mm |
| **Form factor** | Raspberry Pi Pico / Pico W compatible |

---

## Images

<img src="images/board.png" alt="RP2350B-Plus-W board" width="320"/>

---

## GPIO Pinout

The board is **pin-compatible with Raspberry Pi Pico W** — all 40 header pins map identically. The RP2350B adds 8 extra GPIOs (GP28–GP35 + extras) accessible via castellated edges/pads.

| Pin | GPIO | Default function |
|-----|------|-----------------|
| 1 | GP0 | UART0 TX / SPI0 RX / I2C0 SDA |
| 2 | GP1 | UART0 RX / SPI0 CSn / I2C0 SCL |
| 4 | GP2 | SPI0 SCK / I2C1 SDA |
| 5 | GP3 | SPI0 TX / I2C1 SCL |
| 6 | GP4 | UART1 TX / SPI0 RX / I2C0 SDA |
| 7 | GP5 | UART1 RX / SPI0 CSn / I2C0 SCL |
| 9 | GP6 | SPI0 SCK / I2C1 SDA |
| 10 | GP7 | SPI0 TX / I2C1 SCL |
| 11 | GP8 | UART1 TX / SPI1 RX / I2C0 SDA |
| 12 | GP9 | UART1 RX / SPI1 CSn / I2C0 SCL |
| 14 | GP10 | SPI1 SCK / I2C1 SDA |
| 15 | GP11 | SPI1 TX / I2C1 SCL |
| 16 | GP12 | UART0 TX / SPI1 RX / I2C0 SDA |
| 17 | GP13 | UART0 RX / SPI1 CSn / I2C0 SCL |
| 19 | GP14 | SPI1 SCK / I2C1 SDA |
| 20 | GP15 | SPI1 TX / I2C1 SCL |
| 21 | GP16 | SPI0 RX / I2C0 SDA / UART0 TX |
| 22 | GP17 | SPI0 CSn / I2C0 SCL / UART0 RX |
| 24 | GP18 | SPI0 SCK / I2C1 SDA |
| 25 | GP19 | SPI0 TX / I2C1 SCL |
| 26 | GP20 | SPI0 RX / I2C0 SDA / UART1 TX |
| 27 | GP21 | SPI0 CSn / I2C0 SCL / UART1 RX |
| 29 | GP22 | — |
| 31 | GP26 | ADC0 |
| 32 | GP27 | ADC1 |
| 34 | GP28 | ADC2 |

> For the full official pinout diagram see: https://www.waveshare.com/img/devkit/RP2350B-Plus-W/RP2350B-Plus-W-details-4.png

---

## Key Differences vs Raspberry Pi Pico 2 W

| Feature | Pico 2 W | RP2350B-Plus-W |
|---------|----------|----------------|
| GPIO count | 26 usable | **41 usable** |
| ADC channels | 3 | **6** |
| PIO state machines | 12 | **12** |
| Flash | 4 MB | **16 MB** |
| Power regulator | DC-DC 800 mA | LDO 800 mA |
| Wireless chip | CYW43439 | CYW43439 (same) |

The RP2350B die has a larger GPIO bank than the RP2350A used on the official Pico 2 — this is the main reason to choose this board over an official Pico 2 W.

---

## Embassy (Rust async) Support

The RP2350B is supported by `embassy-rp` via the `rp235x` target. Bluetooth uses the `cyw43` cyw43 driver.

```toml
# Cargo.toml
[dependencies]
embassy-rp = { version = "0.3", features = ["rp235xa", "unstable-pac", "time-driver"] }
embassy-executor = { version = "0.7", features = ["arch-cortex-m", "executor-thread"] }
embassy-time = "0.4"
cyw43 = "0.3"
cyw43-pio = "0.3"
```

```rust
#![no_std]
#![no_main]

use embassy_executor::Spawner;
use embassy_rp::gpio::{Level, Output};
use embassy_time::Timer;

#[embassy_executor::main]
async fn main(_spawner: Spawner) {
    let p = embassy_rp::init(Default::default());
    let mut led = Output::new(p.PIN_25, Level::Low); // onboard LED

    loop {
        led.set_high();
        Timer::after_millis(500).await;
        led.set_low();
        Timer::after_millis(500).await;
    }
}
```

Build target: `thumbv8m.main-none-eabihf` (Cortex-M33)  
Or for RISC-V mode: `riscv32imac-unknown-none-elf`

---

## MicroPython

Use the RP2350 W MicroPython UF2 from https://micropython.org/download/RPI_PICO2_W/

```python
import network, time

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("SSID", "password")
while not wlan.isconnected():
    time.sleep(0.5)
print("Connected:", wlan.ifconfig())
```

---

## C/C++ SDK

Use `pico-sdk` with target `pico2_w`:

```cmake
cmake_minimum_required(VERSION 3.13)
set(PICO_BOARD pico2_w)
include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)
project(hello_rp2350b C CXX ASM)
pico_sdk_init()
add_executable(hello main.c)
target_link_libraries(hello pico_stdlib pico_cyw43_arch_lwip_threadsafe_background)
pico_add_extra_outputs(hello)
```

---

## Programming

1. Hold **BOOT** button, plug in USB-C → appears as USB mass storage drive
2. Drag and drop `.uf2` file → board reboots and runs
3. Or use `picotool` / `probe-rs` with a debug probe (SWD via 3-pin header)

SWD debug header: pins **SWDIO**, **SWDCLK**, **GND** on the castellated edge.
