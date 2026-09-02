#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose -f infrastructure/docker-compose.yml --env-file .env down
echo "Stopped. Volumes under ./data are untouched."
