#!/usr/bin/env bash
# Bring the whole stack back up: databases first, then the backend.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "Starting databases..."
railway redeploy -s Postgres --from-source -y
railway redeploy -s MongoDB --from-source -y

echo "Deploying backend (builds from $ROOT)..."
cd "$ROOT"
railway up --service backend --detach

echo
echo "Triggered. Watch progress with:  railway status"
