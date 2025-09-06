#!/bin/bash

# GCP Connection Test Runner
# This script runs the GCP connection tests within the Docker environment

set -e

echo "🧪 Running GCP Connection Tests..."
echo "=================================="

# Change to the project directory
cd /app

# Set Python path
export PYTHONPATH=/app:$PYTHONPATH

# Run the GCP connection tests
python tests/test_gcp_connections.py

echo "=================================="
echo "✅ GCP tests completed!"
