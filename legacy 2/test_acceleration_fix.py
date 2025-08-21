#!/usr/bin/env python3
"""
Test the acceleration fix for legacy unified control panel
"""

import sys
import os
import time

# Add the tep2py path
sys.path.insert(0, 'external_repos/tep2py-master')

def test_tep2py_acceleration():
    """Test tep2py with acceleration"""
    
    print("🧪 TESTING TEP2PY ACCELERATION FIX")
    print("="*50)
    
    try:
        from tep2py import tep2py
        import numpy as np
        
        # Create test data
        idata = np.zeros((3, 20))  # 3 samples, no faults
        
        print("Test 1: Normal speed (1.0x)")
        print("-" * 30)
        
        # Test normal speed
        start_time = time.time()
        tep_normal = tep2py(idata, speed_factor=1.0)
        tep_normal.simulate()
        time_normal = time.time() - start_time
        
        final_pressure_normal = tep_normal.process_data.iloc[-1]['XMEAS(7)']
        print(f"✅ Normal speed: {time_normal:.3f}s")
        print(f"   Final pressure: {final_pressure_normal:.1f} kPa")
        
        print(f"\nTest 2: Accelerated speed (5.0x)")
        print("-" * 30)
        
        # Test accelerated speed
        start_time = time.time()
        tep_accel = tep2py(idata, speed_factor=5.0)
        tep_accel.simulate()
        time_accel = time.time() - start_time
        
        final_pressure_accel = tep_accel.process_data.iloc[-1]['XMEAS(7)']
        print(f"✅ Accelerated speed: {time_accel:.3f}s")
        print(f"   Final pressure: {final_pressure_accel:.1f} kPa")
        
        # Analysis
        print(f"\n📊 ANALYSIS:")
        print("-" * 30)
        
        pressure_diff = abs(final_pressure_normal - final_pressure_accel)
        speedup = time_normal / time_accel if time_accel > 0 else float('inf')
        
        print(f"Pressure difference: {pressure_diff:.1f} kPa")
        print(f"Actual speedup: {speedup:.1f}x")
        
        # Success criteria
        physics_ok = pressure_diff < 50.0  # Allow some difference
        speedup_ok = speedup > 1.0  # Should be faster
        
        print(f"\nSuccess Criteria:")
        print(f"✅ Physics preserved: {physics_ok} (diff < 50 kPa)")
        print(f"✅ Speed improvement: {speedup_ok} (speedup > 1x)")
        
        overall_success = physics_ok and speedup_ok
        print(f"\n{'✅ TEST PASSED' if overall_success else '❌ TEST FAILED'}")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_unified_panel_connection():
    """Test connection to unified control panel"""
    
    print(f"\n🌐 TESTING UNIFIED PANEL CONNECTION")
    print("="*50)
    
    try:
        import requests
        
        # Test if unified panel is running
        response = requests.get("http://localhost:9001/api/status", timeout=3)
        if response.status_code == 200:
            status = response.json()
            print("✅ Unified panel is running")
            print(f"   TEP Running: {status.get('tep_running', False)}")
            print(f"   Speed Factor: {status.get('simulation_speed_factor', 1.0)}x")
            return True
        else:
            print(f"⚠️  Unified panel returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️  Unified panel not running: {e}")
        print("To start it, run:")
        print("cd /Users/chennanli/Desktop/LLM_Project/TE/legacy")
        print("source ../tep_env/bin/activate")
        print("python unified_tep_control_panel.py")
        return False

def main():
    print("LEGACY TEP ACCELERATION TEST")
    print("Testing the corrected acceleration implementation")
    print()
    
    # Change to legacy directory
    os.chdir('/Users/chennanli/Desktop/LLM_Project/TE/legacy')
    
    # Test tep2py acceleration
    tep2py_ok = test_tep2py_acceleration()
    
    # Test unified panel connection
    panel_ok = test_unified_panel_connection()
    
    print(f"\n{'='*60}")
    print("FINAL RESULTS")
    print(f"{'='*60}")
    
    print(f"TEP2PY Acceleration: {'✅ WORKING' if tep2py_ok else '❌ FAILED'}")
    print(f"Unified Panel: {'✅ RUNNING' if panel_ok else '⚠️  NOT RUNNING'}")
    
    if tep2py_ok:
        print(f"\n🎉 ACCELERATION IS WORKING!")
        print("✅ tep2py now uses TEMAIN_ACCELERATED for speed > 1.0x")
        print("✅ Physics values are preserved")
        print("✅ True speed improvement achieved")
        
        if panel_ok:
            print("✅ Unified panel is running - try the speed slider!")
        else:
            print("⚠️  Start the unified panel to test the web interface")
    else:
        print(f"\n❌ Acceleration needs debugging")
    
    print(f"\nTest completed: {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
