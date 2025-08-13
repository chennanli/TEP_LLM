#!/bin/bash

# TEP Integration - Frontend Startup Script
# Starts the React frontend with Vite dev server

set -e

echo "🌐 TEP Integration - Starting Frontend"
echo "===================================="

# Check if we're in the right directory
if [ ! -f "src/frontend/package.json" ]; then
    echo "❌ Error: Please run this script from the integration folder"
    echo "   cd integration && ./start-frontend.sh"
    exit 1
fi

# Check if virtual environment exists (for consistency)
if [ ! -d "../tep_env" ]; then
    echo "❌ Error: Virtual environment 'tep_env' not found"
    echo "   Please ensure tep_env is in the parent directory"
    exit 1
fi

# Activate virtual environment (for consistency with backend)
echo "🔧 Activating virtual environment..."
source ../tep_env/bin/activate

# Navigate to frontend directory
cd src/frontend

# Check if Node.js is available
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm not found. Please install Node.js"
    exit 1
fi

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found in frontend directory"
    exit 1
fi

# Check if node_modules exists, install if not
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

echo "✅ Virtual environment activated"
echo "✅ Frontend dependencies ready"
echo ""
echo "🚀 Starting React frontend with Vite..."
echo "🌐 Frontend will be available at: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the frontend server
npm run dev
