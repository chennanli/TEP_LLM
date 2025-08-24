#!/usr/bin/env python3
"""
Minimal test to debug TEP Fortran integration issue.
Testing the simplest possible call to temain_mod.temain() to isolate dimension errors.
"""

import numpy as np
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_fortran_binary():
    """Test if Fortran binary loads correctly."""
    try:
        import temain_mod
        print("✅ Fortran binary loaded successfully")
        print(f"📋 Available functions: {[f for f in dir(temain_mod) if not f.startswith('_')]}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Fortran binary: {e}")
        return False

def test_minimal_temain_call():
    """Test the simplest possible TEMAIN call."""
    try:
        import temain_mod
        
        print("\n🔬 Testing minimal TEMAIN call...")
        
        # Test 1: Single timestep, all zeros
        print("\n--- Test 1: Single timestep, zeros ---")
        idata = np.zeros((1, 20), dtype=float)
        xdata = np.zeros((1, 52), dtype=float, order='F')
        
        print(f"IDV input shape: {idata.shape}, dtype: {idata.dtype}")
        print(f"XDATA output shape: {xdata.shape}, dtype: {xdata.dtype}, order: {'F' if xdata.flags.f_contiguous else 'C'}")
        
        try:
            result = temain_mod.temain(180, 1, idata, xdata, 1)
            print(f"✅ Test 1 SUCCESS: {type(result)}")
            if hasattr(result, 'shape'):
                print(f"   Result shape: {result.shape}")
            return True
        except Exception as e:
            print(f"❌ Test 1 FAILED: {e}")
            
        # Test 2: Try with ones instead of zeros
        print("\n--- Test 2: Single timestep, ones ---")
        idata = np.ones((1, 20), dtype=float)
        xdata = np.zeros((1, 52), dtype=float, order='F')
        
        try:
            result = temain_mod.temain(180, 1, idata, xdata, 1)
            print(f"✅ Test 2 SUCCESS: {type(result)}")
            return True
        except Exception as e:
            print(f"❌ Test 2 FAILED: {e}")
            
        # Test 3: Try different time parameter
        print("\n--- Test 3: Different time parameter ---")
        idata = np.zeros((1, 20), dtype=float)
        xdata = np.zeros((1, 52), dtype=float, order='F')
        
        try:
            result = temain_mod.temain(60, 1, idata, xdata, 1)
            print(f"✅ Test 3 SUCCESS: {type(result)}")
            return True
        except Exception as e:
            print(f"❌ Test 3 FAILED: {e}")
            
        return False
        
    except ImportError as e:
        print(f"❌ Cannot import temain_mod: {e}")
        return False

def test_matrix_dimensions():
    """Test different matrix dimensions to understand requirements."""
    try:
        import temain_mod
        
        print("\n🔍 Testing matrix dimension requirements...")
        
        # Test different numbers of timesteps
        for n_steps in [1, 2, 5, 10]:
            print(f"\n--- Testing {n_steps} timesteps ---")
            idata = np.zeros((n_steps, 20), dtype=float)
            xdata = np.zeros((n_steps, 52), dtype=float, order='F')
            
            try:
                result = temain_mod.temain(180, n_steps, idata, xdata, 1)
                print(f"✅ {n_steps} timesteps: SUCCESS")
                return True
            except Exception as e:
                print(f"❌ {n_steps} timesteps: {e}")
                
        return False
        
    except ImportError as e:
        print(f"❌ Cannot import temain_mod: {e}")
        return False

def test_tep2py_wrapper():
    """Test the tep2py wrapper to see where it fails."""
    try:
        print("\n🔧 Testing tep2py wrapper...")
        
        # Import the wrapper
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
            return True
        else:
            print("❌ No process data generated")
            return False
            
    except Exception as e:
        print(f"❌ tep2py wrapper failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting TEP Fortran debugging...")
    
    # Test 1: Binary loading
    if not test_fortran_binary():
        print("❌ Cannot proceed - Fortran binary not loading")
        sys.exit(1)
    
    # Test 2: Minimal TEMAIN calls
    if test_minimal_temain_call():
        print("\n✅ Minimal TEMAIN calls working!")
    else:
        print("\n❌ Minimal TEMAIN calls failing")
        
    # Test 3: Matrix dimensions
    if test_matrix_dimensions():
        print("\n✅ Matrix dimension tests working!")
    else:
        print("\n❌ Matrix dimension tests failing")
    
    # Test 4: tep2py wrapper
    if test_tep2py_wrapper():
        print("\n✅ tep2py wrapper working!")
    else:
        print("\n❌ tep2py wrapper failing")
    
    print("\n🏁 Debugging complete!")
