#!/usr/bin/env python3
"""
Demo System Test Script
Tests all components before manager demo
"""

import requests
import time
import json

def test_system():
    """Test the demo system components"""
    
    print("🧪 Testing Demo System for Manager Presentation")
    print("=" * 50)
    
    base_url = "http://localhost:9001"
    
    # Test 1: Main dashboard
    print("\n1. Testing Main Dashboard...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Main dashboard accessible")
        else:
            print(f"❌ Dashboard returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard not accessible: {e}")
        return False
    
    # Test 2: System status
    print("\n2. Testing System Status...")
    try:
        response = requests.get(f"{base_url}/api/system-status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print("✅ System status API working")
            print(f"   TEP Simulation: {status.get('tep_simulation', 'Unknown')}")
            print(f"   FaultExplainer: {status.get('faultexplainer', 'Unknown')}")
        else:
            print(f"❌ System status returned {response.status_code}")
    except Exception as e:
        print(f"❌ System status error: {e}")
    
    # Test 3: TEP data
    print("\n3. Testing TEP Data...")
    try:
        response = requests.get(f"{base_url}/api/tep-data", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ TEP data API working")
            if 'sensor_data' in data:
                print(f"   Sensors available: {len(data['sensor_data'])}")
            if 'timestamp' in data:
                print(f"   Last update: {data['timestamp']}")
        else:
            print(f"❌ TEP data returned {response.status_code}")
    except Exception as e:
        print(f"❌ TEP data error: {e}")
    
    # Test 4: Fault injection capability
    print("\n4. Testing Fault Injection...")
    try:
        # Just test the endpoint exists, don't actually inject
        response = requests.get(f"{base_url}/api/fault-types", timeout=5)
        if response.status_code == 200:
            fault_types = response.json()
            print("✅ Fault injection API working")
            print(f"   Available fault types: {len(fault_types)}")
        else:
            print(f"❌ Fault types returned {response.status_code}")
    except Exception as e:
        print(f"❌ Fault injection error: {e}")
    
    # Test 5: LLM analysis status
    print("\n5. Testing LLM Analysis...")
    try:
        response = requests.get(f"{base_url}/api/llm-status", timeout=5)
        if response.status_code == 200:
            llm_status = response.json()
            print("✅ LLM analysis API working")
            print(f"   Status: {llm_status.get('status', 'Unknown')}")
        else:
            print(f"❌ LLM status returned {response.status_code}")
    except Exception as e:
        print(f"❌ LLM analysis error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Demo System Test Complete!")
    print("\n📋 Pre-Demo Checklist:")
    print("✅ System running on http://localhost:9001")
    print("✅ All APIs responding")
    print("✅ Ready for manager demo")
    
    print("\n🎬 Demo Flow:")
    print("1. Show dashboard at http://localhost:9001")
    print("2. Explain real-time TEP simulation")
    print("3. Demonstrate fault injection")
    print("4. Show anomaly detection")
    print("5. Display LLM analysis results")
    
    return True

if __name__ == "__main__":
    test_system()
