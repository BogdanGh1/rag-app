#!/usr/bin/env bash
# Stop the whole stack: backend first, then databases.
# Removes the active deployments only — data volumes are preserved.
set -uo pipefail

echo "Stopping backend..."
railway down -s backend -y || true

echo "Stopping databases..."
railway down -s MongoDB -y || true
railway down -s Postgres -y || true

echo
echo "All services stopped. Volumes preserved. Bring back with ./deploy-up.sh"
