#!/bin/bash
# Setup API Keys for TEP-FaultExplainer Integration
# This script helps users configure their API keys securely

echo "🔑 TEP-FaultExplainer API Key Setup"
echo "=================================="
echo ""

# Check if template files exist and copy them
LEGACY_TEMPLATE="legacy/external_repos/FaultExplainer-main/config.template.json"
LEGACY_CONFIG="legacy/external_repos/FaultExplainer-main/config.json"
INTEGRATION_TEMPLATE="integration/src/backend/services/llm-analysis/config.template.json"
INTEGRATION_CONFIG="integration/src/backend/services/llm-analysis/config.json"

if [ ! -f "$LEGACY_TEMPLATE" ]; then
    echo "❌ Legacy template file not found: $LEGACY_TEMPLATE"
    exit 1
fi

if [ ! -f "$INTEGRATION_TEMPLATE" ]; then
    echo "❌ Integration template file not found: $INTEGRATION_TEMPLATE"
    exit 1
fi

# Copy templates to config files
echo "📋 Creating config files from templates..."
cp "$LEGACY_TEMPLATE" "$LEGACY_CONFIG"
cp "$INTEGRATION_TEMPLATE" "$INTEGRATION_CONFIG"

echo "📋 Please provide your API keys:"
echo ""

# Get Anthropic API key
echo "🤖 Anthropic Claude API Key:"
echo "   Get your key from: https://console.anthropic.com/"
read -p "   Enter your Anthropic API key: " ANTHROPIC_KEY

# Get Google Gemini API key  
echo ""
echo "🔍 Google Gemini API Key:"
echo "   Get your key from: https://aistudio.google.com/app/apikey"
read -p "   Enter your Google Gemini API key: " GEMINI_KEY

echo ""
echo "🔧 Updating configuration files..."

# Update legacy config
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/YOUR_ANTHROPIC_API_KEY_HERE/$ANTHROPIC_KEY/g" "$LEGACY_CONFIG"
    sed -i '' "s/YOUR_GOOGLE_GEMINI_API_KEY_HERE/$GEMINI_KEY/g" "$LEGACY_CONFIG"
    sed -i '' "s/YOUR_ANTHROPIC_API_KEY_HERE/$ANTHROPIC_KEY/g" "$INTEGRATION_CONFIG"
    sed -i '' "s/YOUR_GOOGLE_GEMINI_API_KEY_HERE/$GEMINI_KEY/g" "$INTEGRATION_CONFIG"
else
    # Linux
    sed -i "s/YOUR_ANTHROPIC_API_KEY_HERE/$ANTHROPIC_KEY/g" "$LEGACY_CONFIG"
    sed -i "s/YOUR_GOOGLE_GEMINI_API_KEY_HERE/$GEMINI_KEY/g" "$LEGACY_CONFIG"
    sed -i "s/YOUR_ANTHROPIC_API_KEY_HERE/$ANTHROPIC_KEY/g" "$INTEGRATION_CONFIG"
    sed -i "s/YOUR_GOOGLE_GEMINI_API_KEY_HERE/$GEMINI_KEY/g" "$INTEGRATION_CONFIG"
fi

echo "✅ API keys configured successfully!"
echo ""
echo "🚀 You can now run the TEP simulator:"
echo "   cd legacy"
echo "   python unified_tep_control_panel.py"
echo ""
echo "🌐 Then open: http://localhost:9001"
echo ""
echo "⚠️  SECURITY NOTE: Your API keys are now in the config files."
echo "   Do NOT commit these files to version control!"
echo "   The .gitignore should exclude them from commits."
