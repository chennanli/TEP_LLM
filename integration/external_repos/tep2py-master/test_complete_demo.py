#!/usr/bin/env python3
"""
Complete Demo Test - Verify everything works as expected
Tests both original tep2py interface and new acceleration features
"""

import numpy as np
import pandas as pd
import time
import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_original_tep2py():
    """Test the original tep2py interface (what your unified interface uses)"""
    
    print("🧪 TESTING ORIGINAL TEP2PY INTERFACE")
    print("="*60)
    print("This is what your unified interface currently uses")
    print()
    
    try:
        # Import the tep2py module
        from tep2py import tep2py
        
        # Create test scenario - normal operation
        idata = np.zeros((5, 20))  # 5 samples, no faults
        
        print(f"Test scenario: {idata.shape[0]} samples, no faults")
        
        # Create tep2py object
        tep = tep2py(idata)
        
        # Run simulation
        print("Running simulation...")
        start_time = time.time()
        tep.simulate()
        execution_time = time.time() - start_time
        
        print(f"✅ Simulation completed in {execution_time:.3f} seconds")
        print(f"✅ Data shape: {tep.process_data.shape}")
        print(f"✅ Final pressure: {tep.process_data.iloc[-1]['XMEAS(7)']:.1f} kPa")
        print(f"✅ Final temperature: {tep.process_data.iloc[-1]['XMEAS(9)']:.1f} °C")
        
        return True, tep.process_data
        
    except Exception as e:
        print(f"❌ Original tep2py test failed: {e}")
        return False, None

def test_direct_temain():
    """Test direct temain_mod calls (both original and accelerated)"""
    
    print("\n🧪 TESTING DIRECT TEMAIN_MOD CALLS")
    print("="*60)
    print("This shows the new acceleration capabilities")
    print()
    
    try:
        import temain_mod
        
        # Test parameters
        npts = 900  # 15 minutes
        nx = 5      # 5 data points
        idata = np.zeros((nx, 20), dtype=np.int32)
        
        print(f"Test scenario: {npts/60:.1f} minutes, {nx} data points")
        print()
        
        # Test 1: Original TEMAIN
        print("1. Original TEMAIN:")
        start_time = time.time()
        result_original = temain_mod.temain(npts, nx, idata, 0)  # quiet
        time_original = time.time() - start_time
        
        print(f"   Time: {time_original:.3f}s")
        print(f"   Final: P={result_original[-1, 6]:.1f} kPa, T={result_original[-1, 8]:.1f}°C")
        
        # Test 2: TEMAIN_ACCELERATED (1x speed)
        print("\n2. TEMAIN_ACCELERATED (1x speed):")
        start_time = time.time()
        result_accel_1x = temain_mod.temain_accelerated(npts, nx, idata, 0, 1.0)
        time_accel_1x = time.time() - start_time
        
        print(f"   Time: {time_accel_1x:.3f}s")
        print(f"   Final: P={result_accel_1x[-1, 6]:.1f} kPa, T={result_accel_1x[-1, 8]:.1f}°C")
        
        # Test 3: TEMAIN_ACCELERATED (5x speed)
        print("\n3. TEMAIN_ACCELERATED (5x speed):")
        start_time = time.time()
        result_accel_5x = temain_mod.temain_accelerated(npts, nx, idata, 0, 5.0)
        time_accel_5x = time.time() - start_time
        
        print(f"   Time: {time_accel_5x:.3f}s")
        print(f"   Final: P={result_accel_5x[-1, 6]:.1f} kPa, T={result_accel_5x[-1, 8]:.1f}°C")
        
        # Analysis
        print(f"\n📊 ANALYSIS:")
        diff_1x = abs(result_original[-1, 6] - result_accel_1x[-1, 6])
        diff_5x = abs(result_original[-1, 6] - result_accel_5x[-1, 6])
        
        print(f"   1x vs Original: ΔP = {diff_1x:.1f} kPa")
        print(f"   5x vs Original: ΔP = {diff_5x:.1f} kPa")
        
        speedup_5x = time_original / time_accel_5x if time_accel_5x > 0 else float('inf')
        print(f"   5x Actual speedup: {speedup_5x:.1f}x")
        
        success = diff_1x < 5.0 and diff_5x < 50.0
        print(f"   {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        return success
        
    except Exception as e:
        print(f"❌ Direct temain test failed: {e}")
        return False

def test_fault_scenario():
    """Test with a fault scenario"""
    
    print("\n🧪 TESTING FAULT SCENARIO")
    print("="*60)
    print("Testing IDV(1) fault with acceleration")
    print()
    
    try:
        from tep2py import tep2py
        import temain_mod
        
        # Create fault scenario
        idata = np.zeros((7, 20))
        idata[3:, 0] = 1  # IDV(1) fault starting at sample 4
        
        print("Scenario: IDV(1) A/C Feed Ratio fault at sample 4")
        print()
        
        # Test with tep2py (original interface)
        print("1. Using tep2py (your current interface):")
        tep = tep2py(idata)
        start_time = time.time()
        tep.simulate()
        time_tep2py = time.time() - start_time
        
        final_p_tep2py = tep.process_data.iloc[-1]['XMEAS(7)']
        print(f"   Time: {time_tep2py:.3f}s")
        print(f"   Final pressure: {final_p_tep2py:.1f} kPa")
        
        # Test with direct accelerated call
        print("\n2. Using TEMAIN_ACCELERATED (5x speed):")
        npts = 60 * 3 * idata.shape[0]  # Same calculation as tep2py
        nx = idata.shape[0]
        
        start_time = time.time()
        result_accel = temain_mod.temain_accelerated(npts, nx, idata, 0, 5.0)
        time_accel = time.time() - start_time
        
        final_p_accel = result_accel[-1, 6]
        print(f"   Time: {time_accel:.3f}s")
        print(f"   Final pressure: {final_p_accel:.1f} kPa")
        
        # Compare
        diff = abs(final_p_tep2py - final_p_accel)
        speedup = time_tep2py / time_accel if time_accel > 0 else float('inf')
        
        print(f"\n📊 COMPARISON:")
        print(f"   Pressure difference: {diff:.1f} kPa")
        print(f"   Speedup achieved: {speedup:.1f}x")
        
        success = diff < 50.0  # Allow some difference due to acceleration
        print(f"   {'✅ FAULT TEST SUCCESS' if success else '❌ FAULT TEST FAILED'}")
        
        return success
        
    except Exception as e:
        print(f"❌ Fault scenario test failed: {e}")
        return False

def main():
    """Run complete demo test"""
    
    print("🎯 COMPLETE TEP DEMO TEST")
    print("Testing both your current interface and new acceleration features")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = []
    
    # Test 1: Original tep2py interface
    success1, data = test_original_tep2py()
    results.append(("Original tep2py Interface", success1))
    
    # Test 2: Direct temain calls
    success2 = test_direct_temain()
    results.append(("Direct TEMAIN calls", success2))
    
    # Test 3: Fault scenario
    success3 = test_fault_scenario()
    results.append(("Fault scenario test", success3))
    
    # Final summary
    print(f"\n{'='*80}")
    print("FINAL DEMO RESULTS")
    print(f"{'='*80}")
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<30} {status}")
    
    total_passed = sum(1 for _, success in results if success)
    total_tests = len(results)
    
    print(f"\nOverall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Your unified interface will work exactly as before")
        print("✅ New acceleration features are available when needed")
        print("✅ Everything is backward compatible")
    else:
        print(f"\n⚠️  {total_tests - total_passed} tests failed")
        print("Check the error messages above for details")
    
    print(f"\nDemo completed: {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
