#!/bin/bash

# Quick GCP Connection Test Runner
# Use this script to quickly retest GCP connections after fixing configuration

echo "🔄 Restarting Docker containers..."
docker-compose down
docker-compose up -d

echo "⏳ Waiting for containers to be ready..."
sleep 10

echo "🧪 Running GCP connection tests..."
docker exec -it ai-trip-planner-backend-api-1 bash -c "cd /app && python tests/test_gcp_connections.py"

echo ""
echo "🎯 Tip: Check the diagnosis file for detailed fixes:"
echo "   cat scripts/gcp_diagnosis.md"
