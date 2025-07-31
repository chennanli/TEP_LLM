#!/bin/bash

echo "🤖 Starting FaultExplainer Backend"
echo "================================="

# Check if tep_env virtual environment exists
if [ ! -d "tep_env" ]; then
    echo "❌ tep_env virtual environment not found!"
    echo "   Please create it first with:"
    echo "   python3 -m venv tep_env"
    exit 1
fi

# Activate your existing tep_env virtual environment
echo "🔄 Activating tep_env virtual environment..."
source tep_env/bin/activate

# Install FaultExplainer requirements if needed
echo "📥 Installing FaultExplainer requirements..."
pip install fastapi uvicorn anthropic google-generativeai openai python-multipart python-dotenv

# Navigate to FaultExplainer backend
cd external_repos/FaultExplainer-MultiLLM/backend

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "❌ FaultExplainer app.py not found!"
    echo "   Make sure you're in the correct directory"
    exit 1
fi

echo ""
echo "🚀 Starting FaultExplainer Backend..."
echo "🌐 Backend will run on: http://localhost:8000"
echo "🌐 Frontend should be on: http://localhost:3000"
echo ""
echo "⏹️  Press Ctrl+C to stop"
echo ""

# Start the backend
python app.py
