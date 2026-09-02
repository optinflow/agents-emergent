#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
TIMESTAMP=$(date -u +%Y%m%d-%H%M%S)
BACKUP_DIR="./data/backups"
mkdir -p "$BACKUP_DIR"
ARCHIVE="$BACKUP_DIR/backup-$TIMESTAMP.tar.gz"
tar -czf "$ARCHIVE" -C data --exclude=backups .
echo "Backup created: $ARCHIVE"
