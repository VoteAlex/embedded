#!/usr/bin/env bash
#
#   ./build.sh                  # image lands in ./out
#   PASSWORD=secret ./build.sh  # defaults to "pi"
#   CLEAN=1 ./build.sh          # discard the cached work volume first
#
# Everything runs in an arm64 Debian container; nothing is installed on the Mac.

set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE=porsche-image-builder:trixie
VOLUME=porsche-image-work

[[ "$(container system status 2>/dev/null)" == *running* ]] || container system start
container image list | grep -q "^${IMAGE%%:*} " || container build -t "$IMAGE" -f "$HERE/Containerfile" "$HERE"
[[ "${CLEAN:-}" == 1 ]] && container volume delete "$VOLUME" 2>/dev/null
container volume inspect "$VOLUME" >/dev/null 2>&1 || container volume create -s 32G "$VOLUME" >/dev/null

# A key is passed as a file; a literal value would be expanded in the chroot.
cp "${SSH_PUBKEY:-$HOME/.ssh/id_ed25519.pub}" "$HERE/.ssh-pubkey"

# WIFI_SSID/WIFI_PSK live in .wifi (git-ignored). iwd names profiles after the
# SSID, hex-escaped as =<hex>.psk when it holds anything outside [A-Za-z0-9_-].
[[ -r "$HERE/.wifi" ]] && . "$HERE/.wifi"
wifi=""
if [[ -n "${WIFI_SSID:-}" ]]; then
  mkdir -p "$HERE/.wifi-profile"
  f="=$(printf %s "$WIFI_SSID" | xxd -p | tr -d '\n').psk"
  printf '[Security]\nPassphrase=%s\n' "$WIFI_PSK" > "$HERE/.wifi-profile/$f"
  wifi="IGconf_iwd_profile=/src/.wifi-profile/$f"
fi
trap 'rm -rf "$HERE/.ssh-pubkey" "$HERE/.wifi-profile"' EXIT

PASSWORD="${PASSWORD:-pi}"
mkdir -p "$HERE/out"

# CAP_SYS_ADMIN: Apple's runtime drops it, mmdebstrap needs it to mount.
container run --rm --cap-add CAP_SYS_ADMIN -u root \
  -v "$HERE:/src" -v "$VOLUME:/work" -v "$HERE/out:/out" -w /src \
  -e "PW=$PASSWORD" -e "WIFI=$wifi" --entrypoint /bin/bash "$IMAGE" -c '
    set -eu
    rpi-image-gen build -S /src -c porsche_image.yaml -B /work -- \
      "IGconf_device_user1passhash=$(openssl passwd -6 "$PW")" ${WIFI:+"$WIFI"}
    find /work -maxdepth 2 \( -name "*.img" -o -name "*.img.*" \) -exec cp -av {} /out/ \;'

echo
echo "image:    out/porsche_image.img.zst"
echo "login:    ssh pi@<ip>   password: $PASSWORD"
echo "flashing: see README"
