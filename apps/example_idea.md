# App Idea — ESP32-P4 Network Device with Web Config Portal

> A wired-Ethernet IoT device powered over the network cable (PoE) that exposes a browser-based configuration and monitoring interface at `app.local`.

---

## 1. Target Hardware

| Field | Value |
|-------|-------|
| **Board** | JC-ESP32P4-M3-DEV |
| **MCU** | ESP32-P4 (dual-core RISC-V, 400 MHz) + ESP32-C6 co-processor |
| **Reference** | `hardware/ESP32-P4-M3-DEV/SUMMARY.md` |

### Peripherals in use

- [ ] Display (model: JD9365, resolution: 800 × 1280)
- [ ] Touch (model: GT911)
- [ ] Wi-Fi — via ESP32-C6 co-processor (fallback / provisioning only)
- [x] Ethernet (PHY: IP101, 100 Mbps RMII, RJ45 with integrated magnetics)
- [ ] Audio
- [ ] SD / TF card
- [ ] RS485 / UART
- [x] Battery / PoE — powered via PoE injector on the RJ45 cable (802.3af/at), no USB required in deployment
- [ ] Other

---

## 2. Goal & Scope

A self-contained network node that connects to the local LAN via a single Ethernet cable (which also delivers power via PoE). The device hosts a local web portal accessible at `app.local` where the user can view status and change settings without needing a phone app or cloud service.

**In scope:**
- Ethernet link with DHCP and mDNS (`app.local`)
- Embedded web server with a settings/config page
- Persistent config storage (NVS)
- On-device status display (current IP, link state, uptime)
- OTA firmware update via the web portal

**Out of scope:**
- Cloud connectivity or external APIs
- Mobile app
- Multi-user authentication (single admin, no auth for v1)

---

## 3. Connectivity

| Field | Value |
|-------|-------|
| **Interface** | Ethernet — IP101 PHY, RMII, MDC=GPIO31, MDIO=GPIO52, PWR/RST=GPIO51, CLK=GPIO50 |
| **Power over cable** | PoE (802.3af) via RJ45; 5 V rail feeds board; no USB needed in deployment |
| **mDNS / hostname** | `app.local` (configurable via web UI) |
| **Protocol** | HTTP REST + Server-Sent Events (SSE) for live updates |
| **Auth** | None for v1 (local LAN assumed trusted) |
| **OTA updates** | Yes — upload `.bin` via `/update` endpoint |

---

## 4. User Interface

### Web / Browser UI

- **`/` — Dashboard:** current IP address, link speed, uptime counter, any attached sensor readings
- **`/settings` — Configuration:** hostname, static IP toggle (DHCP vs manual), any app-specific parameters; saved to NVS on submit
- **`/update` — OTA:** drag-and-drop firmware `.bin` upload with progress bar
- Live data pushed via SSE (no polling needed in the browser)

### On-device display UI

- Boot screen: board logo + "Connecting…" spinner
- Main screen (LVGL): IP address, link status icon (up/down), uptime, hostname
- Touch: tap to cycle between status screens
- Error screen: red banner if Ethernet link is lost for > 5 s

---

## 5. Core Features

1. **Ethernet init** — bring up IP101 PHY via `esp_eth`, obtain IP via DHCP, register mDNS `app.local`
2. **HTTP web server** — `esp_http_server` serving static HTML/CSS/JS from SPIFFS + REST endpoints (`GET /api/status`, `POST /api/settings`)
3. **NVS config store** — read/write hostname, static IP settings, and app params as a JSON blob in NVS namespace `app_cfg`
4. **LVGL display** — status dashboard rendered on the 800 × 1280 MIPI panel, updated every second
5. **GT911 touch** — navigate between display screens
6. **OTA via HTTP** — `/update` endpoint triggers `esp_https_ota` (HTTP for LAN), validates image, reboots
7. **Link-loss recovery** — watchdog re-inits PHY if MDIO heartbeat fails for > 30 s

---

## 6. Data & Storage

| What | Where | Format |
|------|-------|--------|
| Configuration (hostname, IP, app params) | NVS namespace `app_cfg` | JSON string blob |
| Web assets (HTML, CSS, JS) | SPIFFS partition | Static files |
| Runtime status (IP, uptime, link state) | RAM struct, exposed via SSE | JSON |
| Logs | UART0 (115200 bps) | Plain text |

---

## 7. Framework & Libraries

| Role | Library | Version / notes |
|------|---------|-----------------|
| **Framework** | ESP-IDF | v5.5+ |
| **Ethernet driver** | `esp_eth` (built-in) | RMII + IP101 BSP |
| **mDNS** | `mdns` component (built-in) | |
| **Web server** | `esp_http_server` (built-in) | |
| **NVS** | `nvs_flash` (built-in) | |
| **OTA** | `esp_ota_ops` (built-in) | |
| **GUI** | LVGL v9 | via `idf_component.yml` |
| **Display driver** | JD9365 MIPI DSI (custom BSP) | from espressif BSP component |
| **Touch driver** | GT911 (custom BSP) | from espressif BSP component |
| **BSP** | `espressif__esp32_p4_function_ev_board` | matches this board |

---

## 8. Project Structure (suggested)

```
apps/esp32p4-web-portal/
├── main/
│   ├── main.c
│   ├── eth.c / eth.h          # Ethernet + mDNS init
│   ├── web_server.c / .h      # HTTP server, REST endpoints, SSE
│   ├── nvs_config.c / .h      # NVS read/write helpers
│   ├── ota.c / .h             # OTA update handler
│   └── ui/
│       ├── ui_main.c          # LVGL screen definitions
│       └── ui_main.h
├── components/
│   └── (none for v1)
├── spiffs_image/              # web assets built into SPIFFS
│   ├── index.html
│   ├── settings.html
│   ├── update.html
│   └── style.css
├── CMakeLists.txt
├── partitions.csv             # custom partition table with SPIFFS + OTA slots
├── sdkconfig.defaults
└── idf_component.yml          # LVGL + BSP dependencies
```

---

## 9. Constraints & Notes

- **PoE budget:** 802.3af delivers up to 15.4 W; the board + display draws well under that. No special handling needed beyond the onboard PoE module.
- **GPIO51 must be toggled HIGH** after boot to bring the IP101 PHY out of reset — do not skip this step.
- **RMII clock (GPIO50)** is an input sourced by the IP101; do not configure it as output.
- **MIPI DSI** lanes are routed internally — no numbered GPIO config needed for the display interface itself; backlight is GPIO23 (LEDC PWM).
- **I2C bus (GPIO7/GPIO8) is shared** between GT911 and ES8311 — initialise with I2C bus lock.
- SPIFFS partition must be declared in `partitions.csv` alongside two OTA app slots.
- Target web assets to < 200 KB total so they fit comfortably in a 512 KB SPIFFS partition.
- Avoid blocking the main task; run the HTTP server and LVGL refresh on separate FreeRTOS tasks.

---

## 10. Open Questions

- [ ] Does the deployment environment have a PoE switch, or will a PoE injector be used? (affects connector/cable planning only)
- [ ] Should the hostname be changeable at runtime via the web UI, or fixed at flash time?
- [ ] Any specific sensor or actuator to attach (I2C expansion header on GPIO7/GPIO8)?
- [ ] Should settings be password-protected in a future version?
