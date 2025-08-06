#!/usr/bin/env python3
"""
Test MVP Dashboard
==================

Quick test to verify the MVP dashboard is working correctly.
"""

import requests
import time
import json

def test_dashboard_endpoints():
    """Test all dashboard endpoints."""
    base_url = "http://localhost:8080"
    
    print("🧪 Testing MVP Dashboard Endpoints")
    print("=" * 50)
    
    # Test 1: Check if dashboard is running
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard is running and accessible")
        else:
            print(f"❌ Dashboard returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to dashboard: {e}")
        return False
    
    # Test 2: Start simulation
    try:
        response = requests.post(f"{base_url}/start_simulation", timeout=10)
        result = response.json()
        if result.get('success'):
            print("✅ Simulation started successfully")
        else:
            print(f"❌ Failed to start simulation: {result.get('message')}")
    except Exception as e:
        print(f"❌ Error starting simulation: {e}")
    
    # Test 3: Adjust A/C ratio
    try:
        response = requests.post(
            f"{base_url}/adjust_ratio",
            json={"ratio": 1.5},
            timeout=5
        )
        result = response.json()
        if result.get('success'):
            print("✅ A/C ratio adjustment successful")
        else:
            print(f"❌ Failed to adjust ratio: {result.get('message')}")
    except Exception as e:
        print(f"❌ Error adjusting ratio: {e}")
    
    # Test 4: Inject fault
    try:
        response = requests.post(
            f"{base_url}/inject_fault",
            json={"fault_type": 1, "intensity": 1.0},
            timeout=5
        )
        result = response.json()
        if result.get('success'):
            print("✅ Fault injection successful")
        else:
            print(f"❌ Failed to inject fault: {result.get('message')}")
    except Exception as e:
        print(f"❌ Error injecting fault: {e}")
    
    # Test 5: Check status
    try:
        response = requests.get(f"{base_url}/get_status", timeout=5)
        status = response.json()
        print(f"✅ Status check successful:")
        print(f"   • Running: {status.get('running')}")
        print(f"   • Fault: {status.get('fault')}")
        print(f"   • A/C Ratio: {status.get('ac_ratio')}")
        print(f"   • Data Points: {status.get('data_points')}")
        print(f"   • Anomaly Score: {status.get('anomaly_score'):.2f}")
    except Exception as e:
        print(f"❌ Error checking status: {e}")
    
    # Wait a bit for data collection
    print("\n⏳ Waiting 10 seconds for data collection...")
    time.sleep(10)
    
    # Test 6: Check status again
    try:
        response = requests.get(f"{base_url}/get_status", timeout=5)
        status = response.json()
        print(f"✅ Updated status:")
        print(f"   • Data Points: {status.get('data_points')}")
        print(f"   • Anomaly Score: {status.get('anomaly_score'):.2f}")
        if status.get('last_explanation'):
            print(f"   • Last Explanation: {status.get('last_explanation')[:100]}...")
    except Exception as e:
        print(f"❌ Error checking updated status: {e}")
    
    # Test 7: Stop simulation
    try:
        response = requests.post(f"{base_url}/stop_simulation", timeout=5)
        result = response.json()
        if result.get('success'):
            print("✅ Simulation stopped successfully")
        else:
            print(f"❌ Failed to stop simulation: {result.get('message')}")
    except Exception as e:
        print(f"❌ Error stopping simulation: {e}")
    
    print("\n🎯 MVP Dashboard Test Complete!")
    return True

def main():
    """Main test function."""
    print("🚀 MVP Dashboard Test Suite")
    print("=" * 50)
    print("Make sure the dashboard is running on http://localhost:8080")
    print("Start it with: python mvp_dashboard.py")
    print()
    
    # Wait for user confirmation
    input("Press Enter when dashboard is running...")
    
    # Run tests
    success = test_dashboard_endpoints()
    
    if success:
        print("\n✅ All tests completed!")
        print("\n🎛️ Next Steps:")
        print("1. Open http://localhost:8080 in your browser")
        print("2. Click 'Start Simulation'")
        print("3. Adjust A/C ratio slider")
        print("4. Inject faults and watch for anomalies")
        print("5. See LLM explanations when anomalies are detected")
    else:
        print("\n❌ Some tests failed. Check the dashboard logs.")

if __name__ == '__main__':
    main()
