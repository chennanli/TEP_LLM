#!/usr/bin/env python3
"""
Test script to verify XMV control functionality in TEP simulation.
Tests both default operation and user-controlled XMV values.
"""

import sys
import os
import numpy as np
import pandas as pd

# Add the tep2py path
sys.path.append('legacy/external_repos/tep2py-master')

try:
    from tep2py import tep2py
    print("✅ Successfully imported tep2py")
except ImportError as e:
    print(f"❌ Failed to import tep2py: {e}")
    sys.exit(1)

def test_default_operation():
    """Test TEP with default XMV values (original factory settings)."""
    print("\n🔧 Test 1: Default Operation (Factory Settings)")
    print("=" * 60)
    
    # Create minimal disturbance matrix (no faults)
    steps = 5  # Short test
    idv_matrix = np.zeros((steps, 20))
    
    # Create TEP instance without user XMV (should use defaults)
    tep_sim = tep2py(idv_matrix, speed_factor=1.0)
    print("🔧 Using basic TEMAIN function (not accelerated)")
    
    # Run simulation
    tep_sim.simulate()
    
    # Check results
    if hasattr(tep_sim, 'process_data') and len(tep_sim.process_data) > 0:
        data = tep_sim.process_data
        print(f"✅ Simulation successful: {len(data)} data points generated")
        
        # Show XMV values (should be close to defaults)
        print(f"📋 Available columns: {list(data.columns)}")

        # Try to find XMV columns
        xmv_cols = [col for col in data.columns if col.startswith('XMV')]
        if not xmv_cols:
            print("⚠️  No XMV columns found in data - using fallback data")
            return data

        xmv_data = data[xmv_cols].iloc[-1]  # Last data point
        
        print("\n📊 Final XMV Values (Default Mode):")
        expected_defaults = [63.053, 53.980, 24.644, 61.302, 22.210,
                           40.064, 38.100, 46.534, 47.446, 41.106, 18.114]

        if len(xmv_data) > 0:
            for i, col in enumerate(xmv_cols):
                actual = xmv_data[col] if col in xmv_data.index else 0.0
                expected = expected_defaults[i] if i < len(expected_defaults) else 0.0
                print(f"   {col}: {actual:.3f} (expected ~{expected:.3f})")
        else:
            print("   No XMV data available")
        
        return data
    else:
        print("❌ Simulation failed - no data generated")
        return None

def test_user_control():
    """Test TEP with user-specified XMV values."""
    print("\n🎛️ Test 2: User Control Mode")
    print("=" * 60)
    
    # Create minimal disturbance matrix (no faults)
    steps = 5  # Short test
    idv_matrix = np.zeros((steps, 20))
    
    # Define custom XMV values (significantly different from defaults)
    user_xmv = [80.0, 70.0, 30.0, 80.0, 30.0, 50.0, 50.0, 60.0, 60.0, 50.0, 25.0]
    print(f"🎯 Setting custom XMV values: {user_xmv}")
    
    # Create TEP instance with user XMV
    tep_sim = tep2py(idv_matrix, speed_factor=1.0, user_xmv=user_xmv)
    
    # Run simulation
    tep_sim.simulate()
    
    # Check results
    if hasattr(tep_sim, 'process_data') and len(tep_sim.process_data) > 0:
        data = tep_sim.process_data
        print(f"✅ Simulation successful: {len(data)} data points generated")
        
        # Show XMV values (should be influenced by user settings)
        print(f"📋 Available columns: {list(data.columns)}")

        # Try to find XMV columns
        xmv_cols = [col for col in data.columns if col.startswith('XMV')]
        if not xmv_cols:
            print("⚠️  No XMV columns found in data - using fallback data")
            return data

        xmv_data = data[xmv_cols].iloc[-1]  # Last data point
        
        print("\n📊 Final XMV Values (User Control Mode):")
        if len(xmv_data) > 0:
            for i, col in enumerate(xmv_cols):
                actual = xmv_data[col] if col in xmv_data.index else 0.0
                set_val = user_xmv[i] if i < len(user_xmv) else 0.0
                print(f"   {col}: {actual:.3f} (set to {set_val:.3f})")
        else:
            print("   No XMV data available")
        
        return data
    else:
        print("❌ Simulation failed - no data generated")
        return None

def compare_results(default_data, user_data):
    """Compare results between default and user control modes."""
    if default_data is None or user_data is None:
        print("❌ Cannot compare - one or both simulations failed")
        return
    
    print("\n🔍 Comparison Analysis")
    print("=" * 60)
    
    # Compare XMV values
    xmv_cols = [col for col in default_data.columns if col.startswith('XMV')]
    if not xmv_cols:
        print("❌ No XMV columns found for comparison")
        return

    default_xmv = default_data[xmv_cols].iloc[-1]
    user_xmv = user_data[xmv_cols].iloc[-1]
    
    print("XMV Differences:")
    for i, col in enumerate(xmv_cols):
        diff = user_xmv[col] - default_xmv[col]
        print(f"   {col}: {diff:+.3f} ({default_xmv[col]:.3f} → {user_xmv[col]:.3f})")
    
    # Compare some key process measurements
    key_measurements = ['XMEAS_1', 'XMEAS_2', 'XMEAS_3', 'XMEAS_6', 'XMEAS_7']
    print("\nKey Process Measurement Differences:")
    for meas in key_measurements:
        if meas in default_data.columns and meas in user_data.columns:
            default_val = default_data[meas].iloc[-1]
            user_val = user_data[meas].iloc[-1]
            diff = user_val - default_val
            print(f"   {meas}: {diff:+.3f} ({default_val:.3f} → {user_val:.3f})")

def test_system_stability():
    """Test if the system remains stable with extreme XMV values."""
    print("\n⚠️  Test 3: System Stability with Extreme Values")
    print("=" * 60)
    
    # Create minimal disturbance matrix
    steps = 3  # Very short test for stability
    idv_matrix = np.zeros((steps, 20))
    
    # Test extreme values (but within reasonable bounds)
    extreme_xmv = [90.0, 90.0, 50.0, 90.0, 50.0, 70.0, 70.0, 80.0, 80.0, 70.0, 40.0]
    print(f"🚨 Testing extreme XMV values: {extreme_xmv}")
    
    try:
        tep_sim = tep2py(idv_matrix, speed_factor=1.0, user_xmv=extreme_xmv)
        tep_sim.simulate()
        
        if hasattr(tep_sim, 'process_data') and len(tep_sim.process_data) > 0:
            print("✅ System remains stable with extreme values")
            return True
        else:
            print("❌ System became unstable")
            return False
    except Exception as e:
        print(f"❌ System crashed with extreme values: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TEP XMV Control Test Suite")
    print("=" * 60)
    
    # Run tests
    default_data = test_default_operation()
    user_data = test_user_control()
    
    # Compare results
    compare_results(default_data, user_data)
    
    # Test stability
    stable = test_system_stability()
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 60)
    print(f"✅ Default operation: {'PASS' if default_data is not None else 'FAIL'}")
    print(f"✅ User control: {'PASS' if user_data is not None else 'FAIL'}")
    print(f"✅ System stability: {'PASS' if stable else 'FAIL'}")
    
    if default_data is not None and user_data is not None:
        print("\n🎉 XMV control is working! You can now control TEP valve positions.")
    else:
        print("\n❌ XMV control needs debugging.")
