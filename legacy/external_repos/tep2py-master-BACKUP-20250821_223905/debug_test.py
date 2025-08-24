#!/usr/bin/env python3
"""
Debug test to check what's happening
"""

import numpy as np
import temain_mod

def debug_test():
    """Simple debug test"""
    
    print("🔍 DEBUG TEST")
    print("="*30)
    
    # Very simple test - normal operation
    npts = 540  # 9 minutes
    nx = 3      # 3 data points
    idata = np.zeros((nx, 20), dtype=np.int32)  # No faults
    
    print(f"Simple test: {npts} seconds, {nx} points, no faults")
    
    # Test original
    print("\nOriginal TEMAIN:")
    result_orig = temain_mod.temain(npts, nx, idata, 1)  # verbose
    print(f"Shape: {result_orig.shape}")
    print(f"Final values: P={result_orig[-1, 6]:.1f}, T={result_orig[-1, 8]:.1f}")
    print(f"All pressure values: {result_orig[:, 6]}")
    
    # Test accelerated 1x
    print(f"\nTEMAIN_ACCELERATED (1x):")
    result_accel = temain_mod.temain_accelerated(npts, nx, idata, 1, 1.0)  # verbose
    print(f"Shape: {result_accel.shape}")
    print(f"Final values: P={result_accel[-1, 6]:.1f}, T={result_accel[-1, 8]:.1f}")
    print(f"All pressure values: {result_accel[:, 6]}")

if __name__ == "__main__":
    debug_test()
