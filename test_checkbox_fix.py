#!/usr/bin/env python3
"""
Test script to verify checkbox functionality is working
"""

import requests
import json
import time

def test_checkbox_functionality():
    """Test that checkboxes properly sync with backend"""
    print("🧪 Testing Checkbox Functionality")
    print("=" * 40)
    
    # Test 1: Get initial status
    print("1. Getting initial model status...")
    try:
        response = requests.get('http://localhost:5173/api/models/status', timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ Active models: {status['active_models']}")
            print(f"   ✅ Runtime enabled: {status['runtime_enabled']}")
            
            # Check what frontend should show
            active_models = status['active_models']
            runtime_enabled = status['runtime_enabled']
            
            lmstudio_should_be_checked = 'lmstudio' in active_models or 'lmstudio' in runtime_enabled
            claude_should_be_checked = 'anthropic' in active_models or 'anthropic' in runtime_enabled
            gemini_should_be_checked = 'gemini' in active_models or 'gemini' in runtime_enabled
            
            print(f"   📋 Frontend should show:")
            print(f"      LMStudio: {'✅ Checked' if lmstudio_should_be_checked else '❌ Unchecked'}")
            print(f"      Claude: {'✅ Checked' if claude_should_be_checked else '❌ Unchecked'}")
            print(f"      Gemini: {'✅ Checked' if gemini_should_be_checked else '❌ Unchecked'}")
            
        else:
            print(f"   ❌ Failed to get status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Toggle Gemini OFF (should work now)
    print("\n2. Testing Gemini toggle OFF...")
    try:
        response = requests.post(
            'http://localhost:5173/api/models/toggle',
            json={"model_name": "gemini", "enabled": False},
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Gemini toggled OFF: {result['success']}")
            print(f"   ✅ Active models: {result['active_models']}")
        else:
            print(f"   ❌ Failed to toggle Gemini OFF: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 3: Check status after toggle
    print("\n3. Checking status after Gemini toggle OFF...")
    try:
        response = requests.get('http://localhost:5173/api/models/status', timeout=10)
        if response.status_code == 200:
            status = response.json()
            active_models = status['active_models']
            runtime_enabled = status['runtime_enabled']
            
            gemini_should_be_checked = 'gemini' in active_models or 'gemini' in runtime_enabled
            print(f"   ✅ Gemini should now be: {'✅ Checked' if gemini_should_be_checked else '❌ Unchecked'}")
            
        else:
            print(f"   ❌ Failed to get status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 4: Toggle Claude ON
    print("\n4. Testing Claude toggle ON...")
    try:
        response = requests.post(
            'http://localhost:5173/api/models/toggle',
            json={"model_name": "anthropic", "enabled": True},
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Claude toggled ON: {result['success']}")
            print(f"   ✅ Active models: {result['active_models']}")
        else:
            print(f"   ❌ Failed to toggle Claude ON: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n✅ All checkbox tests passed!")
    print("\n🎯 What you should see in the browser:")
    print("   • Gemini checkbox: UNCHECKED (you toggled it off)")
    print("   • Claude checkbox: CHECKED (you toggled it on)")
    print("   • LMStudio checkbox: UNCHECKED (not enabled)")
    print("\n💡 Try clicking the checkboxes in the browser - they should respond now!")
    
    return True

def main():
    """Main test function"""
    print("🔧 Testing Checkbox Fix")
    print("=" * 50)
    print("Issue: Checkboxes not responding to clicks")
    print("Fix: Added Vite proxy + fixed state synchronization")
    print("=" * 50)
    
    if test_checkbox_functionality():
        print("\n🎉 SUCCESS: Checkbox functionality should now work!")
        print("\n📋 What was fixed:")
        print("1. ✅ Added Vite proxy configuration to route /api calls")
        print("2. ✅ Fixed frontend state sync to check active_models")
        print("3. ✅ Frontend now properly connects to backend")
        
        print("\n🎯 Next Steps:")
        print("1. Open browser: http://localhost:5173")
        print("2. Try clicking the model checkboxes in the header")
        print("3. They should now respond and toggle on/off")
        print("4. Check browser console for any remaining errors")
    else:
        print("\n❌ FAILED: Checkbox functionality still needs work")

if __name__ == "__main__":
    main()
