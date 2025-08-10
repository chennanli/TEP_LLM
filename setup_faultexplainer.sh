#!/bin/bash
"""
Setup script for FaultExplainer integration
Ensures all dependencies are installed
"""

echo "🔧 Setting up FaultExplainer integration..."

# Check if we're in the right directory
if [ ! -d "external_repos/FaultExplainer-main" ]; then
    echo "❌ FaultExplainer-main not found. Please ensure you're in the correct directory."
    exit 1
fi

# Setup backend dependencies
echo "📦 Installing backend dependencies..."
cd external_repos/FaultExplainer-main/backend
pip install -r requirements.txt

# Setup frontend dependencies
echo "📦 Installing frontend dependencies..."
cd ../frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm packages..."
    npm install
else
    echo "✅ npm packages already installed"
fi

# Return to root directory
cd ../../../

echo "✅ FaultExplainer setup complete!"
echo ""
echo "🚀 Now you can use the Unified Control Panel:"
echo "   1. Start: python unified_tep_control_panel.py"
echo "   2. Open: http://localhost:9001"
echo "   3. Click buttons to start components"
echo ""
echo "📊 Data Flow:"
echo "   TEP Simulation (3min) → PCA Analysis (6min) → LLM Diagnosis (12min)"
echo ""
echo "🎛️ Controls:"
echo "   - IDV range: 0.0 to 1.0 (corrected)"
echo "   - Threshold: 0.01 (corrected)"
echo "   - Single interface for all components"
