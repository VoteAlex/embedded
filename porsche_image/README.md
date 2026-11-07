# porsche_image

A Raspberry Pi 5 image that boots straight into a Chromium kiosk showing
porsche.com, built with [rpi-image-gen](https://github.com/raspberrypi/rpi-image-gen).
Modelled on the upstream `examples/webkiosk`.

Debian Trixie (`trixie-minbase`) with the Raspberry Pi vendor repo, kernel and
firmware. Root lives on NVMe behind a Geekworm X1001 HAT at PCIe Gen 3.

Everything is built on a Mac inside an arm64 Debian container, so nothing is
installed on the host beyond Apple's `container` CLI.

## Build

```bash
./build.sh
```

Artefacts land in `out/`. The login is `pi` / `pi`; set `PASSWORD=` to change it.
Your `~/.ssh/id_ed25519.pub` is baked in, so SSH works without it either way.

Put WLAN credentials in `.wifi` (git-ignored) to have them baked in:

```sh
WIFI_SSID='FRITZ!Box 7590 JJ'
WIFI_PSK='...'
```

## Flashing

The NVMe cannot overwrite itself while it is the running root, so the SD card
is used as a stepping stone. All four steps run over SSH from the Mac.

1. Write the image to the SD card of the running Pi (~100 s):

```bash
ssh pi@PI 'sudo sh -c "zstd -dc | dd of=/dev/mmcblk0 bs=4M iflag=fullblock conv=fsync status=progress"' \
  < out/porsche_image.img.zst
```

2. Boot from SD, then reboot:

```bash
ssh pi@PI 'sudo rpi-eeprom-config > /tmp/e && sed -i s/0xf416/0xf461/ /tmp/e && sudo rpi-eeprom-config --apply /tmp/e'
ssh pi@PI 'sudo systemctl reboot'
```

3. From the SD system, write the image to NVMe (~50 s) and grow the root:

```bash
ssh pi@PI 'sudo sh -c "zstd -dc | dd of=/dev/nvme0n1 bs=4M iflag=fullblock conv=fsync status=progress"' \
  < out/porsche_image.img.zst
ssh pi@PI 'sudo parted -s /dev/nvme0n1 resizepart 2 100% && sudo e2fsck -fy /dev/nvme0n1p2 && sudo resize2fs /dev/nvme0n1p2'
```

4. Boot from NVMe again, then reboot:

```bash
ssh pi@PI 'sudo rpi-eeprom-config > /tmp/e && sed -i s/0xf461/0xf416/ /tmp/e && sudo rpi-eeprom-config --apply /tmp/e'
ssh pi@PI 'sudo systemctl reboot'
```

`BOOT_ORDER` reads right to left: `0xf416` is NVMe, SD, USB; `0xf461` puts SD
first. The applied value only becomes visible after the reboot, because the Pi 5
writes it to the opposite half of its A/B EEPROM.

The image does not grow its root filesystem on its own, hence step 3.

Each flash gives the Pi a new machine-id and usually a new DHCP address. Find it
again with `arp -an | grep d8:3a:dd`.

## Files

| | |
|---|---|
| `config/porsche_image.yaml` | includes `trixie-minbase.yaml`, overrides the rest |
| `layer/porsche_image.yaml` | kiosk packages and the systemd service |
| `layer/porsche_image.d/for/rpi-boot-firmware/config.txt.d/` | `config.txt` fragments — PCIe Gen 3 |
| `kiosk.service.tpl` | template for the kiosk unit |
| `splash.tga` | boot splash, 24-bit uncompressed TGA |
| `build.sh`, `Containerfile` | the containerised build host |
