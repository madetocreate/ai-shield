#!/bin/bash
# AI-Shield Smoke Test Script
# Führt grundlegende Health Checks und einen Test-Call durch

set -e

GATEWAY_URL="${GATEWAY_URL:-http://localhost:4050}"
CONTROL_PLANE_URL="${CONTROL_PLANE_URL:-http://localhost:4051}"
LITELLM_MASTER_KEY="${LITELLM_MASTER_KEY:-}"

echo "AI-Shield Smoke Tests"
echo "===================="
echo ""

# Prüfe ob curl verfügbar ist
if ! command -v curl &> /dev/null; then
  echo "ERROR: curl is required for smoke tests"
  echo "Install curl or use wget"
  exit 1
fi

# Health Check: Gateway
echo "1. Testing Gateway health..."
if curl -sf "${GATEWAY_URL}/health" > /dev/null 2>&1; then
  echo "   ✓ Gateway is healthy"
else
  echo "   ✗ Gateway health check failed"
  exit 1
fi

# Health Check: Control Plane
echo "2. Testing Control Plane health..."
if curl -sf "${CONTROL_PLANE_URL}/health" > /dev/null 2>&1; then
  echo "   ✓ Control Plane is healthy"
else
  echo "   ✗ Control Plane health check failed"
  exit 1
fi

# Test API Call (nur wenn Master Key gesetzt)
if [ -z "$LITELLM_MASTER_KEY" ]; then
  echo ""
  echo "⚠ Skipping API test (LITELLM_MASTER_KEY not set)"
  echo "   To test API calls, set LITELLM_MASTER_KEY:"
  echo "   export LITELLM_MASTER_KEY=your-key"
  echo "   ./scripts/smoke.sh"
else
  echo "3. Testing Gateway API call..."
  RESPONSE=$(curl -sf -X POST "${GATEWAY_URL}/v1/chat/completions" \
    -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
    -H "Content-Type: application/json" \
    -d '{
      "model": "gpt-4o-mini",
      "messages": [{"role": "user", "content": "Hello"}],
      "max_tokens": 10
    }' 2>&1)
  
  if [ $? -eq 0 ]; then
    echo "   ✓ API call successful"
  else
    echo "   ✗ API call failed"
    echo "   Response: $RESPONSE"
    exit 1
  fi
fi

echo ""
echo "✓ All smoke tests passed!"

