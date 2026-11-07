# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyserial>=3.5",
# ]
# ///
"""Auto-detect the bitrate of a CAN bus using a CANable 2 (slcan firmware).

Opens the bus in LISTEN-ONLY mode at each standard bitrate and counts frames,
so it never transmits or disturbs the bus.

Usage:
    uv run can_scan.py [PORT] [DWELL_SECONDS]

Default PORT can also be set via env var CAN_PORT.
"""
import os, sys, time
import serial

PORT = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CAN_PORT", "/dev/cu.usbmodem207E337F38451")
DWELL = float(sys.argv[2]) if len(sys.argv) > 2 else 2.5

# slcan speed codes
SPEEDS = [("S8", "1 Mbit/s"), ("S6", "500 kbit/s"), ("S5", "250 kbit/s"),
          ("S4", "125 kbit/s"), ("S3", "100 kbit/s"), ("S2", "50 kbit/s"),
          ("S1", "20 kbit/s"), ("S0", "10 kbit/s")]

s = serial.Serial(PORT, 115200, timeout=0.2)
time.sleep(0.2)
s.reset_input_buffer()
found = []
for code, label in SPEEDS:
    s.write(b"C\r"); time.sleep(0.1); s.read(64)            # close
    s.write(code.encode() + b"\r"); time.sleep(0.1); s.read(64)  # set speed
    s.write(b"L\r"); time.sleep(0.1); s.read(64)            # open LISTEN-ONLY
    s.reset_input_buffer()
    end = time.time() + DWELL
    buf = b""
    while time.time() < end:
        d = s.read(256)
        if d:
            buf += d
    s.write(b"C\r"); time.sleep(0.1); s.read(64)            # close
    frames = buf.count(b"\r")  # each slcan frame ends with CR
    flag = "  <-- TRAFFIC" if frames > 0 else ""
    print(f"{label:12} : {frames:4d} frame markers{flag}")
    if frames:
        found.append(label)
s.close()
print()
print("Bus speed appears to be:", ", ".join(found) if found else
      "NONE found - check CANH/CANL wiring, CAN-side ground, that the bus is awake (ignition on), and termination.")
