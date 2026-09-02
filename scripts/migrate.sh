#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== Step 1/4: Verify Docker =="
if ! command -v docker &> /dev/null; then
  echo "Docker is not installed. Install Docker + Docker Compose first."
  exit 1
fi

echo "== Step 2/4: Restore data (optional) =="
if [ -n "${1:-}" ]; then
  ./scripts/restore.sh "$1"
else
  echo "No backup archive passed - skipping restore. Usage: ./scripts/migrate.sh <backup.tar.gz>"
fi

echo "== Step 3/4: Load secrets =="
if [ ! -f .env ]; then
  echo "No .env found. Copy .env.example to .env and fill in secrets first."
  exit 1
fi

echo "== Step 4/4: Start the stack =="
./scripts/start.sh
echo "Migration complete. Same Linux computer restored."
