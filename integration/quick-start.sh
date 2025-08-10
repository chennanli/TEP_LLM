#!/bin/bash

# TEP Industrial Intelligence Platform - Quick Start Script
# This script gets you running today with minimal setup

set -e

echo "🏭 TEP Industrial Intelligence Platform - Quick Start"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

echo "✅ Docker is running"

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating environment file..."
    cat > .env << EOF
# LLM API Keys (replace with your actual keys)
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here

# Development settings
ENVIRONMENT=development
USE_DATABASE=false
EOF
    echo "✅ Created .env file - please update with your API keys"
fi

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/{raw,processed,models,knowledge-base}

# Build and start services
echo "🚀 Building and starting services..."
echo "This may take a few minutes on first run..."

docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up -d

echo "⏳ Waiting for services to be ready..."
sleep 15

# Health check function
check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo "🔍 Checking $service_name..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo "✅ $service_name is ready"
            return 0
        fi
        
        echo "⏳ Waiting for $service_name (attempt $attempt/$max_attempts)..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name failed to start"
    return 1
}

# Check all services
echo "🏥 Performing health checks..."

check_service "API Gateway" "http://localhost:8000/health"
check_service "TEP Simulation" "http://localhost:8001/health"
check_service "LLM Analysis" "http://localhost:8002/health"
check_service "Frontend" "http://localhost:3000"

echo ""
echo "🎉 TEP Industrial Intelligence Platform is ready!"
echo ""
echo "🌐 Access Points:"
echo "   • Main Dashboard: http://localhost:3000"
echo "   • API Gateway: http://localhost:8000"
echo "   • API Docs: http://localhost:8000/docs"
echo ""
echo "🎛️ Quick Test:"
echo "   1. Open http://localhost:3000"
echo "   2. Click 'Control Panel' tab"
echo "   3. Click 'Start Simulation'"
echo "   4. Watch real-time data in other tabs"
echo ""
echo "📚 Next Steps:"
echo "   • Update API keys in .env file for LLM analysis"
echo "   • Explore the unified dashboard with 5 tabs"
echo "   • Test fault injection and anomaly detection"
echo ""
echo "🛑 To stop all services:"
echo "   docker-compose -f docker-compose.dev.yml down"
echo ""

# Show running containers
echo "📊 Running Services:"
docker-compose -f docker-compose.dev.yml ps
