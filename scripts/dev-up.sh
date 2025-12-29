#!/bin/bash
# AI-Shield Dev Startup Script
# Startet alle Services mit korrekter ENV-Datei-Interpolation

set -e

# Default env file path
BACKEND_ENV_PATH="${BACKEND_ENV_PATH:-${HOME}/Documents/Backend-Secrets/backend.env}"

# Prüfe ob ENV-Datei existiert
if [ ! -f "$BACKEND_ENV_PATH" ]; then
  echo "ERROR: Environment file not found: $BACKEND_ENV_PATH"
  echo ""
  echo "Please create it or set BACKEND_ENV_PATH to point to your .env file"
  echo ""
  echo "Example:"
  echo "  export BACKEND_ENV_PATH=/path/to/backend.env"
  echo "  ./scripts/dev-up.sh"
  exit 1
fi

echo "Starting AI-Shield services..."
echo "Using env file: $BACKEND_ENV_PATH"
echo ""

# Starte Docker Compose mit --env-file
docker compose --env-file "$BACKEND_ENV_PATH" up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 5

# Health checks
echo ""
echo "Checking health endpoints..."

# Gateway health check
if command -v curl &> /dev/null; then
  if curl -sf http://localhost:4050/health > /dev/null 2>&1; then
    echo "✓ Gateway (port 4050) is healthy"
  else
    echo "✗ Gateway (port 4050) is not responding"
  fi

  # Control Plane health check
  if curl -sf http://localhost:4051/health > /dev/null 2>&1; then
    echo "✓ Control Plane (port 4051) is healthy"
  else
    echo "✗ Control Plane (port 4051) is not responding"
  fi
else
  echo "Warning: curl not found, skipping health checks"
  echo "Install curl to enable health checks"
fi

echo ""
echo "AI-Shield services started!"
echo ""
echo "Services:"
echo "  - Gateway:       http://localhost:4050"
echo "  - Control Plane: http://localhost:4051"
echo "  - Langfuse:      http://localhost:3000"
echo "  - Grafana:       http://localhost:3001"
echo ""
echo "To view logs:"
echo "  docker compose logs -f gateway"

