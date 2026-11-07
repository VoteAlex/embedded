import json, sys
label = sys.argv[1]
j = json.load(sys.stdin)["jobs"][0]
for k in ("read", "write"):
    d = j[k]
    if d["io_bytes"]:
        print("%-16s %-5s %8.1f MB/s %9.0f IOPS  lat %7.2f ms" % (
            label, k, d["bw"]/1024, d["iops"], d["lat_ns"]["mean"]/1e6))
