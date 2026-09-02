#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -z "${1:-}" ]; then
  echo "Usage: ./scripts/restore.sh <path-to-backup.tar.gz>"
  exit 1
fi
ARCHIVE="$1"
if [ ! -f "$ARCHIVE" ]; then
  echo "Backup archive not found: $ARCHIVE"
  exit 1
fi
mkdir -p data
tar -xzf "$ARCHIVE" -C data
echo "Restored volumes from $ARCHIVE into ./data"
