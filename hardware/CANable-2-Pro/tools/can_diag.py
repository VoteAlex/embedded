import os, sys, time, serial

PORT = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CAN_PORT", "/dev/cu.usbmodem207E337F38451")

def cmd(s, c, label):
    s.write(c + b"\r")
    time.sleep(0.15)
    resp = s.read(64)
    ok = b"\r" in resp
    err = b"\x07" in resp  # \a bell = error
    print(f"  {label:20s} -> {resp!r}  {'OK' if ok else 'ERR' if err else '???'}")
    return ok

s = serial.Serial(PORT, 115200, timeout=0.3)
time.sleep(0.3)
s.reset_input_buffer()

print(f"Port: {PORT}\n")
print("=== Checking slcan command responses ===")
cmd(s, b"C",  "Close channel")
cmd(s, b"S5", "Set 250 kbit/s")
ok = cmd(s, b"L",  "Open LISTEN-ONLY")

if ok:
    print("\nListening for 3 seconds at 250 kbit/s...")
    end = time.time() + 3
    buf = b""
    while time.time() < end:
        d = s.read(256)
        if d: buf += d
    frames = buf.count(b"\r")
    print(f"Raw bytes received: {len(buf)}")
    print(f"Frame markers (\\r): {frames}")
    if buf:
        print(f"First 100 bytes: {buf[:100]!r}")
else:
    print("\nListen-only mode FAILED - trying normal open (O)...")
    cmd(s, b"C",  "Close channel")
    cmd(s, b"S5", "Set 250 kbit/s")
    cmd(s, b"O",  "Open NORMAL")
    print("\nListening for 3 seconds...")
    end = time.time() + 3
    buf = b""
    while time.time() < end:
        d = s.read(256)
        if d: buf += d
    frames = buf.count(b"\r")
    print(f"Raw bytes received: {len(buf)}")
    print(f"Frame markers (\\r): {frames}")

cmd(s, b"C", "Close channel")
s.close()
