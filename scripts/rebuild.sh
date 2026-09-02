#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose -f infrastructure/docker-compose.yml --env-file .env build --no-cache
docker compose -f infrastructure/docker-compose.yml --env-file .env up -d
echo "Rebuilt images from the Dockerfiles. Data volumes were not touched."
