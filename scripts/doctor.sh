#!/bin/bash
# AI-Shield Doctor Script
# Führt umfassende Health Checks durch

set -e

GATEWAY_URL="${GATEWAY_URL:-http://localhost:4050}"
CONTROL_PLANE_URL="${CONTROL_PLANE_URL:-http://localhost:4051}"

echo "AI-Shield Doctor"
echo "================"
echo ""

# Prüfe ob curl verfügbar ist
if ! command -v curl &> /dev/null; then
  echo "ERROR: curl is required for health checks"
  exit 1
fi

# Prüfe ob Docker Compose läuft
echo "1. Checking Docker Compose services..."
if docker compose ps | grep -q "ai-shield-gateway.*Up"; then
  echo "   ✓ Gateway container is running"
else
  echo "   ✗ Gateway container is not running"
  echo "   Run: ./scripts/dev-up.sh"
  exit 1
fi

if docker compose ps | grep -q "ai-shield-control-plane.*Up"; then
  echo "   ✓ Control Plane container is running"
else
  echo "   ✗ Control Plane container is not running"
  exit 1
fi

# Gateway Health Check
echo ""
echo "2. Checking Gateway health..."
if curl -sf "${GATEWAY_URL}/health" > /dev/null 2>&1; then
  echo "   ✓ Gateway is healthy"
  HEALTH_RESPONSE=$(curl -sf "${GATEWAY_URL}/health" 2>&1)
  echo "   Response: $HEALTH_RESPONSE"
else
  echo "   ✗ Gateway health check failed"
  echo "   URL: ${GATEWAY_URL}/health"
  exit 1
fi

# Control Plane Health Check
echo ""
echo "3. Checking Control Plane health..."
if curl -sf "${CONTROL_PLANE_URL}/health" > /dev/null 2>&1; then
  echo "   ✓ Control Plane is healthy"
  HEALTH_RESPONSE=$(curl -sf "${CONTROL_PLANE_URL}/health" 2>&1)
  echo "   Response: $HEALTH_RESPONSE"
else
  echo "   ✗ Control Plane health check failed"
  echo "   URL: ${CONTROL_PLANE_URL}/health"
  exit 1
fi

# Policy Engine Check (via gateway logs)
echo ""
echo "4. Checking Policy Engine..."
if docker compose logs gateway 2>&1 | grep -q "policy_engine\|ModuleNotFoundError"; then
  if docker compose logs gateway 2>&1 | grep -q "ModuleNotFoundError.*policy_engine"; then
    echo "   ✗ Policy Engine module not found (check volume mount)"
    exit 1
  else
    echo "   ✓ Policy Engine loaded (no errors in logs)"
  fi
else
  echo "   ⚠ Could not verify Policy Engine status from logs"
fi

# Control Plane Registry Check
echo ""
echo "5. Checking Control Plane registry endpoint..."
ADMIN_KEY="${CONTROL_PLANE_ADMIN_KEY:-${AI_SHIELD_ADMIN_KEY:-}}"
if [ -z "$ADMIN_KEY" ]; then
  echo "   ⚠ Skipping registry check (CONTROL_PLANE_ADMIN_KEY not set)"
else
  if curl -sf -H "x-ai-shield-admin-key: ${ADMIN_KEY}" \
    "${CONTROL_PLANE_URL}/v1/mcp/registry" > /dev/null 2>&1; then
    echo "   ✓ Registry endpoint accessible"
  else
    echo "   ⚠ Registry endpoint not accessible (may need auth)"
  fi
fi

# Policy Tests
echo ""
echo "6. Checking Policy Tests..."
if [ -f "apps/gateway/scripts/run_policy_tests.py" ]; then
  echo "   ✓ Policy test script found"
  echo "   Run manually: docker compose exec gateway python /app/scripts/run_policy_tests.py"
else
  echo "   ⚠ Policy test script not found"
fi

echo ""
echo "✓ All checks passed!"
echo ""
echo "Services:"
echo "  - Gateway:       ${GATEWAY_URL}"
echo "  - Control Plane: ${CONTROL_PLANE_URL}"
echo ""
echo "Next steps:"
echo "  - Run smoke tests: ./scripts/smoke.sh"
echo "  - View logs: docker compose logs -f gateway"

