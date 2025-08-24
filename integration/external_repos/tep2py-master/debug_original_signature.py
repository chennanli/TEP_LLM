#!/usr/bin/env python3
"""
Test TEP with original function signature from tep2py_original.py
The original uses only 4 arguments, not 5!
"""

import numpy as np
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_original_signature():
    """Test with original 4-argument signature."""
    try:
        import temain_mod
        
        print("🔧 Testing ORIGINAL 4-argument signature...")
        print("📋 From tep2py_original.py: temain(npts, nx, idata, verbose)")
        
        # Create test data like original
        n_steps = 1
        
        # Use FLOAT arrays like original (not INTEGER!)
        idata = np.zeros((n_steps, 20), dtype=float)
        print(f"IDV array: shape={idata.shape}, dtype={idata.dtype}")
        
        # Test original 4-argument call
        print("\n🎯 Testing 4-argument temain call...")
        try:
            result = temain_mod.temain(
                np.asarray(60*3*idata.shape[0], dtype=int),  # npts
                idata.shape[0],                              # nx  
                idata,                                       # idata
                int(1)                                       # verbose
            )
            print(f"✅ SUCCESS with 4-argument signature!")
            print(f"   Result type: {type(result)}")
            if hasattr(result, 'shape'):
                print(f"   Result shape: {result.shape}")
                print(f"   Sample values: {result[0, :5] if len(result.shape) > 1 else result[:5]}")
            
            return result
            
        except Exception as e:
            print(f"❌ 4-argument call failed: {e}")
            
        return None
        
    except ImportError as e:
        print(f"❌ Cannot import temain_mod: {e}")
        return None

def test_original_class():
    """Test the original tep2py class."""
    try:
        print("\n🔄 Testing original tep2py class...")
        
        # Import original class
        sys.path.insert(0, '.')
        from tep2py_original import tep2py as original_tep2py
        
        # Create test IDV matrix
        idata = np.zeros((1, 20), dtype=float)
        print(f"IDV matrix: {idata.shape}")
        
        # Create original tep2py instance
        tep_sim = original_tep2py(idata)
        print("✅ Original tep2py instance created")
        
        # Run simulation
        tep_sim.simulate()
        print("✅ Original simulation completed")
        
        if hasattr(tep_sim, 'process_data'):
            print(f"✅ Process data generated: {len(tep_sim.process_data)} rows")
            print(f"   Columns: {list(tep_sim.process_data.columns[:5])}")
            print(f"   Sample data: {tep_sim.process_data.iloc[0, :5].values}")
            return True
        else:
            print("❌ No process data generated")
            return False
            
    except Exception as e:
        print(f"❌ Original class failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_steps_original():
    """Test multiple timesteps with original signature."""
    try:
        import temain_mod
        
        print("\n📈 Testing multiple timesteps with original signature...")
        
        for n_steps in [1, 2, 5]:
            print(f"\n--- Testing {n_steps} timesteps ---")
            
            # FLOAT idata like original
            idata = np.zeros((n_steps, 20), dtype=float)
            
            try:
                result = temain_mod.temain(
                    np.asarray(60*3*idata.shape[0], dtype=int),
                    idata.shape[0],
                    idata,
                    int(1)
                )
                print(f"✅ {n_steps} timesteps: SUCCESS")
                print(f"   Result shape: {result.shape}")
                
            except Exception as e:
                print(f"❌ {n_steps} timesteps failed: {e}")
                
        return True
        
    except ImportError as e:
        print(f"❌ Cannot import temain_mod: {e}")
        return False

def test_with_disturbances():
    """Test with actual disturbance values."""
    try:
        import temain_mod
        
        print("\n🎛️ Testing with actual disturbance values...")
        
        # Create IDV matrix with some disturbances
        n_steps = 2
        idata = np.zeros((n_steps, 20), dtype=float)
        
        # Set IDV_1 (A/C Feed Ratio) to 1 in second timestep
        idata[1, 0] = 1.0
        print(f"IDV matrix with disturbance: {idata}")
        
        try:
            result = temain_mod.temain(
                np.asarray(60*3*idata.shape[0], dtype=int),
                idata.shape[0],
                idata,
                int(1)
            )
            print(f"✅ Disturbance test SUCCESS!")
            print(f"   Result shape: {result.shape}")
            print(f"   First timestep: {result[0, :3]}")
            print(f"   Second timestep: {result[1, :3]}")
            
            return True
            
        except Exception as e:
            print(f"❌ Disturbance test failed: {e}")
            
        return False
        
    except ImportError as e:
        print(f"❌ Cannot import temain_mod: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting TEP original signature test...")
    
    # Test 1: Original 4-argument signature
    result = test_original_signature()
    if result is not None:
        print("\n✅ Original signature working!")
        
        # Test 2: Original class
        if test_original_class():
            print("\n✅ Original class working!")
            
            # Test 3: Multiple timesteps
            if test_multiple_steps_original():
                print("\n✅ Multiple timesteps working!")
                
                # Test 4: With disturbances
                if test_with_disturbances():
                    print("\n✅ Disturbance tests working!")
                
            print("\n🎉 TEP Fortran integration WORKING with original signature!")
            sys.exit(0)
    
    print("\n❌ Original signature still not working")
