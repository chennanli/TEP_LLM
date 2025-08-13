#!/bin/bash

# TEP Integration - Backend Startup Script
# Starts the FastAPI backend with Claude LLM integration

set -e

echo "🏭 TEP Integration - Starting Backend"
echo "===================================="

# Check if we're in the right directory
if [ ! -f "src/backend/services/llm-analysis/app.py" ]; then
    echo "❌ Error: Please run this script from the integration folder"
    echo "   cd integration && ./start-backend.sh"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "../tep_env" ]; then
    echo "❌ Error: Virtual environment 'tep_env' not found"
    echo "   Please ensure tep_env is in the parent directory"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source ../tep_env/bin/activate

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Error: Python not found in virtual environment"
    exit 1
fi

# Navigate to backend directory
cd src/backend/services/llm-analysis

# Check if config file exists
if [ ! -f "config.json" ]; then
    echo "❌ Error: config.json not found in backend directory"
    exit 1
fi

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found in backend directory"
    exit 1
fi

echo "✅ Virtual environment activated"
echo "✅ Configuration file found"
echo "✅ Backend application found"
echo ""
echo "🚀 Starting FastAPI backend server..."
echo "📡 Backend will be available at: http://localhost:8000"
echo "📚 API documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the backend server
python app.py
