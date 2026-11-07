# Raspberry Pi 5 (8 GB) + Geekworm X1001 — Hardware Reference

> Quad-core Cortex-A76 SBC with a single exposed PCIe 2.0 lane. Paired here with the
> **Geekworm X1001** M.2 M-Key HAT, which turns that lane into a full NVMe boot drive.
> This sheet documents the **as-built unit** named `porsche`, used as the target for the
> Ferdinand infotainment stack.

- **Board:** Raspberry Pi 5 Model B Rev 1.0, 8 GB
- **Revision code:** `d04170` · **Serial:** `8a1b54831d689712`
- **HAT:** Geekworm X1001 — PCIe to M.2 NVMe (M-Key, top-mounted)
- **SSD fitted:** Samsung SSD 960 EVO 500 GB (`S3EUNB0J403559E`, FW `2B7QCXE7`)
- **Cooling:** Official Active Cooler (PWM fan + heatsink)
- **Product page:** https://www.raspberrypi.com/products/raspberry-pi-5/
- **X1001 wiki:** https://wiki.geekworm.com/X1001
- **Datasheet:** https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-product-brief.pdf

> ⚠️ **X1001 vs X1000/X1011:** The **X1001** mounts the SSD on **top** of the Pi and supports
> 2230/2242/2260/2280. The X1000 is a bottom-mount for 2230/2242 only, the X1011 a bottom-mount
> for 2280. All three use the same single PCIe lane — none of them is faster than the others.

---

## Table of Contents

1. [Specifications](#specifications)
2. [PCIe and the X1001 HAT](#pcie-and-the-x1001-hat)
3. [Booting from NVMe](#booting-from-nvme)
4. [Migrating an existing SD install to NVMe](#migrating-an-existing-sd-install-to-nvme)
5. [Measured performance — SD vs NVMe](#measured-performance--sd-vs-nvme)
6. [Active Cooler / fan control](#active-cooler--fan-control)
7. [Power budget](#power-budget)
8. [NVMe health monitoring](#nvme-health-monitoring)
9. [Headless setup notes](#headless-setup-notes)
10. [Tuning applied to this unit](#tuning-applied-to-this-unit)
11. [Known pitfalls](#known-pitfalls)

---

## Specifications

| Specification | Value |
|---------------|-------|
| **SoC** | Broadcom BCM2712 |
| **CPU** | 4 × Arm Cortex-A76 @ 2.4 GHz, 64-bit |
| **Cache** | 512 KB L2 per core, 2 MB shared L3 |
| **GPU** | VideoCore VII, OpenGL ES 3.1, Vulkan 1.2 |
| **RAM** | 8 GB LPDDR4X-4267 (7.9 GiB usable) |
| **PCIe** | 1 × PCIe 2.0 lane on the FFC connector; Gen 3 possible but *not* officially certified |
| **Southbridge** | RP1 (USB, Ethernet, GPIO) on a second internal PCIe link |
| **Networking** | Gigabit Ethernet, Wi-Fi 802.11ac dual-band, Bluetooth 5.0 / BLE |
| **USB** | 2 × USB 3.0 (5 Gbit/s), 2 × USB 2.0 |
| **Display** | 2 × micro-HDMI, up to 4Kp60 each |
| **Storage** | microSD (SDR104), plus NVMe via the PCIe FFC |
| **Power** | USB-C PD, 5 V/5 A (25 W) recommended; 5 V/3 A works with reduced USB budget |
| **RTC** | Onboard, with battery connector (J5) |
| **Power button** | Yes — a real one, unlike on the Pi 4 |

---

## PCIe and the X1001 HAT

The Pi 5 exposes **exactly one** PCIe lane through a 16-pin flat flex connector. The X1001
routes that lane to an M.2 M-Key slot. Consequences worth knowing:

- The link is always **x1**. `lspci` reporting `Width x1 (downgraded)` against a `Width x4`
  capability is **normal** for a four-lane SSD — not a fault, not a seating problem.
- Default link speed is **Gen 2 (5 GT/s)** ≈ 450 MB/s usable.
- **Gen 3 (8 GT/s)** ≈ 800 MB/s is unlocked with one line in `config.txt`. It is stable on most
  drives but is explicitly *not* guaranteed by Raspberry Pi — the trace lengths are not certified
  for it. Test before relying on it. Measured here: a clean **~2× over Gen 2**, zero link errors
  (see [Gen 2 vs Gen 3](#gen-2-vs-gen-3)). Under sustained load the SSD's temperature, not the
  link, becomes the limit.

```ini
# /boot/firmware/config.txt
dtparam=pciex1_gen=3
```

Verify what the link actually negotiated:

```sh
sudo lspci -vv -s 0001:01:00.0 | grep -E 'LnkCap:|LnkSta:'
# LnkCap: Speed 8GT/s, Width x4
# LnkSta: Speed 8GT/s, Width x1 (downgraded)   <- Gen 3 active, x1 as expected
```

If the drive is not listed by `lspci` at all, the FFC cable is the usual suspect: it is easy to
insert **reversed** or not fully seated. The contacts face the board on both ends.

---

## Booting from NVMe

The bootloader's `BOOT_ORDER` is a hex string read **right to left**, one nibble per attempt:

| Nibble | Meaning |
|--------|---------|
| `1` | SD card |
| `2` | Network / PXE |
| `3` | USB device boot |
| `4` | USB mass storage |
| `6` | **NVMe** |
| `f` | Restart the sequence (loop) |

So `0xf416` means: try **NVMe → SD → USB → repeat**. That ordering is the one to use — NVMe is
preferred, but a working SD card still rescues the board if the SSD ever fails.

```sh
sudo rpi-eeprom-config > /tmp/eeprom.conf
sed -i 's/^BOOT_ORDER=.*/BOOT_ORDER=0xf416/' /tmp/eeprom.conf
sudo rpi-eeprom-config --apply /tmp/eeprom.conf
sudo reboot
```

> Immediately after `--apply`, `rpi-eeprom-config` still prints the **old** value. That is
> expected: the Pi 5 uses an A/B bootloader and the new image only becomes current at the next
> boot. Verify after rebooting, not before.

A firmware update (`rpi-eeprom-update -a`) **preserves** `BOOT_ORDER` — verified on this unit.

---

## Migrating an existing SD install to NVMe

The GUI tool is **Raspberry Pi Imager → "Accessories → SD Card Copier"**, but on a headless box
the manual route is faster and fully scriptable. Done on this unit:

```sh
# 1. Partition: 512 MB FAT32 boot + rest ext4, MBR (msdos) label
sudo sgdisk --zap-all /dev/nvme0n1
sudo parted -s /dev/nvme0n1 mklabel msdos
sudo parted -s /dev/nvme0n1 mkpart primary fat32 1MiB 513MiB
sudo parted -s /dev/nvme0n1 set 1 boot on
sudo parted -s /dev/nvme0n1 mkpart primary ext4 513MiB 100%
sudo mkfs.vfat -F32 -n bootfs /dev/nvme0n1p1
sudo mkfs.ext4 -F -L rootfs  /dev/nvme0n1p2

# 2. Clone the live system (safe while running; services keep going)
sudo mount /dev/nvme0n1p2 /mnt/nvroot
sudo mkdir -p /mnt/nvroot/boot/firmware
sudo mount /dev/nvme0n1p1 /mnt/nvroot/boot/firmware
sudo rsync -aHAXx --info=progress2 \
  --exclude=/proc/* --exclude=/sys/* --exclude=/dev/* --exclude=/run/* \
  --exclude=/tmp/*  --exclude=/mnt/* --exclude=/media/* --exclude=/lost+found \
  / /mnt/nvroot/
sudo rsync -a /boot/firmware/ /mnt/nvroot/boot/firmware/

# 3. Repoint the clone at its OWN PARTUUID  <- the step everyone forgets
NEW=$(lsblk -no PARTUUID /dev/nvme0n1p1 | cut -d- -f1)
sudo sed -i "s/PARTUUID=<old>/PARTUUID=$NEW/g" /mnt/nvroot/etc/fstab
sudo sed -i "s/PARTUUID=<old>/PARTUUID=$NEW/g" /mnt/nvroot/boot/firmware/cmdline.txt
```

`rsync -x` keeps the copy on one filesystem, so `/proc`, `/sys` and bind mounts cannot be walked
into. `-HAX` preserves hardlinks, ACLs and xattrs — dropping them quietly breaks some packages.

**Skip `-x` at your peril:** without it, rsync will happily recurse into `/mnt/nvroot` itself.

---

## Measured performance — SD vs NVMe

Same board, same OS image, identical benchmark (`fio`, 1 GiB file, `--direct=1`, 20 s per test).
SD was a 128 GB card; NVMe is the 960 EVO at **PCIe Gen 3**.

| Test | SD card | NVMe Gen 3 | Factor |
|------|---------|------------|--------|
| Sequential read, 1 M | 90.3 MB/s | **788.2 MB/s** | 8.7× |
| Sequential write, 1 M | 22.7 MB/s | **694.3 MB/s** | 30.6× |
| Random read, 4 k QD32 | 3 899 IOPS | **194 502 IOPS** | 49.9× |
| Random write, 4 k QD32 | 729 IOPS | **125 858 IOPS** | 172.6× |
| Random read latency | 8.20 ms | **0.16 ms** | 51× |
| `multi-user.target` reached | 6.48 s | **3.47 s** | 1.9× |

Takeaways:

- Sequential throughput saturates the **single PCIe lane**, not the SSD. A newer drive will not
  go faster here — ~800 MB/s is the ceiling at Gen 3, ~450 MB/s at Gen 2.
- The real-world win is **random I/O**: ~170× on 4 k writes. That is what makes `apt`, builds,
  databases and log-heavy services feel like a different machine.
- Boot time barely moves, because it is dominated by service startup and network waits, not disk.

Reusable benchmark script: `tools/diskbench.sh` in this folder.

### Gen 2 vs Gen 3

Measured back to back on this unit by toggling `dtparam=pciex1_gen=3` and rebooting. Same file,
same `fio` parameters, so the two columns are directly comparable (they are from a later run than
the table above, hence the slightly different Gen 3 figures).

| Test | Gen 2 (5 GT/s) | Gen 3 (8 GT/s) | Factor |
|------|----------------|----------------|--------|
| Sequential read, 1 M | 431.1 MB/s | **852.5 MB/s** | 1.98× |
| Sequential write, 1 M | 382.7 MB/s | **752.3 MB/s** | 1.97× |
| Random read, 4 k QD32 | 108 034 IOPS | **212 585 IOPS** | 1.97× |
| Random write, 4 k QD32 | 95 459 IOPS | **135 877 IOPS** | 1.42× |

So yes — Gen 3 roughly **doubles** throughput, and on this drive it ran without a single PCIe
error (`lspci | grep -i AER`, `num_err_log_entries` stable, link never dropped to 5 GT/s).
Random writes gain less because the SSD's own flash, not the link, is the bottleneck there.

### Sustained load and thermal throttling

The numbers above are **bursts**. Under continuous mixed load the limit stops being the PCIe link
and becomes the SSD controller temperature:

| 2 min `randrw` 70/30, 64 k, QD32 ×4 | read | write | hotspot (`Temperature Sensor 2`) |
|---|---|---|---|
| Burst reference (20 s) | 852.5 MB/s | 752.3 MB/s | — |
| Cooler ~3 cm from the SSD | 500.5 MB/s | 215.0 MB/s | **85 °C** |
| Cooler repositioned over the SSD | 520.3 MB/s | 223.9 MB/s | **77 °C** |

The 960 EVO's own thresholds are `wctemp` 350 K = **77 °C** (warning) and `cctemp` 352 K =
**79 °C** (critical). Note that `temperature` / `Temperature Sensor 1` (the composite) stayed at a
harmless ~52 °C the whole time — **only sensor 2, the controller hotspot, hits the limit**. Reading
just the composite value hides the problem completely.

Also note what does *not* help: the Pi's Active Cooler is driven by the **SoC** thermal zone. The
SoC sat at 51 °C, so the fan stayed at step 1 (~2000 RPM) while the SSD was cooking 2 cm away.
Moving the cooler closer bought 8 °C and ~4 % throughput, but the drive still throttles.

If you need sustained Gen 3 throughput, give the M.2 module its **own heatsink**; the HAT ships
without one and the Pi's fan control will never react to the SSD.

---

## Active Cooler / fan control

The fan is driven by the kernel's thermal governor as a **cooling device**, not by a daemon.
Four speed steps are mapped to temperature trip points, so at idle it runs slowly and is close
to inaudible — which is regularly mistaken for a dead fan.

```sh
# Is it even recognised?
cat /sys/class/thermal/cooling_device0/type     # -> pwm-fan
cat /sys/class/thermal/cooling_device0/cur_state  # 0..4

# Actual RPM and PWM duty
cat /sys/class/hwmon/hwmon3/fan1_input          # e.g. 1717
cat /sys/class/hwmon/hwmon3/pwm1                # e.g. 75

# Force full speed to prove it spins, then release it
echo 4 | sudo tee /sys/class/thermal/cooling_device0/cur_state
echo 0 | sudo tee /sys/class/thermal/cooling_device0/cur_state
```

Measured on this unit: **step 1 = 1717 RPM**, **step 4 = 3436 RPM**. SoC sat at 52–57 °C under
the X1001, i.e. permanently in step 1.

Trip points can be shifted in `config.txt` if the default curve is too eager or too lazy:

```ini
dtparam=fan_temp0=50000,fan_temp0_hyst=5000,fan_temp0_speed=75
```

---

## Power budget

The Pi 5 negotiates its USB-C input and then decides how much it is willing to hand out.

| Supply | Peripheral budget | Notes |
|--------|-------------------|-------|
| 5 V / 5 A (25 W, official PSU) | 1.6 A across USB | Required for NVMe + spinning rust + hungry HATs |
| 5 V / 3 A (15 W) | 600 mA across USB | Pi throttles the USB budget and warns at boot |

An NVMe SSD draws **2–4 W** under load — comfortably inside the 25 W supply, but a 15 W charger
plus a power-hungry drive is a well-known source of random reboots and "drive disappeared" errors.

`usb_max_current_enable=1` in `config.txt` forces the full USB budget even when the PSU does not
advertise PD properly. Only set it if the supply genuinely delivers 5 A.

---

## NVMe health monitoring

```sh
sudo apt install nvme-cli
sudo nvme list
sudo nvme smart-log /dev/nvme0
```

Fields that matter:

| Field | On this unit | Meaning |
|-------|--------------|---------|
| `percentage_used` | 7 % | Share of rated write endurance consumed. >90 % = plan a replacement |
| `power_on_hours` | 11 833 h | Drive is second-hand; factor that into expectations |
| `power_cycles` | 2 598 | — |
| `temperature` | 31 °C | Composite sensor |
| `Temperature Sensor 2` | 47 °C | Controller — the one that throttles |
| `critical_warning` | 0 | Anything non-zero needs attention now |

**Watch sensor 2, not `temperature`.** On this drive the composite reads ~25 °C lower than the
controller hotspot. Under load the composite looked fine at 52 °C while sensor 2 was at 85 °C and
the drive was throttling hard — see
[Sustained load and thermal throttling](#sustained-load-and-thermal-throttling). The drive's own
limits are visible in `nvme id-ctrl`:

```sh
sudo nvme id-ctrl /dev/nvme0 | grep -E 'wctemp|cctemp'   # 350 K = 77 °C warn, 352 K = 79 °C crit
sudo nvme smart-log /dev/nvme0 | grep -i 'Temperature Sensor'
```

`nvme smart-log` printing `Invalid Field in Command` alongside valid output is harmless — the tool
probes optional log pages the drive does not implement. It is not a link problem.

TRIM is handled by the weekly `fstrim.timer` (enabled by default on Raspberry Pi OS). Prefer it
over the `discard` mount option — inline discard costs latency on every delete.

```sh
systemctl status fstrim.timer
sudo fstrim -v /
```

---

## Headless setup notes

- **Wi-Fi is not configured just because the hardware works.** A Pi imaged for Ethernet has *no*
  WLAN profile at all: `nmcli connection show` lists only the wired connection, and `wlan0` sits
  in `disconnected` forever. Diagnose in that order — radio, rfkill, regdomain, *then* profiles.

  ```sh
  nmcli radio                                  # WIFI enabled?
  cat /sys/class/rfkill/*/soft                 # 0 = not blocked
  sudo nmcli device wifi rescan && nmcli device wifi list
  sudo nmcli connection add type wifi con-name HomeWiFi ifname wlan0 ssid "<SSID>" \
       wifi-sec.key-mgmt wpa-psk wifi-sec.psk "<PSK>"
  ```

- **Keep Ethernet as the default route** when both are up, so an SSH session does not migrate
  mid-command. NetworkManager picks the profile with the *higher* `autoconnect-priority`, and the
  resulting route metric decides:

  ```sh
  sudo nmcli connection modify "Wired connection 1" connection.autoconnect-priority 50
  sudo nmcli connection modify HomeWiFi          connection.autoconnect-priority 10
  ip route   # eth0 metric 100 wins over wlan0 metric 600
  ```

- **A GPU-direct GUI needs a real display.** Anything using the DRM/KMS path (Slint `linuxkms`,
  Qt EGLFS, kmscube) exits immediately with no connected HDMI output and will crash-loop under
  systemd `Restart=always`. Check before blaming the application:

  ```sh
  for c in /sys/class/drm/card*-HDMI*; do echo "$c: $(cat $c/status)"; done
  ```

  To view such a UI remotely, run it inside a headless Wayland compositor (`cage` + `wayvnc`)
  rather than trying to attach VNC to the KMS console — there is no `/dev/fb0` to capture.

---

## Tuning applied to this unit

| Change | Why |
|--------|-----|
| `dtparam=pciex1_gen=3` | ~2× throughput over Gen 2, measured, zero link errors |
| `BOOT_ORDER=0xf416` | NVMe first, SD retained as rescue |
| `fstrim.timer` (default, verified) | Sustains NVMe write performance |
| `noatime` on `/` | Avoids a metadata write on every read |
| zram swap instead of a swap file | No SSD wear, faster than disk swap |
| `cloud-init` purged + `ds=nocloud` removed from `cmdline.txt` | Raspberry Pi Imager leftover; it sat in the critical boot chain for ~2.3 s |
| `NetworkManager-wait-online` disabled | Blocked boot for 5.2 s; nothing here needs it |
| `journald` capped at 200 MB | Default is 10 % of the filesystem — 45 GB on a 465 GB drive |
| SSH: pubkey only, password auth off | Standard hardening |

Boot profiling:

```sh
systemd-analyze time
systemd-analyze blame | head -15
systemd-analyze critical-chain
```

Net effect of the last three items: **12.58 s → 4.98 s** total startup, and 4.39 s once the
application stack was removed as well. What remained before that was the applications themselves
(`nats-sim` and `nats-gateway` at ~2.2 s each), not the OS.

---

## Known pitfalls

- **`lspci` shows `Width x1 (downgraded)`** — expected. The Pi 5 only has one lane.
- **`rpi-eeprom-config` prints the old `BOOT_ORDER` right after `--apply`** — A/B bootloader; it
  updates at the next boot. Verify after rebooting.
- **Cloning without fixing PARTUUIDs** gives a system that boots from NVMe but mounts the *SD*
  as root, so changes silently land on the wrong disk. Fix `fstab` **and** `cmdline.txt`.
- **The SD card becomes a frozen snapshot** the moment you switch. Useful as a rescue image,
  but it drifts out of date — do not treat it as a backup.
- **The fan appears dead at idle.** It is running at step 1; check `fan1_input` before replacing.
- **The Active Cooler does not cool the SSD.** Its fan curve follows the *SoC* thermal zone only.
  The SoC can idle at 51 °C while the NVMe controller sits at 85 °C and throttles — the fan will
  not spin up for it. Give the M.2 module its own heatsink.
- **`nvme smart-log` composite `temperature` hides the hotspot.** Read `Temperature Sensor 2`.
- **Underpowered PSU** causes USB current warnings and NVMe dropouts. Use the 27 W official unit.
- **No `/dev/fb0` on a Pi 5 with `vc4-kms-v3d`.** Legacy framebuffer tools and framebuffer
  screen-grab tricks do not work; everything goes through DRM.
- **A second-hand SSD can report high `power_on_hours`.** Check `percentage_used` before trusting
  it with anything that is not reproducible.

---

## This unit — current state

| Item | Value |
|------|-------|
| Hostname | `porsche` |
| OS | Debian GNU/Linux 13 (trixie), Raspberry Pi OS |
| Kernel | `6.18.60+rpt-rpi-2712` |
| Bootloader | 2026-10-30 |
| Root | `/dev/nvme0n1p2` (PARTUUID `23753786-02`), ext4, `noatime` |
| Boot | `/dev/nvme0n1p1` (PARTUUID `23753786-01`), vfat |
| PCIe link | 8 GT/s × 1 (Gen 3) |
| Ethernet | 192.168.178.158 (default route) |
| Wi-Fi | 192.168.178.150, profile `FRITZBox-JJ` (backup) |
| Boot time | 4.4 s to `multi-user.target` |
| RAM in use | ~266 MB idle |
| Workload | none — clean base system, ready for a new project |

The previous *Ferdinand* infotainment deployment (`nats-server`, `nats-gateway`, `nats-sim`,
`navi`, `media`, `infotainment-slint`, plus its D-Bus policy and `seatd`) was removed in
Nov 2026 after a full backup. Sources remain at `~/GitHub/ferdinand` on the Mac; the deploy
script pushed binaries to `/opt/infotainment/bin`. Tailscale was removed at the same time.
