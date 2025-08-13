#!/bin/bash

# TEP Integration - Complete System Startup Script
# Starts both backend and frontend in background processes

set -e

echo "🏭 TEP Integration - Complete System Startup"
echo "============================================"

# Check if we're in the right directory
if [ ! -f "src/backend/services/llm-analysis/app.py" ] || [ ! -f "src/frontend/package.json" ]; then
    echo "❌ Error: Please run this script from the integration folder"
    echo "   cd integration && ./start-system.sh"
    exit 1
fi

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down TEP Integration system..."
    if [ ! -z "$BACKEND_PID" ]; then
        echo "   Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "   Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    echo "✅ System shutdown complete"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if virtual environment exists
if [ ! -d "../tep_env" ]; then
    echo "❌ Error: Virtual environment 'tep_env' not found"
    echo "   Please ensure tep_env is in the parent directory"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source ../tep_env/bin/activate

# Start backend in background
echo "🚀 Starting backend server..."
cd src/backend/services/llm-analysis
python app.py &
BACKEND_PID=$!
cd ../../../..

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Check if backend is running
if ! curl -s http://localhost:8000/status > /dev/null 2>&1; then
    echo "❌ Error: Backend failed to start"
    cleanup
fi

echo "✅ Backend running on http://localhost:8000"

# Start frontend in background
echo "🚀 Starting frontend server..."
cd src/frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!
cd ../..

# Wait for frontend to start
echo "⏳ Waiting for frontend to initialize..."
sleep 10

echo ""
echo "🎉 TEP Integration System is running!"
echo ""
echo "🌐 Access Points:"
echo "   • Frontend Dashboard: http://localhost:5173"
echo "   • Backend API: http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/docs"
echo ""
echo "🎛️ Features Available:"
echo "   • Real-time TEP monitoring with 33 operational ranges"
echo "   • Claude LLM integration for fault analysis"
echo "   • PCA-based anomaly detection"
echo "   • Enhanced charts with smart Y-axis scaling"
echo ""
echo "📊 Process IDs:"
echo "   • Backend PID: $BACKEND_PID"
echo "   • Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Wait for user to stop the system
wait
