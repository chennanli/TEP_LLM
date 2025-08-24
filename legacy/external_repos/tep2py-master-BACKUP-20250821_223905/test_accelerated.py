#!/usr/bin/env python3
"""
Test script for TEMAIN_ACCELERATED function
Tests the new accelerated TEP simulation implementation
"""

import numpy as np
import temain_mod
import time

def test_temain_accelerated():
    """Test the TEMAIN_ACCELERATED function with different speed factors"""
    
    print("=" * 60)
    print("TESTING TEMAIN_ACCELERATED FUNCTION")
    print("=" * 60)
    
    # Test parameters
    npts = 540  # 9 minutes of simulation (540 seconds)
    nx = 3      # 3 output points (every 3 minutes)
    
    # No faults - all zeros
    idata = np.zeros((nx, 20), dtype=np.int32)
    
    print(f"Test parameters:")
    print(f"  NPTS = {npts} (simulation seconds)")
    print(f"  NX = {nx} (output points)")
    print(f"  IDATA = all zeros (no faults)")
    print()
    
    # Test 1: Baseline (SPEED_FACTOR = 1.0)
    print("TEST 1: Baseline (SPEED_FACTOR = 1.0)")
    print("-" * 40)
    
    start_time = time.time()
    result_baseline = temain_mod.temain_accelerated(npts, nx, idata, 0, 1.0)
    baseline_time = time.time() - start_time
    
    print(f"Execution time: {baseline_time:.2f} seconds")
    print(f"Final values:")
    print(f"  Reactor Pressure (XMEAS[7]): {result_baseline[-1, 6]:.1f} kPa")
    print(f"  Reactor Temperature (XMEAS[9]): {result_baseline[-1, 8]:.1f} °C")
    print(f"  A Feed (XMEAS[1]): {result_baseline[-1, 0]:.3f}")
    print(f"  D Feed (XMEAS[4]): {result_baseline[-1, 3]:.1f}")
    print()
    
    # Test 2: 5x Speed (SPEED_FACTOR = 5.0)
    print("TEST 2: 5x Acceleration (SPEED_FACTOR = 5.0)")
    print("-" * 40)
    
    start_time = time.time()
    result_5x = temain_mod.temain_accelerated(npts, nx, idata, 0, 5.0)
    speed_5x_time = time.time() - start_time
    
    print(f"Execution time: {speed_5x_time:.2f} seconds")
    print(f"Final values:")
    print(f"  Reactor Pressure (XMEAS[7]): {result_5x[-1, 6]:.1f} kPa")
    print(f"  Reactor Temperature (XMEAS[9]): {result_5x[-1, 8]:.1f} °C")
    print(f"  A Feed (XMEAS[1]): {result_5x[-1, 0]:.3f}")
    print(f"  D Feed (XMEAS[4]): {result_5x[-1, 3]:.1f}")
    print()
    
    # Test 3: 10x Speed (SPEED_FACTOR = 10.0)
    print("TEST 3: 10x Acceleration (SPEED_FACTOR = 10.0)")
    print("-" * 40)
    
    start_time = time.time()
    result_10x = temain_mod.temain_accelerated(npts, nx, idata, 0, 10.0)
    speed_10x_time = time.time() - start_time
    
    print(f"Execution time: {speed_10x_time:.2f} seconds")
    print(f"Final values:")
    print(f"  Reactor Pressure (XMEAS[7]): {result_10x[-1, 6]:.1f} kPa")
    print(f"  Reactor Temperature (XMEAS[9]): {result_10x[-1, 8]:.1f} °C")
    print(f"  A Feed (XMEAS[1]): {result_10x[-1, 0]:.3f}")
    print(f"  D Feed (XMEAS[4]): {result_10x[-1, 3]:.1f}")
    print()
    
    # Analysis
    print("ANALYSIS")
    print("-" * 40)
    
    # Check if values are consistent (should be similar for all speed factors)
    pressure_diff_5x = abs(result_baseline[-1, 6] - result_5x[-1, 6])
    pressure_diff_10x = abs(result_baseline[-1, 6] - result_10x[-1, 6])
    temp_diff_5x = abs(result_baseline[-1, 8] - result_5x[-1, 8])
    temp_diff_10x = abs(result_baseline[-1, 8] - result_10x[-1, 8])
    
    print(f"Value consistency check:")
    print(f"  Pressure difference (1x vs 5x): {pressure_diff_5x:.1f} kPa")
    print(f"  Pressure difference (1x vs 10x): {pressure_diff_10x:.1f} kPa")
    print(f"  Temperature difference (1x vs 5x): {temp_diff_5x:.1f} °C")
    print(f"  Temperature difference (1x vs 10x): {temp_diff_10x:.1f} °C")
    print()
    
    # Speed analysis
    if baseline_time > 0:
        speedup_5x = baseline_time / speed_5x_time if speed_5x_time > 0 else float('inf')
        speedup_10x = baseline_time / speed_10x_time if speed_10x_time > 0 else float('inf')
        
        print(f"Performance analysis:")
        print(f"  Baseline time: {baseline_time:.2f} seconds")
        print(f"  5x speed time: {speed_5x_time:.2f} seconds (speedup: {speedup_5x:.1f}x)")
        print(f"  10x speed time: {speed_10x_time:.2f} seconds (speedup: {speedup_10x:.1f}x)")
        print()
    
    # Success criteria
    print("SUCCESS CRITERIA")
    print("-" * 40)
    
    # Expected values from handoff document
    expected_pressure = 2700  # ~2700 kPa
    expected_temp = 120       # ~120°C
    
    pressure_ok = abs(result_baseline[-1, 6] - expected_pressure) < 100  # Within 100 kPa
    temp_ok = abs(result_baseline[-1, 8] - expected_temp) < 10           # Within 10°C
    consistency_ok = pressure_diff_5x < 50 and pressure_diff_10x < 50    # Values consistent
    
    print(f"✓ Pressure in expected range (~2700 kPa): {pressure_ok}")
    print(f"✓ Temperature in expected range (~120°C): {temp_ok}")
    print(f"✓ Values consistent across speed factors: {consistency_ok}")
    
    overall_success = pressure_ok and temp_ok and consistency_ok
    print(f"\n{'✓ OVERALL SUCCESS' if overall_success else '✗ TESTS FAILED'}")
    
    return overall_success

def compare_with_original():
    """Compare TEMAIN_ACCELERATED with original TEMAIN"""
    
    print("\n" + "=" * 60)
    print("COMPARING WITH ORIGINAL TEMAIN")
    print("=" * 60)
    
    # Test parameters
    npts = 540
    nx = 3
    idata = np.zeros((nx, 20), dtype=np.int32)
    
    # Run original TEMAIN
    print("Running original TEMAIN...")
    start_time = time.time()
    result_original = temain_mod.temain(npts, nx, idata, 0)
    original_time = time.time() - start_time
    
    # Run TEMAIN_ACCELERATED with speed factor 1.0
    print("Running TEMAIN_ACCELERATED (speed=1.0)...")
    start_time = time.time()
    result_accelerated = temain_mod.temain_accelerated(npts, nx, idata, 0, 1.0)
    accelerated_time = time.time() - start_time
    
    print(f"\nComparison Results:")
    print(f"Original TEMAIN:")
    print(f"  Time: {original_time:.2f} seconds")
    print(f"  Pressure: {result_original[-1, 6]:.1f} kPa")
    print(f"  Temperature: {result_original[-1, 8]:.1f} °C")
    
    print(f"TEMAIN_ACCELERATED (1.0x):")
    print(f"  Time: {accelerated_time:.2f} seconds")
    print(f"  Pressure: {result_accelerated[-1, 6]:.1f} kPa")
    print(f"  Temperature: {result_accelerated[-1, 8]:.1f} °C")
    
    # Check differences
    pressure_diff = abs(result_original[-1, 6] - result_accelerated[-1, 6])
    temp_diff = abs(result_original[-1, 8] - result_accelerated[-1, 8])
    
    print(f"\nDifferences:")
    print(f"  Pressure difference: {pressure_diff:.1f} kPa")
    print(f"  Temperature difference: {temp_diff:.1f} °C")
    
    # Success criteria for identical results
    identical = pressure_diff < 1.0 and temp_diff < 1.0
    print(f"\n{'✓ IDENTICAL RESULTS' if identical else '✗ RESULTS DIFFER'}")
    
    return identical

if __name__ == "__main__":
    print("TEP ACCELERATED SIMULATION TEST")
    print("Testing the new TEMAIN_ACCELERATED function")
    print()
    
    try:
        # Test the accelerated function
        success1 = test_temain_accelerated()
        
        # Compare with original
        success2 = compare_with_original()
        
        print("\n" + "=" * 60)
        print("FINAL RESULTS")
        print("=" * 60)
        print(f"Accelerated function test: {'PASS' if success1 else 'FAIL'}")
        print(f"Original comparison test: {'PASS' if success2 else 'FAIL'}")
        print(f"Overall result: {'SUCCESS' if success1 and success2 else 'FAILURE'}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
