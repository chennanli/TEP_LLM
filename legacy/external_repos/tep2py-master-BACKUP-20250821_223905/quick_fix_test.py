#!/usr/bin/env python3
"""
Quick test to verify the fault timing fix
"""

import numpy as np
import temain_mod
import time

def test_fault_timing_fix():
    """Test that 1x speed now matches original exactly"""
    
    print("🔧 TESTING FAULT TIMING FIX")
    print("="*50)
    
    # Test IDV(1) fault scenario
    npts = 1200  # 20 minutes
    nx = 7       # 7 data points
    
    # Create fault pattern: normal for first 3 points, then IDV(1) fault
    idata = np.zeros((nx, 20), dtype=np.int32)
    idata[3:, 0] = 1  # IDV(1) fault starting at point 4 (12 minutes)
    
    print(f"Test scenario: IDV(1) fault at 12 minutes")
    print(f"Duration: {npts/60:.1f} minutes, {nx} data points")
    print()
    
    # Test original TEMAIN
    print("Running Original TEMAIN...")
    start_time = time.time()
    result_original = temain_mod.temain(npts, nx, idata, 0)
    time_original = time.time() - start_time
    
    print(f"✅ Original: {time_original:.3f}s")
    print(f"   Final: P={result_original[-1, 6]:.1f} kPa, T={result_original[-1, 8]:.1f}°C")
    
    # Test TEMAIN_ACCELERATED (1x speed)
    print("\nRunning TEMAIN_ACCELERATED (1x speed)...")
    start_time = time.time()
    result_accel_1x = temain_mod.temain_accelerated(npts, nx, idata, 0, 1.0)
    time_accel_1x = time.time() - start_time
    
    print(f"✅ Accelerated (1x): {time_accel_1x:.3f}s")
    print(f"   Final: P={result_accel_1x[-1, 6]:.1f} kPa, T={result_accel_1x[-1, 8]:.1f}°C")
    
    # Test TEMAIN_ACCELERATED (5x speed)
    print("\nRunning TEMAIN_ACCELERATED (5x speed)...")
    start_time = time.time()
    result_accel_5x = temain_mod.temain_accelerated(npts, nx, idata, 0, 5.0)
    time_accel_5x = time.time() - start_time
    
    print(f"✅ Accelerated (5x): {time_accel_5x:.3f}s")
    print(f"   Final: P={result_accel_5x[-1, 6]:.1f} kPa, T={result_accel_5x[-1, 8]:.1f}°C")
    
    # Analysis
    print(f"\n{'='*50}")
    print("ANALYSIS")
    print(f"{'='*50}")
    
    # Calculate differences
    diff_1x_p = abs(result_original[-1, 6] - result_accel_1x[-1, 6])
    diff_1x_t = abs(result_original[-1, 8] - result_accel_1x[-1, 8])
    diff_5x_p = abs(result_original[-1, 6] - result_accel_5x[-1, 6])
    diff_5x_t = abs(result_original[-1, 8] - result_accel_5x[-1, 8])
    
    print(f"Differences from Original:")
    print(f"  1x speed: ΔP={diff_1x_p:.1f} kPa, ΔT={diff_1x_t:.1f}°C")
    print(f"  5x speed: ΔP={diff_5x_p:.1f} kPa, ΔT={diff_5x_t:.1f}°C")
    
    # Success criteria
    identical_1x = diff_1x_p < 1.0 and diff_1x_t < 0.1
    acceptable_5x = diff_5x_p < 20.0 and diff_5x_t < 2.0
    
    print(f"\nSuccess Criteria:")
    print(f"  1x identical to original: {'✅' if identical_1x else '❌'} (ΔP<1.0, ΔT<0.1)")
    print(f"  5x acceptable difference: {'✅' if acceptable_5x else '❌'} (ΔP<20.0, ΔT<2.0)")
    
    overall_success = identical_1x and acceptable_5x
    print(f"\n{'✅ FIX SUCCESSFUL' if overall_success else '❌ FIX FAILED'}")
    
    return overall_success

if __name__ == "__main__":
    success = test_fault_timing_fix()
    
    if success:
        print("\n🎉 The fault timing fix is working!")
        print("TEMAIN_ACCELERATED now properly matches original TEMAIN")
        print("Ready for comprehensive re-evaluation!")
    else:
        print("\n⚠️  Fix needs more work")
        print("Check fault timing logic in TEMAIN_ACCELERATED")
