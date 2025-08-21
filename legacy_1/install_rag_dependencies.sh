#!/bin/bash

# Install RAG Dependencies for TEP Legacy System
# Optional: Only run this if you want RAG (knowledge base) capabilities

set -e

echo "📚 TEP RAG Dependencies Installation"
echo "===================================="

# Check if virtual environment exists
if [ ! -d "../tep_env" ]; then
    echo "❌ Error: Virtual environment 'tep_env' not found"
    echo "   Please ensure tep_env is in the parent directory"
    exit 1
fi

echo "🔧 Activating virtual environment..."
source ../tep_env/bin/activate

echo "📦 Installing RAG dependencies..."
echo "This may take a few minutes..."
echo ""

# Install RAG dependencies
pip install chromadb sentence-transformers PyPDF2

echo ""
echo "✅ RAG dependencies installed successfully!"
echo ""
echo "🎯 Next steps to enable RAG:"
echo "1. Add PDF documents to: external_repos/FaultExplainer-main/log_materials/"
echo "2. Start the legacy system: ./start_legacy_system.sh"
echo "3. The backend will now include RAG capabilities"
echo ""
echo "📚 RAG Features:"
echo "   • Knowledge base from PDF documents"
echo "   • Enhanced LLM responses with citations"
echo "   • Semantic search of troubleshooting procedures"
echo "   • Source attribution in fault analysis"
echo ""
echo "🔍 Test RAG installation:"
echo "   cd external_repos/FaultExplainer-main/backend"
echo "   python test_rag_integration.py"
