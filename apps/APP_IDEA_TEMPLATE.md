# App Idea — [PROJECT NAME]

---

## 1. Board

- [ ] **ESP32-2424S012** — ESP32-C3 · 1.28″ round display · touch · USB-C · battery · `hardware/ESP32-2424S012/SUMMARY.md`
- [ ] **JC-ESP32P4-M3-DEV** — ESP32-P4 · 800×1280 MIPI display · touch · audio · Ethernet · Wi-Fi 6 · `hardware/ESP32-P4-M3-DEV/SUMMARY.md`
- [ ] Other / custom board: ______

---

## 2. Framework

- [ ] **ESP-IDF** (v5.5+) — recommended for production, full hardware control
- [ ] **Arduino** (ESP32 core v3.2.1+) — rapid prototyping
- [ ] **ESP-IDF + Arduino as component** — both together

---

## 3. Display & UI

**Rendering library:**
- [ ] **LVGL** (v9) — widgets, animations, event system
- [ ] **LVGL** (v8) — stable / legacy
- [ ] **LovyanGFX** — low-level SPI/MIPI display driver + primitives
- [ ] **TFT_eSPI** — Arduino display library
- [ ] **esp_lcd** panel API — bare ESP-IDF LCD abstraction only
- [ ] No display / headless

**Display interaction:**
- [ ] Touch input (capacitive)
- [ ] Gesture navigation (swipe / tap / long-press)
- [ ] Button navigation (physical GPIO buttons)
- [ ] Rotary encoder navigation
- [ ] No touch / no input

**Display features:**
- [ ] Animations / transitions between screens
- [ ] Custom fonts
- [ ] Image / PNG assets from SPIFFS
- [ ] Brightness control (LEDC PWM backlight)
- [ ] Screen off / auto-dim on idle
- [ ] Multi-language / i18n

---

## 4. Connectivity

### Network interface
- [ ] **Wi-Fi** — station mode (connects to existing AP)
- [ ] **Wi-Fi** — soft-AP mode (device creates its own hotspot)
- [ ] **Wi-Fi** — dual mode (station + AP simultaneously)
- [ ] **Wi-Fi provisioning** — BLE-assisted or SoftAP provisioning (`wifi_provisioning` component)
- [ ] **Ethernet** (wired RJ45 — ESP32-P4 only, IP101 PHY)
- [ ] **ESP-NOW** — peer-to-peer, no router needed
- [ ] **BLE** — peripheral (advertises, accepts connections)
- [ ] **BLE** — central (scans and connects to other devices)
- [ ] **BLE** — beacon / advertising only
- [ ] **Zigbee** — `esp_zigbee_sdk` (ESP32-H / ESP32-C6 co-proc)
- [ ] **Thread / OpenThread** — mesh IPv6
- [ ] **Matter** — `esp-matter` SDK (Wi-Fi or Thread transport)
- [ ] No network

### Power delivery
- [ ] USB (powered via USB-C cable)
- [ ] **PoE** — powered via Ethernet cable (802.3af/at — ESP32-P4 only)
- [ ] Battery (Li-Ion via JST connector)
- [ ] Battery + USB charging (onboard charger IC)
- [ ] Solar / energy harvesting (deep-sleep duty cycle)

### IP / time / discovery
- [ ] DHCP (automatic IP)
- [ ] Static IP (hardcoded or NVS-configured)
- [ ] **mDNS** — device reachable at `_______.local` (`mdns` component)
- [ ] **DNS-SD** — advertise services over mDNS
- [ ] **SNTP** — synchronise system clock with NTP server (`esp_sntp`)
- [ ] **DNS resolver** — resolve hostnames to IP

---

## 5. Application Protocol

**Inbound (device acts as server):**
- [ ] **HTTP REST** — JSON API (`esp_http_server`)
- [ ] **HTTPS** — TLS-wrapped HTTP server (`esp_https_server`)
- [ ] **WebSocket server** — real-time bidirectional (`esp_http_server` WS upgrade)
- [ ] **Server-Sent Events (SSE)** — live push to browser clients
- [ ] **TCP server** — raw socket, custom binary protocol
- [ ] **UDP server** — low-latency sensor broadcast / command receiver
- [ ] **CoAP server** — constrained IoT protocol (`libcoap`)
- [ ] **Modbus RTU slave** — industrial serial over RS485

**Outbound (device acts as client):**
- [ ] **HTTP client** — call external REST APIs (`esp_http_client`)
- [ ] **HTTPS client** — TLS (`esp_tls`)
- [ ] **WebSocket client** — connect to remote WS server (`esp_websocket_client`)
- [ ] **MQTT client** — pub/sub to broker (`esp_mqtt` / `mqtt5`)
- [ ] **MQTT v5** — enhanced MQTT with properties and reason codes
- [ ] **CoAP client** — send CoAP requests
- [ ] **Modbus RTU master** — poll industrial sensors over RS485

- [ ] No network protocol

---

## 6. Web Portal (browser UI)

- [ ] **Dashboard** — live status / sensor readings (SSE or WebSocket)
- [ ] **Settings page** — configure device parameters, save to NVS
- [ ] **OTA update page** — drag-and-drop `.bin` upload with progress bar
- [ ] **Log viewer** — stream ESP_LOG output to browser in real time
- [ ] **File manager** — browse / upload / delete files on SPIFFS or SD
- [ ] **Chart / graph** — time-series sensor data (Chart.js)
- [ ] **Console** — send commands to device from browser (WebSocket)
- [ ] **Wi-Fi scan & connect** — scan SSIDs, enter password, save creds
- [ ] No web portal

---

## 7. OTA & Updates

- [ ] **HTTP OTA** — push `.bin` via web portal `/update` endpoint (`esp_ota_ops`)
- [ ] **HTTPS OTA** — device pulls firmware from a URL (`esp_https_ota`)
- [ ] **Delta OTA** — incremental patch (smaller download)
- [ ] **Rollback on boot fail** — revert to previous app partition automatically
- [ ] **Factory partition** — factory reset restores known-good firmware
- [ ] **Version check** — compare running version before applying update
- [ ] No OTA

---

## 8. Storage

**On-chip:**
- [ ] **NVS** — key-value store for config (Wi-Fi creds, user settings) (`nvs_flash`)
- [ ] **NVS encrypted** — AES-XTS encrypted NVS partition
- [ ] **SPIFFS** — flat file system for web assets, JSON, small logs (`spiffs`)
- [ ] **LittleFS** — power-safe alternative to SPIFFS (`esp_littlefs` component)
- [ ] **FAT on flash** — wear-levelled FAT partition (`wear_levelling` + `fatfs`)

**External:**
- [ ] **SD / TF card** — SDIO 3.0 or SPI mode, large file storage (`sdmmc` / `sdspi`)
- [ ] **I2C EEPROM** — small byte-addressable config store (AT24Cxx)
- [ ] **SPI Flash (external)** — additional XIP or data flash

- [ ] No persistent storage

---

## 9. Peripheral Drivers (ESP-IDF built-in)

**GPIO / basic I/O:**
- [ ] `driver/gpio` — digital input / output / interrupt
- [ ] `driver/ledc` — LED PWM (backlight, dimming, status LED)
- [ ] `driver/rmt` — remote control peripheral (WS2812 LED strip, IR TX/RX)
- [ ] `driver/pcnt` — pulse counter (encoder, flow meter, frequency input)
- [ ] `driver/sigma_delta` — sigma-delta modulation output
- [ ] `driver/dedic_gpio` — cycle-accurate GPIO toggling

**Communication buses:**
- [ ] `driver/i2c` / `i2c_master` — I2C host (sensors, display touch, codec)
- [ ] `driver/spi_master` — SPI host (display, ADC, SD in SPI mode)
- [ ] `driver/uart` — serial UART (debug, RS232/485, GPS modules)
- [ ] `driver/twai` — CAN bus (automotive / industrial — ESP32-P4 only)
- [ ] `driver/i2s` — I2S audio (codec, microphone, DAC)
- [ ] `driver/sdmmc` — SDIO / SD/MMC host controller

**Analog:**
- [ ] `driver/adc` — analog to digital conversion (oneshot / continuous)
- [ ] `driver/dac` — digital to analog output (ESP32 classic only)
- [ ] `driver/temperature_sensor` — internal chip temperature

**Timers / clocks:**
- [ ] `esp_timer` — high-resolution one-shot and periodic timers
- [ ] `driver/gptimer` — general-purpose hardware timer

---

## 10. Sensors & External Modules (I2C / SPI / GPIO)

**Environment:**
- [ ] Temperature / humidity — DHT22 · SHT3x · SHT4x · AHT20
- [ ] Temperature / humidity / pressure — BME280 · BME680
- [ ] Barometric pressure / altitude — BMP280 · BMP390
- [ ] Air quality / VOC — SGP30 · SGP41 · ENS160
- [ ] CO₂ (NDIR) — SCD40 · SCD41 · MH-Z19
- [ ] Particulate matter / dust — PMS5003 · SDS011
- [ ] Ambient light — BH1750 · VEML7700
- [ ] UV index — VEML6075 · ML8511
- [ ] Colour — TCS34725

**Motion / position:**
- [ ] PIR motion — HC-SR501
- [ ] Radar motion — LD2410 · HLK-LD2450 (UART)
- [ ] Ultrasonic distance — HC-SR04
- [ ] ToF distance — VL53L0X · VL53L4CD (I2C)
- [ ] IMU / accelerometer / gyroscope — MPU6050 · ICM42688 · BMI270
- [ ] Magnetometer / compass — HMC5883L · QMC5883L · MMC5983
- [ ] GPS / GNSS — NEO-M8N · L76K (UART / I2C)

**Electrical / power:**
- [ ] Current / power monitor — INA219 · INA3221 · ACS712
- [ ] Voltage divider / battery level (ADC)
- [ ] Hall effect sensor

**User input:**
- [ ] Push button (GPIO interrupt, debounce)
- [ ] Rotary encoder (PCNT)
- [ ] Capacitive touch (ESP built-in touch sensor)
- [ ] Keypad matrix
- [ ] IR remote receiver (RMT)

**Output / actuation:**
- [ ] Relay / digital output (GPIO)
- [ ] MOSFET driver (PWM load switching)
- [ ] Servo motor (LEDC / MCPWM)
- [ ] Stepper motor (GPIO step/dir or UART driver — TMC2209)
- [ ] DC motor (PWM + H-bridge)
- [ ] RGB LED strip (WS2812B / SK6812 via RMT)
- [ ] Buzzer / piezo (LEDC tone)
- [ ] 7-segment / LED matrix display (TM1637 / MAX7219)
- [ ] OLED display secondary (SSD1306 I2C)

**Interfaces / modules:**
- [ ] LoRa transceiver — SX1276 / LLCC68 (SPI)
- [ ] RS232 / RS485 level shifter — MAX3485
- [ ] CAN transceiver — SN65HVD230
- [ ] 1-Wire bus — DS18B20 temperature sensor
- [ ] RFID — MFRC522 (SPI) · PN532 (I2C)
- [ ] Fingerprint sensor — R503 (UART)
- [ ] Cellular / LTE modem — SIM7600 (UART AT commands)
- [ ] Other: ______

---

## 11. Audio (ESP32-P4 only — ES8311 codec)

- [ ] **Playback** — output audio to onboard speaker header (I2S TX)
- [ ] **Recording** — capture from onboard MEMS microphone (I2S RX)
- [ ] **I2S passthrough** — raw PCM stream over network (UDP / WebSocket)
- [ ] **Tone / beep generator** — software-generated sine/square wave
- [ ] **MP3 / AAC decode** — stream or file playback (`esp-adf` audio pipeline)
- [ ] **Voice activity detection (VAD)**
- [ ] **Wake word detection** — local keyword spotting
- [ ] No audio

---

## 12. Time & Scheduling

- [ ] **SNTP / NTP** — sync RTC to internet time server (`esp_sntp`)
- [ ] **RTC (internal)** — keep time in deep sleep across reboots
- [ ] **External RTC** — DS3231 / PCF8563 (I2C, battery-backed)
- [ ] **Cron-style scheduler** — run tasks at fixed times/intervals
- [ ] **Timestamp logging** — tag readings/events with ISO-8601 time
- [ ] No time awareness needed

---

## 13. Provisioning & Configuration

- [ ] **Wi-Fi provisioning (BLE)** — phone app sets SSID/password via BLE (`wifi_provisioning`)
- [ ] **Wi-Fi provisioning (SoftAP)** — captive portal on device hotspot
- [ ] **NVS config via web UI** — settings page saves JSON to NVS
- [ ] **Config file on SD/SPIFFS** — read `config.json` at boot
- [ ] **Factory reset** — hold button N seconds to wipe NVS and reboot
- [ ] **QR code on display** — show provisioning QR at first boot
- [ ] **Hardcoded / no provisioning** — credentials baked into firmware

---

## 14. Security

- [ ] **TLS 1.2 / 1.3** — all network traffic encrypted (`esp_tls` / `mbedtls`)
- [ ] **Certificate pinning** — reject unexpected server certs
- [ ] **HTTPS web server** (`esp_https_server`)
- [ ] **HTTP Basic Auth** — username + password on web endpoints
- [ ] **API token / Bearer auth** — token in `Authorization` header
- [ ] **Encrypted NVS** — AES-XTS partition encryption
- [ ] **Secure boot v2** — signed firmware, eFuse locked (`esp_secure_cert`)
- [ ] **Flash encryption** — ciphertext stored on flash
- [ ] **Mutual TLS (mTLS)** — client certificate authentication
- [ ] **WPA2 Enterprise** — 802.1X network auth
- [ ] No security (trusted local network / prototyping)

---

## 15. System / RTOS / Architecture

**Tasks & synchronisation:**
- [ ] **FreeRTOS tasks** — separate tasks per subsystem (network, UI, sensors)
- [ ] **Task notifications** — lightweight single-value signals between tasks
- [ ] **Queues** — pass data structs between tasks (FreeRTOS queue)
- [ ] **Semaphores / mutexes** — shared resource protection
- [ ] **Event groups** (`esp_event` loop) — broadcast system-wide events
- [ ] **Ring buffer** — lock-free data stream between tasks (`esp_ringbuf`)

**Timers:**
- [ ] `esp_timer` — high-res one-shot / periodic software timer
- [ ] FreeRTOS software timer — lower-res, runs in timer task
- [ ] Hardware `gptimer` — cycle-accurate callbacks

**Power:**
- [ ] **Light sleep** — CPU paused, peripherals on, ~µA wake latency (`esp_pm`)
- [ ] **Deep sleep** — full power-off, wake on timer / GPIO / touch / ULP
- [ ] **ULP coprocessor** — run sensor reads while main CPU sleeps (ESP32-S / P4)
- [ ] **Modem sleep** — Wi-Fi radio off between DTIM beacons
- [ ] **Power profiling** — log current draw for optimisation

**Watchdog & recovery:**
- [ ] **TWDT** — task watchdog, reset if any task starves
- [ ] **Interrupt watchdog** — reset on blocked ISR
- [ ] **Panic handler** — log core dump to flash on crash
- [ ] **Core dump** — save crash state to SPIFFS / SD for post-mortem

---

## 16. Debug, Logging & Diagnostics

- [ ] **ESP_LOG** (UART, 115200 bps) — `ESP_LOGI/W/E/D/V` structured log levels
- [ ] **USB-JTAG** — breakpoint debugging (ESP32-C3 / P4 built-in)
- [ ] **OpenOCD + GDB** — full debug session over JTAG
- [ ] **Core dump to flash** — post-mortem analysis after crash
- [ ] **Coredump upload** — send crash report to server (`esp_core_dump`)
- [ ] **ESP Insights** — cloud-based diagnostics and crash analytics (`esp_insights`)
- [ ] **Heap monitor** — log `heap_caps_get_free_size()` periodically
- [ ] **Stack high-water mark** — track per-task stack usage
- [ ] **Prometheus `/metrics`** — expose metrics for Grafana scraping
- [ ] **Syslog over UDP** — forward ESP_LOG to a syslog server
- [ ] **Interactive UART console** — `esp_console` + `argtable3` CLI commands
- [ ] **LED status indicator** — GPIO LED signals boot / connected / error states
- [ ] **Buzzer feedback** — audio cues on events (boot, error, alert)

---

## 17. ESP-IDF Components (idf_component.yml / idf-component-manager)

**Espressif managed components:**
- [ ] `espressif/esp_lcd_ili9341` — ILI9341 SPI panel driver
- [ ] `espressif/esp_lcd_gc9a01` — GC9A01 round display driver
- [ ] `espressif/esp_lcd_jd9365` — JD9365 MIPI DSI driver (ESP32-P4)
- [ ] `espressif/esp_lcd_touch_gt911` — GT911 touch driver
- [ ] `espressif/esp_lcd_touch_cst816s` — CST816x touch driver
- [ ] `espressif/lvgl__lvgl` — LVGL GUI library
- [ ] `espressif/esp_codec_dev` — ES8311 / ES8388 audio codec HAL
- [ ] `espressif/esp32_p4_function_ev_board` — BSP for JC-ESP32P4-M3-DEV
- [ ] `espressif/esp_websocket_client` — WebSocket client
- [ ] `espressif/esp_mqtt` — MQTT 3.1.1 / 5.0 client
- [ ] `espressif/esp_modem` — PPP modem / LTE (SIM7600 etc.)
- [ ] `espressif/esp_tinyusb` — USB device stack (CDC, HID, MSC)
- [ ] `espressif/esp_serial_slave_link` — SDIO/SPI slave link (inter-chip)
- [ ] `espressif/esp_hosted` — Wi-Fi/BT co-processor via SDIO/SPI
- [ ] `espressif/esp_insights` — cloud diagnostics
- [ ] `espressif/esp_rainmaker` — Espressif cloud + Alexa/Google Home
- [ ] `espressif/esp_matter` — Matter SDK (smart home standard)
- [ ] `espressif/esp-dsp` — DSP algorithms (FFT, FIR, IIR)
- [ ] `espressif/qrcode` — QR code generator (for display)
- [ ] `espressif/button` — GPIO button with debounce + long-press events
- [ ] `espressif/led_strip` — addressable LED (WS2812 / SK6812 via RMT)
- [ ] `espressif/led_indicator` — multi-pattern LED status indicator
- [ ] `espressif/esp_littlefs` — LittleFS file system
- [ ] `espressif/catch2` — unit testing framework (Catch2)

**Third-party / community:**
- [ ] `joltwallet/littlefs` — alternative LittleFS port
- [ ] `igrr/esp-jsmn` — lightweight JSON tokeniser
- [ ] `DFRobot/...` — sensor library components
- [ ] Other: ______

---

## 18. What should this app do?

<!-- This is the only free-text section. Describe the idea in plain language.
     Copilot will use every checked box above as the technical specification. -->


