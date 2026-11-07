# CANable 2 Pro — Test Tools (macOS / uv)

Small, self-contained scripts to verify a **CANable 2.0 Pro** (slcan firmware) and
sniff a CAN bus from macOS, Windows, or Linux. No SocketCAN required — the adapter
is driven as a USB serial (slcan) device.

## Requirements

- [`uv`](https://docs.astral.sh/uv/) (`brew install uv`)

That's it. Each script carries its Python dependencies inline (PEP 723), so
`uv run` builds and caches an environment automatically — no venv, no `pip install`.

## Find your serial port

The CANable enumerates as a USB modem/serial port:

```bash
ls /dev/cu.usbmodem*          # macOS
# Linux: /dev/ttyACM0   ·   Windows: COMx
```

Either pass the port as the first argument, or set it once:

```bash
export CAN_PORT=/dev/cu.usbmodem207E337F38451
```

## Scripts

### `can_scan.py` — auto-detect the bitrate (passive)

Opens the bus in **listen-only** mode at every standard bitrate (10 k … 1 M) and
counts frames. Never transmits, so it can't disturb the bus.

```bash
uv run can_scan.py                 # uses $CAN_PORT
uv run can_scan.py /dev/cu.usbmodem207E337F38451 2.5
```

### `can_sniff.py` — live frame sniffer

Opens the bus at a chosen bitrate and prints incoming frames plus a summary of the
busiest IDs.

```bash
uv run can_sniff.py                              # $CAN_PORT, 125 kbit/s, 10 s
uv run can_sniff.py $CAN_PORT 500000 20          # 500 kbit/s for 20 s
```

## No-file one-liners

```bash
# Firmware version (proves USB + MCU + firmware are alive)
uv run --with pyserial python -c "import serial,time; s=serial.Serial('$CAN_PORT',115200,timeout=0.5); s.write(b'V\r'); time.sleep(0.3); print(s.read(128))"

# Quick sniff
uv run --with python-can python -c "import can; b=can.Bus('slcan',channel='$CAN_PORT',bitrate=125000); [print(b.recv()) for _ in range(20)]"
```

## Troubleshooting "0 frames"

If the firmware responds to `V` but you see **no frames at any bitrate**, the
adapter is fine — the issue is on the CAN side:

1. **CAN-side ground.** The Pro is galvanically isolated, so the CAN side floats.
   Wire the screw-terminal **GND** to the bus ground or the transceiver has no
   common-mode reference and sees nothing.
2. **CANH/CANL** — check they aren't swapped or loose.
3. **Bus awake?** Many vehicle/body buses sleep with the ignition off.
4. **Termination** — enable the onboard 120 Ω only if the bus isn't already
   terminated at both ends (a healthy powered-off bus reads ~60 Ω across CANH–CANL).

## slcan command cheat-sheet

| Command | Meaning |
|---------|---------|
| `V\r` | firmware version |
| `S0..S8\r` | bitrate: 10k, 20k, 50k, 100k, 125k, 250k, 500k, 800k, 1M |
| `O\r` | open channel (normal — transmits + ACKs) |
| `L\r` | open channel (listen-only — passive) |
| `C\r` | close channel |
| `t<id><dlc><data>\r` | a CAN data frame |
