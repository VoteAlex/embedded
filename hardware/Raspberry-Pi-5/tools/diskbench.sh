#!/bin/bash
# Disk benchmark used for the SD vs NVMe comparison in ../SUMMARY.md
# Usage: ./diskbench.sh [target-directory]      (needs: fio, python3)
HERE=$(cd "$(dirname "$0")" && pwd)
D=${1:-$HOME/benchtmp}
mkdir -p "$D"
echo "### Ziel: $D  ($(df -h "$D" | tail -1 | awk "{print \$1}"))"
echo
run() {
  fio --name=bench --filename="$D/fio.tmp" --size=1G --direct=1 --ioengine=libaio \
      --rw="$2" --bs="$3" --iodepth="$4" --numjobs=1 --runtime=20 --time_based \
      --group_reporting --output-format=json 2>/dev/null | python3 "$HERE/fioparse.py" "$1"
}
run seq-read-1M   read      1M 8
run seq-write-1M  write     1M 8
run rand-read-4k  randread  4k 32
run rand-write-4k randwrite 4k 32
rm -f "$D/fio.tmp"
echo
echo "### Bootzeit"
systemd-analyze time
