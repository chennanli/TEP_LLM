#!/usr/bin/env python3
"""
Test LLM connection and root cause analysis functionality
"""

import requests
import json
import time

def test_llm_health():
    """Test if FaultExplainer backend is healthy"""
    print("🏥 TESTING FAULTEXPLAINER HEALTH")
    print("="*50)
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ FaultExplainer backend is healthy: {result}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_lmstudio_direct():
    """Test LMStudio directly"""
    print(f"\n🤖 TESTING LMSTUDIO DIRECT CONNECTION")
    print("="*50)
    
    try:
        # Test LMStudio models endpoint
        response = requests.get("http://localhost:1234/v1/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print(f"✅ LMStudio models available: {len(models['data'])}")
            for model in models['data'][:3]:  # Show first 3 models
                print(f"   • {model['id']}")
            
            # Test chat completion
            print(f"\n🧪 Testing chat completion...")
            chat_data = {
                "model": "mistralai_mistral-small-3.1-24b-instruct-2503",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say hello in one sentence."}
                ],
                "max_tokens": 50
            }
            
            response = requests.post("http://localhost:1234/v1/chat/completions", 
                                   json=chat_data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                message = result['choices'][0]['message']['content']
                print(f"✅ LMStudio response: {message}")
                return True
            else:
                print(f"❌ Chat completion failed: {response.status_code}")
                return False
        else:
            print(f"❌ LMStudio models check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ LMStudio test error: {e}")
        return False

def test_faultexplainer_llm():
    """Test FaultExplainer LLM integration"""
    print(f"\n🔧 TESTING FAULTEXPLAINER LLM INTEGRATION")
    print("="*50)
    
    try:
        # Create test data that simulates TEP anomaly
        test_data = {
            "data": {
                "A Feed": [0.25, 0.26, 0.27],  # Slight increase
                "Reactor Pressure": [2706.0, 2710.0, 2715.0],  # Pressure rising
                "Reactor Temperature": [120.4, 120.6, 120.8],  # Temperature rising
                "D Feed": [3665.0, 3665.0, 3665.0],  # Stable
                "E Feed": [4501.0, 4501.0, 4501.0]   # Stable
            },
            "id": "test-001",
            "file": "test_anomaly.csv"
        }
        
        print("📊 Sending test data to /explain endpoint...")
        response = requests.post("http://localhost:8000/explain", 
                               json=test_data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ FaultExplainer analysis successful!")
            print(f"📝 Analysis result: {result[:200]}..." if len(str(result)) > 200 else f"📝 Analysis result: {result}")
            return True
        else:
            print(f"❌ FaultExplainer analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FaultExplainer LLM test error: {e}")
        return False

def main():
    print("LLM CONNECTION AND ROOT CAUSE ANALYSIS TEST")
    print("Testing if LMStudio and FaultExplainer can provide root cause analysis")
    print()
    
    # Test 1: Health check
    health_ok = test_llm_health()
    
    # Test 2: LMStudio direct
    lmstudio_ok = test_lmstudio_direct()
    
    # Test 3: FaultExplainer LLM integration
    faultexplainer_ok = test_faultexplainer_llm()
    
    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    
    print(f"✅ FaultExplainer Health: {'PASS' if health_ok else 'FAIL'}")
    print(f"✅ LMStudio Direct: {'PASS' if lmstudio_ok else 'FAIL'}")
    print(f"✅ FaultExplainer LLM: {'PASS' if faultexplainer_ok else 'FAIL'}")
    
    if health_ok and lmstudio_ok and faultexplainer_ok:
        print(f"\n🎉 ALL TESTS PASSED!")
        print("✅ Your LLM root cause analysis system is working!")
        print()
        print("🚀 What this means:")
        print("• LMStudio is running and responding")
        print("• FaultExplainer backend can connect to LMStudio")
        print("• Root cause analysis should work in your TEP system")
        print()
        print("🎯 Next steps:")
        print("1. Start your TEP simulation")
        print("2. Inject a fault (e.g., IDV_1 = 1)")
        print("3. Wait for anomaly detection")
        print("4. Check 'Show Last 5 Analyses' for LLM diagnosis")
        
    else:
        print(f"\n⚠️  SOME TESTS FAILED")
        print("🔧 Troubleshooting needed:")
        if not health_ok:
            print("• FaultExplainer backend may not be running")
        if not lmstudio_ok:
            print("• LMStudio may not be running or accessible")
        if not faultexplainer_ok:
            print("• Integration between FaultExplainer and LMStudio has issues")
    
    print(f"\nTest completed: {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
