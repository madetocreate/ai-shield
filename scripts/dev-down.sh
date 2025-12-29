#!/bin/bash
# AI-Shield Dev Shutdown Script

set -e

echo "Stopping AI-Shield services..."

docker compose down

echo ""
echo "AI-Shield services stopped!"

