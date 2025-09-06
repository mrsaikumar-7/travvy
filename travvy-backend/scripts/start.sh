#!/bin/bash

# Travvy - Development Startup Script

echo "🚀 Starting Travvy Backend..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your configuration before continuing."
    exit 1
fi

# Start services with Docker Compose
echo "📦 Starting services with Docker Compose..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running!"
    echo ""
    echo "🌐 API Server: http://localhost:8000"
    echo "📖 API Docs: http://localhost:8000/docs"
    echo "🌺 Celery Monitor: http://localhost:5555"
    echo "🔧 Redis: localhost:6379"
    echo ""
    echo "📊 Check service status:"
    docker-compose ps
else
    echo "❌ Some services failed to start. Check logs:"
    docker-compose logs
fi
