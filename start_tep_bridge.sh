#!/bin/bash

echo "🎛️ TEP-FaultExplainer Bridge Startup"
echo "===================================="

# Check if tep_env virtual environment exists
if [ ! -d "tep_env" ]; then
    echo "❌ tep_env virtual environment not found!"
    echo "   Please create it first with:"
    echo "   python3 -m venv tep_env"
    echo "   source tep_env/bin/activate"
    echo "   pip install your TEP requirements"
    exit 1
fi

# Activate your existing tep_env virtual environment
echo "🔄 Activating tep_env virtual environment..."
source tep_env/bin/activate

# Install required packages for TEP Bridge
echo "📥 Installing required packages in tep_env..."
pip install flask pandas numpy requests

# Install FaultExplainer backend requirements if needed
echo "📥 Installing FaultExplainer requirements..."
pip install fastapi uvicorn anthropic google-generativeai openai

# Check if FaultExplainer backend is running
echo "🔍 Checking FaultExplainer backend..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ FaultExplainer backend is running"
else
    echo "⚠️  FaultExplainer backend not detected on port 8000"
    echo "   Please start it first with:"
    echo "   cd external_repos/FaultExplainer-MultiLLM/backend"
    echo "   python main.py"
    echo ""
    echo "   Or continue anyway for data generation only"
fi

echo ""
echo "🚀 Starting TEP-FaultExplainer Bridge..."
echo "🌐 Open your browser to: http://localhost:8083"
echo ""

# Start the bridge
python tep_faultexplainer_bridge.py
