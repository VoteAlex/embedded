# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-can>=4.6.1",
#     "pyserial>=3.5",
# ]
# ///
"""Read live vehicle speed from an OBD-II port via a CANable 2 (slcan firmware).

Sends OBD-II Mode 01 / PID 0x0D (vehicle speed) requests and prints the reply.
Works on ISO 15765-4 (CAN) vehicles at 500 kbit/s, 11-bit IDs - e.g. Porsche
911 (997.2 / 991 / 992).

Wiring: OBD pin 6 -> CANH, pin 14 -> CANL, pin 4/5 -> GND. Disable the onboard
120 ohm termination (the car bus is already terminated). Ignition ON.

Usage:
    uv run read_speed.py [PORT] [BITRATE]
"""
import os, sys, time
import can

PORT = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CAN_PORT", "/dev/cu.usbmodem207E337F38451")
BITRATE = int(sys.argv[2]) if len(sys.argv) > 2 else int(os.environ.get("CAN_BITRATE", "500000"))

bus = can.Bus(interface="slcan", channel=PORT, bitrate=BITRATE)

# OBD-II: functional request ID 0x7DF, Mode 01, PID 0x0D = vehicle speed (km/h)
request = can.Message(
    arbitration_id=0x7DF,
    is_extended_id=False,
    data=[0x02, 0x01, 0x0D, 0x00, 0x00, 0x00, 0x00, 0x00],
)

print(f"Polling vehicle speed on {PORT} @ {BITRATE} bit/s (Ctrl-C to stop)...\n")
try:
    while True:
        bus.send(request)
        deadline = time.time() + 1.0
        got = False
        while time.time() < deadline:
            msg = bus.recv(timeout=1.0)
            if msg is None:
                continue
            d = msg.data
            # ECU positive responses use IDs 0x7E8..0x7EF; 0x41 = 0x40 + Mode 01
            if 0x7E8 <= msg.arbitration_id <= 0x7EF and len(d) >= 4 and d[1] == 0x41 and d[2] == 0x0D:
                kmh = d[3]
                print(f"Speed: {kmh:3d} km/h   ({kmh * 0.621371:5.1f} mph)")
                got = True
                break
        if not got:
            print("(no response - ignition on? bitrate 500k? CANH/CANL/GND wired? termination off?)")
        time.sleep(0.25)
except KeyboardInterrupt:
    print("\nStopped.")
finally:
    bus.shutdown()
