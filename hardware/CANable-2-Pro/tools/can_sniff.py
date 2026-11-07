# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyserial>=3.5",
#     "python-can>=4.6.1",
# ]
# ///
"""Sniff a CAN bus through a CANable 2 (slcan firmware) on macOS/Windows/Linux.

Usage:
    uv run can_sniff.py [PORT] [BITRATE] [DURATION]

Defaults can also be set via env vars CAN_PORT / CAN_BITRATE.
Example:
    uv run can_sniff.py /dev/cu.usbmodem207E337F38451 125000 10
"""
import os, sys, time, collections
import can

PORT = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CAN_PORT", "/dev/cu.usbmodem207E337F38451")
BITRATE = int(sys.argv[2]) if len(sys.argv) > 2 else int(os.environ.get("CAN_BITRATE", "125000"))
DURATION = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0

bus = can.Bus(interface="slcan", channel=PORT, bitrate=BITRATE)
print(f"Listening on {PORT} @ {BITRATE} bit/s for {DURATION:.0f}s...\n")

count = 0
seen = collections.Counter()
end = time.time() + DURATION
try:
    while time.time() < end:
        msg = bus.recv(timeout=0.5)
        if msg is None:
            continue
        count += 1
        seen[msg.arbitration_id] += 1
        if count <= 20:
            data = " ".join(f"{b:02X}" for b in msg.data)
            print(f"ID 0x{msg.arbitration_id:03X}  [{msg.dlc}]  {data}")
finally:
    bus.shutdown()

print(f"\nTotal frames: {count}")
if seen:
    print(f"Unique IDs : {len(seen)}")
    top = ", ".join(f"0x{i:03X}({n})" for i, n in seen.most_common(8))
    print("Busiest IDs:", top)
else:
    print("No frames received. Check bitrate, wiring (CANH/CANL), CAN-side ground, and termination.")
