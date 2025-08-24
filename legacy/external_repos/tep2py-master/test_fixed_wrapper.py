#!/usr/bin/env python3
"""
Test the fixed tep2py wrapper with correct Fortran signature.
"""

import numpy as np
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_fixed_wrapper():
    """Test the fixed tep2py wrapper."""
    try:
        print("🔧 Testing fixed tep2py wrapper...")
        
        # Import the fixed wrapper
        import tep2py
        
        # Create minimal IDV matrix (1 timestep, 20 IDV variables)
        idv_matrix = np.zeros((1, 20), dtype=float)
        print(f"IDV matrix shape: {idv_matrix.shape}")
        
        # Try to create tep2py instance
        tep_sim = tep2py.tep2py(idv_matrix, speed_factor=1.0)
        print("✅ tep2py instance created")
        
        # Try to simulate
        tep_sim.simulate()
        print("✅ Simulation completed")
        
        if hasattr(tep_sim, 'process_data'):
            print(f"✅ Process data generated: {len(tep_sim.process_data)} rows")
            print(f"   Columns: {list(tep_sim.process_data.columns[:5])}")
            print(f"   Sample XMEAS: {tep_sim.process_data.iloc[0, :5].values}")
            print(f"   Sample XMV: {tep_sim.process_data.iloc[0, 41:46].values}")
            return True
        else:
            print("❌ No process data generated")
            return False
            
    except Exception as e:
        print(f"❌ Fixed wrapper failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_timesteps():
    """Test with multiple timesteps."""
    try:
        print("\n📈 Testing multiple timesteps...")
        
        import tep2py
        
        # Test with 3 timesteps
        idv_matrix = np.zeros((3, 20), dtype=float)
        # Add a disturbance in the second timestep
        idv_matrix[1, 0] = 1.0  # IDV_1 (A/C Feed Ratio)
        
        print(f"IDV matrix: {idv_matrix.shape}")
        print(f"Disturbance at timestep 1: IDV_1 = {idv_matrix[1, 0]}")
        
        tep_sim = tep2py.tep2py(idv_matrix, speed_factor=1.0)
        tep_sim.simulate()
        
        if hasattr(tep_sim, 'process_data'):
            print(f"✅ Multi-timestep data: {len(tep_sim.process_data)} rows")
            
            # Show how measurements change with disturbance
            for i in range(len(tep_sim.process_data)):
                xmeas_1 = tep_sim.process_data.iloc[i, 0]  # First measurement
                print(f"   Timestep {i}: XMEAS_1 = {xmeas_1:.6f}")
            
            return True
        else:
            print("❌ No multi-timestep data generated")
            return False
            
    except Exception as e:
        print(f"❌ Multi-timestep test failed: {e}")
        return False

def test_with_speed_factor():
    """Test with different speed factors."""
    try:
        print("\n⚡ Testing speed factors...")
        
        import tep2py
        
        idv_matrix = np.zeros((2, 20), dtype=float)
        
        for speed in [1.0, 10.0, 50.0]:
            print(f"\n--- Testing speed factor {speed}x ---")
            
            tep_sim = tep2py.tep2py(idv_matrix, speed_factor=speed)
            tep_sim.simulate()
            
            if hasattr(tep_sim, 'process_data'):
                print(f"✅ Speed {speed}x: {len(tep_sim.process_data)} rows generated")
            else:
                print(f"❌ Speed {speed}x: No data generated")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Speed factor test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting fixed wrapper test...")
    
    # Test 1: Basic wrapper functionality
    if test_fixed_wrapper():
        print("\n✅ Fixed wrapper working!")
        
        # Test 2: Multiple timesteps
        if test_multiple_timesteps():
            print("\n✅ Multiple timesteps working!")
            
            # Test 3: Speed factors
            if test_with_speed_factor():
                print("\n✅ Speed factors working!")
                
                print("\n🎉 TEP wrapper completely FIXED!")
                print("🔄 Ready to test full data pipeline!")
                sys.exit(0)
    
    print("\n❌ Wrapper tests failed")
