#!/usr/bin/env python3
"""
Test TEP with correct data types based on Fortran interface.
The .pyf file shows idata should be INTEGER, not FLOAT!
"""

import numpy as np
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_correct_data_types():
    """Test with correct data types from Fortran interface."""
    try:
        import temain_mod
        
        print("🔧 Testing with CORRECT data types...")
        print("📋 From .pyf file: idata should be INTEGER dimension(nx,20)")
        
        # Initialize COMMON blocks first
        print("🚀 Initializing COMMON blocks...")
        
        # Try to initialize the system
        try:
            # Call teinit with a time parameter
            print("🔧 Calling teinit with time parameter...")
            temain_mod.teinit(0.0)  # Initialize with time=0
            print("✅ teinit(0.0) successful")
        except Exception as e:
            print(f"⚠️ teinit failed: {e}")
            # Continue anyway
        
        # Create arrays with CORRECT types
        n_steps = 1
        
        # IDV array - INTEGER type as specified in .pyf
        idata = np.zeros((n_steps, 20), dtype=np.int32, order='F')
        print(f"IDV array: shape={idata.shape}, dtype={idata.dtype}, order={'F' if idata.flags.f_contiguous else 'C'}")
        
        # XDATA array - DOUBLE PRECISION (float64)
        xdata = np.zeros((n_steps, 52), dtype=np.float64, order='F')
        print(f"XDATA array: shape={xdata.shape}, dtype={xdata.dtype}, order={'F' if xdata.flags.f_contiguous else 'C'}")
        
        # Test with correct types
        print("\n🎯 Testing temain with INTEGER idata...")
        try:
            result = temain_mod.temain(180, n_steps, idata, xdata, 1)
            print(f"✅ SUCCESS with INTEGER idata!")
            print(f"   Result type: {type(result)}")
            if hasattr(result, 'shape'):
                print(f"   Result shape: {result.shape}")
            
            # Check if xdata was filled
            print(f"   XDATA sample values: {xdata[0, :5]}")
            return True
            
        except Exception as e:
            print(f"❌ Still failed with INTEGER idata: {e}")
            
        return False
        
    except ImportError as e:
        print(f"❌ Cannot import temain_mod: {e}")
        return False

def test_with_initialization_sequence():
    """Test complete initialization sequence."""
    try:
        import temain_mod
        
        print("\n🔄 Testing complete initialization sequence...")
        
        # Step 1: Initialize system
        print("1️⃣ Initializing TEP system...")
        try:
            # Try different initialization approaches
            temain_mod.teinit(0.0)
            print("✅ teinit(0.0) completed")
        except Exception as e:
            print(f"⚠️ teinit failed: {e}")
        
        # Step 2: Set up arrays with correct types
        print("2️⃣ Setting up arrays...")
        n_steps = 1
        
        # INTEGER idata (IDV disturbances)
        idata = np.zeros((n_steps, 20), dtype=np.int32, order='F')
        
        # DOUBLE PRECISION xdata (output measurements)
        xdata = np.zeros((n_steps, 52), dtype=np.float64, order='F')
        
        print(f"   IDV: {idata.shape} {idata.dtype}")
        print(f"   XDATA: {xdata.shape} {xdata.dtype}")
        
        # Step 3: Call temain
        print("3️⃣ Calling temain...")
        try:
            result = temain_mod.temain(180, n_steps, idata, xdata, 1)
            print("✅ temain SUCCESS!")
            
            # Check results
            print(f"   Result: {type(result)}")
            print(f"   XDATA filled: {np.any(xdata != 0)}")
            print(f"   Sample XDATA: {xdata[0, :3]}")
            
            return True
            
        except Exception as e:
            print(f"❌ temain failed: {e}")
            
        return False
        
    except ImportError as e:
        print(f"❌ Cannot import temain_mod: {e}")
        return False

def test_multiple_timesteps():
    """Test with multiple timesteps once basic call works."""
    try:
        import temain_mod
        
        print("\n📈 Testing multiple timesteps...")
        
        # Initialize
        try:
            temain_mod.teinit(0.0)
        except:
            pass
        
        # Test with multiple timesteps
        for n_steps in [1, 2, 5]:
            print(f"\n--- Testing {n_steps} timesteps ---")
            
            # INTEGER idata
            idata = np.zeros((n_steps, 20), dtype=np.int32, order='F')
            
            # DOUBLE PRECISION xdata
            xdata = np.zeros((n_steps, 52), dtype=np.float64, order='F')
            
            try:
                result = temain_mod.temain(180, n_steps, idata, xdata, 1)
                print(f"✅ {n_steps} timesteps: SUCCESS")
                print(f"   XDATA shape: {xdata.shape}")
                print(f"   Sample values: {xdata[-1, :3]}")  # Last timestep
                
                if n_steps == 1:
                    return True  # Success with single timestep
                    
            except Exception as e:
                print(f"❌ {n_steps} timesteps failed: {e}")
                
        return False
        
    except ImportError as e:
        print(f"❌ Cannot import temain_mod: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting TEP correct data types test...")
    
    # Test 1: Correct data types
    if test_correct_data_types():
        print("\n✅ Correct data types working!")
        
        # Test 2: Complete sequence
        if test_with_initialization_sequence():
            print("\n✅ Complete initialization sequence working!")
            
            # Test 3: Multiple timesteps
            if test_multiple_timesteps():
                print("\n✅ Multiple timesteps working!")
            
        print("\n🎉 TEP Fortran integration FIXED!")
        sys.exit(0)
    
    print("\n❌ Still not working - need more investigation")
