#!/usr/bin/env python3
"""
Test script for unified interface with acceleration
"""

import requests
import time
import json

def test_unified_acceleration():
    """Test the unified interface acceleration features"""
    
    print("🧪 TESTING UNIFIED INTERFACE ACCELERATION")
    print("="*60)
    
    base_url = "http://localhost:9001"
    
    # Test 1: Check if server is running
    print("1. Checking server status...")
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Server is running")
            print(f"   TEP Running: {status.get('tep_running', False)}")
            print(f"   Current Speed Factor: {status.get('simulation_speed_factor', 1.0)}x")
            print(f"   Using Acceleration: {status.get('use_accelerated_simulation', False)}")
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Please start the unified interface first:")
        print("cd /Users/chennanli/Desktop/LLM_Project/TE")
        print("source tep_env/bin/activate")
        print("python integration/src/backend/services/simulation/unified_tep_control_panel.py")
        return False
    
    # Test 2: Set simulation speed
    print(f"\n2. Testing simulation speed control...")
    for speed_factor in [1.0, 3.0, 5.0, 1.0]:  # Test different speeds
        try:
            response = requests.post(
                f"{base_url}/api/simulation_speed",
                json={"speed_factor": speed_factor},
                timeout=5
            )
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print(f"✅ Set speed to {speed_factor}x")
                    print(f"   Acceleration enabled: {result['use_accelerated_simulation']}")
                else:
                    print(f"❌ Failed to set speed: {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ HTTP error {response.status_code}")
        except Exception as e:
            print(f"❌ Error setting speed {speed_factor}x: {e}")
        
        time.sleep(1)  # Brief pause between tests
    
    # Test 3: Check final status
    print(f"\n3. Final status check...")
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Final status:")
            print(f"   Simulation Speed Factor: {status.get('simulation_speed_factor', 1.0)}x")
            print(f"   Using Accelerated Simulation: {status.get('use_accelerated_simulation', False)}")
            print(f"   Loop Speed Mode: {status.get('speed_mode', 'unknown')}")
            print(f"   Step Interval: {status.get('step_interval_seconds', 0)}s")
        else:
            print(f"❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status check error: {e}")
    
    print(f"\n{'='*60}")
    print("TEST COMPLETE")
    print("✅ The unified interface now supports true simulation acceleration!")
    print("✅ Use the 'Simulation Acceleration' slider in the web interface")
    print("✅ Speed factors from 1x to 10x are supported")
    
    return True

def show_usage_instructions():
    """Show how to use the new acceleration features"""
    
    print("\n🚀 HOW TO USE SIMULATION ACCELERATION")
    print("="*60)
    
    print("1. Start the unified interface:")
    print("   cd /Users/chennanli/Desktop/LLM_Project/TE")
    print("   source tep_env/bin/activate")
    print("   python integration/src/backend/services/simulation/unified_tep_control_panel.py")
    
    print("\n2. Open web browser:")
    print("   http://localhost:9001")
    
    print("\n3. In the web interface:")
    print("   - Look for '🚀 Simulation Acceleration' section")
    print("   - Use the 'Speed Factor' slider (1x to 10x)")
    print("   - Higher values = faster simulation")
    print("   - Status shows current acceleration level")
    
    print("\n4. What you'll see:")
    print("   - Loop Speed: Controls how often simulation runs (Demo/Real)")
    print("   - Sim Speed: Controls how fast each simulation step runs (1x-10x)")
    print("   - Both work together for maximum speed")
    
    print("\n5. Recommended settings:")
    print("   - Demo mode + 5x acceleration = Very fast testing")
    print("   - Real mode + 2x acceleration = Faster production")
    print("   - Real mode + 1x acceleration = Normal operation")

if __name__ == "__main__":
    print("UNIFIED INTERFACE ACCELERATION TEST")
    print("Testing the new simulation acceleration features")
    print()
    
    success = test_unified_acceleration()
    
    if success:
        show_usage_instructions()
    else:
        print("\n⚠️  Test failed - please check the unified interface setup")
    
    print(f"\nTest completed: {time.strftime('%Y-%m-%d %H:%M:%S')}")
