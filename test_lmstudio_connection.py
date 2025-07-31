#!/usr/bin/env python3
"""
Test LMStudio Connection
========================

Simple test to verify your LMStudio is working with the TEP system.
"""

import requests
import json

def test_lmstudio_connection():
    """Test connection to your LMStudio instance."""
    print("🔍 Testing LMStudio Connection...")
    
    try:
        # Test the exact URL from your screenshot
        url = "http://127.0.0.1:1234/v1/chat/completions"
        
        # Simple test message
        payload = {
            "model": "mistralai_mistral-small-3.1-24b-instruct-2503",
            "messages": [
                {
                    "role": "user", 
                    "content": "Hello! Can you help me analyze industrial process data?"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer lm-studio"
        }
        
        print("📤 Sending test request to LMStudio...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            print("✅ LMStudio connection successful!")
            print(f"🤖 LMStudio response: {message}")
            return True
        else:
            print(f"❌ LMStudio returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to LMStudio")
        print("   Make sure LMStudio is running on http://127.0.0.1:1234")
        return False
    except Exception as e:
        print(f"❌ Error testing LMStudio: {e}")
        return False

def test_tep_simulator():
    """Test TEP simulator."""
    print("\n🔍 Testing TEP Simulator...")
    try:
        import sys
        sys.path.append('external_repos/tep2py-master')
        from tep2py import tep2py
        print("✅ TEP simulator loaded successfully!")
        return True
    except Exception as e:
        print(f"❌ TEP simulator error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 LMStudio + TEP Integration Test")
    print("=" * 40)
    
    # Test TEP
    tep_ok = test_tep_simulator()
    
    # Test LMStudio
    lm_ok = test_lmstudio_connection()
    
    print("\n" + "=" * 40)
    print("🎯 TEST RESULTS")
    print("=" * 40)
    print(f"TEP Simulator: {'✅ PASS' if tep_ok else '❌ FAIL'}")
    print(f"LMStudio: {'✅ PASS' if lm_ok else '❌ FAIL'}")
    
    if tep_ok and lm_ok:
        print("\n🎉 Both components working!")
        print("Next step: Start FaultExplainer backend")
        print("Run: cd external_repos/FaultExplainer-MultiLLM/backend && python app.py")
    else:
        print("\n⚠️  Some components failed - check errors above")
