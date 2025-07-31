#!/bin/bash

echo "🎛️ TEP-FaultExplainer Complete Startup"
echo "======================================"

# Check if tep_env virtual environment exists
if [ ! -d "tep_env" ]; then
    echo "❌ tep_env virtual environment not found!"
    echo ""
    echo "🔧 Creating tep_env virtual environment..."
    python3 -m venv tep_env
    
    echo "🔄 Activating tep_env..."
    source tep_env/bin/activate
    
    echo "📥 Installing basic requirements..."
    pip install --upgrade pip
    pip install numpy pandas matplotlib flask requests
    pip install fastapi uvicorn anthropic google-generativeai openai python-multipart
    
    echo "✅ tep_env created and configured!"
else
    echo "✅ Found existing tep_env virtual environment"
fi

echo ""
echo "🚀 Starting Services..."
echo ""

# Function to start FaultExplainer backend
start_faultexplainer() {
    echo "🤖 Starting FaultExplainer Backend..."
    source tep_env/bin/activate

    # Install missing dependencies
    pip install python-dotenv

    cd external_repos/FaultExplainer-MultiLLM/backend
    python app.py &
    FAULTEXPLAINER_PID=$!
    cd ../../..
    echo "✅ FaultExplainer Backend started (PID: $FAULTEXPLAINER_PID)"
}

# Function to start TEP Bridge
start_tep_bridge() {
    echo "🎛️ Starting TEP Bridge..."
    sleep 3  # Wait for FaultExplainer to start
    source tep_env/bin/activate
    python tep_faultexplainer_bridge.py &
    TEP_BRIDGE_PID=$!
    echo "✅ TEP Bridge started (PID: $TEP_BRIDGE_PID)"
}

# Start services
start_faultexplainer
start_tep_bridge

echo ""
echo "🎯 All Services Started!"
echo "========================"
echo "🤖 FaultExplainer Backend: http://localhost:8000"
echo "🎛️ TEP Bridge Interface:   http://localhost:8083"
echo "🌐 FaultExplainer Frontend: http://localhost:3000 (if running)"
echo ""
echo "📋 Next Steps:"
echo "1. Open http://localhost:8083 in your browser"
echo "2. Click '📊 Run Normal Operation' to establish baseline"
echo "3. Select fault type and click '🚨 Start Fault Simulation'"
echo "4. View LLM explanations in the interface"
echo ""
echo "⏹️  Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
trap 'echo ""; echo "🛑 Stopping all services..."; kill $FAULTEXPLAINER_PID $TEP_BRIDGE_PID 2>/dev/null; exit 0' INT

# Keep script running
wait
