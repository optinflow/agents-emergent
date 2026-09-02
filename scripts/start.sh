#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose -f infrastructure/docker-compose.yml --env-file .env up -d
echo "Personal AI Computer is starting. Dashboard: http://localhost:${FRONTEND_PORT:-3000}"
