#!/usr/bin/env python3
"""
Test script to verify Gemini API key functionality
"""

import requests
import json

def test_gemini_api(api_key):
    """Test if Gemini API key is working"""
    
    print(f"🧪 Testing Gemini API key: {api_key[:20]}...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Hello, this is a test message. Please respond with: API key is working correctly."
                    }
                ]
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("📡 Sending request to Gemini API...")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                text = result['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ API key is working!")
                print(f"📝 Response: {text}")
                return True
            else:
                print(f"❌ Unexpected response format: {result}")
                return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"📝 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

if __name__ == "__main__":
    # Test the new API key
    new_api_key = "AIzaSyDsspV6O8-ZU8vJjEXGSDFfvscu-rpkks8"
    
    print("🔑 Testing new Gemini API key...")
    print("=" * 50)
    
    success = test_gemini_api(new_api_key)
    
    if success:
        print("\n🎉 New API key is working! You can use it in your TEP system.")
    else:
        print("\n❌ New API key is not working. You may need to:")
        print("   1. Check if the key is valid")
        print("   2. Ensure Gemini API is enabled in Google Cloud")
        print("   3. Check if there are usage limits or billing issues")
