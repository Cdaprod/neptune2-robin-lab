#!/usr/bin/env bash
set -euo pipefail

IP="${1:-}"
PORT="${2:-8080}"
PTY="${PTY:-/tmp/neptune2-mks}"

if [[ -z "$IP" ]]; then
  echo "usage: $0 <printer-ip> [port]" >&2
  exit 2
fi

if ! command -v socat >/dev/null 2>&1; then
  echo "socat is required." >&2
  echo "macOS: brew install socat" >&2
  echo "Debian/Ubuntu: sudo apt install socat" >&2
  exit 1
fi

rm -f "$PTY"
echo "$PTY -> tcp:$IP:$PORT"
exec socat "PTY,link=${PTY},rawer,echo=0,waitslave" "TCP:${IP}:${PORT},keepalive,nodelay"
