#!/bin/bash

# LMStudio Quick Health Check and Recovery Script
# Usage: ./lmstudio_quick_check.sh [--fix]

echo "🔍 LMStudio Quick Health Check"
echo "================================"

# Check if LMStudio is responding
echo "📡 Testing LMStudio connection..."
response=$(curl -s -w "%{http_code}" -o /tmp/lmstudio_test.json http://localhost:1234/v1/models 2>/dev/null)
http_code="${response: -3}"

if [ "$http_code" = "200" ]; then
    models_count=$(cat /tmp/lmstudio_test.json | grep -o '"id"' | wc -l)
    echo "✅ LMStudio is responding (HTTP $http_code)"
    echo "📊 Models available: $models_count"
    
    # Quick chat test
    echo "🤖 Testing chat completion..."
    chat_response=$(curl -s -w "%{http_code}" -X POST http://localhost:1234/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d '{"model": "mistralai_mistral-small-3.1-24b-instruct-2503", "messages": [{"role": "user", "content": "Say OK"}], "max_tokens": 5}' \
        -o /tmp/lmstudio_chat.json 2>/dev/null)
    
    chat_code="${chat_response: -3}"
    if [ "$chat_code" = "200" ]; then
        echo "✅ Chat completion working"
        echo "🎉 LMStudio is HEALTHY"
    else
        echo "❌ Chat completion failed (HTTP $chat_code)"
        echo "⚠️  LMStudio connection OK but chat not working"
    fi
else
    echo "❌ LMStudio not responding (HTTP $http_code)"
    echo "🔧 LMStudio appears to be DOWN"
    
    if [ "$1" = "--fix" ]; then
        echo ""
        echo "🛠️  Attempting to help with recovery..."
        echo "1. Checking if LMStudio process is running..."
        
        # Check if LMStudio is running
        lmstudio_process=$(ps aux | grep -i lmstudio | grep -v grep)
        if [ -n "$lmstudio_process" ]; then
            echo "   ✅ LMStudio process found"
            echo "   🔄 Try restarting the server in LMStudio"
        else
            echo "   ❌ LMStudio process not found"
            echo "   🚀 Please start LMStudio application"
        fi
        
        echo ""
        echo "📋 Manual Recovery Steps:"
        echo "   1. Open LMStudio application"
        echo "   2. Go to 'Server' tab"
        echo "   3. Select model: mistralai_mistral-small-3.1-24b-instruct-2503"
        echo "   4. Click 'Start Server'"
        echo "   5. Ensure server runs on localhost:1234"
        echo ""
        echo "🔄 Run this script again to verify: ./lmstudio_quick_check.sh"
    else
        echo ""
        echo "💡 Run with --fix flag for recovery suggestions:"
        echo "   ./lmstudio_quick_check.sh --fix"
    fi
fi

# Cleanup
rm -f /tmp/lmstudio_test.json /tmp/lmstudio_chat.json

echo ""
echo "🌐 Backend health check: curl http://localhost:8000/health/lmstudio"
echo "🔧 Full diagnostic: python lmstudio_health_check.py"
