#!/usr/bin/env python3
"""
Test TEP with the correct signature from f2py compilation output.
The f2py output shows: temain(npts,idata,xdata,verbose,[nx])
This means nx is optional and comes LAST, not second!
"""

import numpy as np
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_correct_f2py_signature():
    """Test with correct signature from f2py compilation."""
    try:
        import temain_mod
        
        print("🔧 Testing CORRECT f2py signature...")
        print("📋 From f2py output: temain(npts,idata,xdata,verbose,[nx])")
        print("📋 This means: npts, idata, xdata, verbose, then optional nx")
        
        # Create test data
        n_steps = 1
        
        # IDV input array (disturbances)
        idata = np.zeros((n_steps, 20), dtype=float)
        print(f"IDV array: shape={idata.shape}, dtype={idata.dtype}")
        
        # XDATA output array (measurements + manipulated variables)
        xdata = np.zeros((n_steps, 52), dtype=float)
        print(f"XDATA array: shape={xdata.shape}, dtype={xdata.dtype}")
        
        # Test new signature: npts, idata, xdata, verbose
        print("\n🎯 Testing new signature: temain(npts, idata, xdata, verbose)...")
        try:
            result = temain_mod.temain(
                np.asarray(60*3*idata.shape[0], dtype=int),  # npts
                idata,                                       # idata (IDV disturbances)
                xdata,                                       # xdata (output array)
                int(1)                                       # verbose
            )
            print(f"✅ SUCCESS with new signature!")
            print(f"   Result type: {type(result)}")
            if hasattr(result, 'shape'):
                print(f"   Result shape: {result.shape}")
                print(f"   Sample values: {result[0, :5] if len(result.shape) > 1 else result[:5]}")
            
            # Check if xdata was filled
            print(f"   XDATA filled: {np.any(xdata != 0)}")
            if np.any(xdata != 0):
                print(f"   XDATA sample: {xdata[0, :5]}")
            
            return result
            
        except Exception as e:
            print(f"❌ New signature failed: {e}")
            
        return None
        
    except ImportError as e:
        print(f"❌ Cannot import temain_mod: {e}")
        return None

def test_with_initialization():
    """Test with proper initialization sequence."""
    try:
        import temain_mod
        
        print("\n🔄 Testing with initialization...")
        
        # Initialize the system first
        print("1️⃣ Initializing TEP system...")
        try:
            # From f2py output: teinit(time,yy,yp,[nn])
            # Let's try with minimal parameters
            time = 0.0
            yy = np.zeros(50, dtype=float)  # State variables
            yp = np.zeros(50, dtype=float)  # Derivatives
            
            temain_mod.teinit(time, yy, yp)
            print("✅ teinit() successful")
        except Exception as e:
            print(f"⚠️ teinit failed: {e}")
            # Continue anyway
        
        # Now try temain
        print("2️⃣ Running temain after initialization...")
        n_steps = 1
        idata = np.zeros((n_steps, 20), dtype=float)
        xdata = np.zeros((n_steps, 52), dtype=float)
        
        try:
            result = temain_mod.temain(
                np.asarray(60*3*idata.shape[0], dtype=int),
                idata,
                xdata,
                int(1)
            )
            print(f"✅ temain after init: SUCCESS!")
            print(f"   XDATA filled: {np.any(xdata != 0)}")
            return True
            
        except Exception as e:
            print(f"❌ temain after init failed: {e}")
            
        return False
        
    except ImportError as e:
        print(f"❌ Cannot import temain_mod: {e}")
        return False

def test_common_blocks():
    """Test accessing COMMON blocks directly."""
    try:
        import temain_mod
        
        print("\n🔍 Testing COMMON block access...")
        
        # Check if we can access COMMON blocks
        common_blocks = ['pv', 'dvec', 'ctrlall', 'flag6']
        
        for block in common_blocks:
            if hasattr(temain_mod, block):
                print(f"✅ Found COMMON block: {block}")
                try:
                    block_obj = getattr(temain_mod, block)
                    print(f"   Type: {type(block_obj)}")
                    if hasattr(block_obj, 'xmeas'):
                        print(f"   Has xmeas: {block_obj.xmeas.shape if hasattr(block_obj.xmeas, 'shape') else type(block_obj.xmeas)}")
                    if hasattr(block_obj, 'xmv'):
                        print(f"   Has xmv: {block_obj.xmv.shape if hasattr(block_obj.xmv, 'shape') else type(block_obj.xmv)}")
                except Exception as e:
                    print(f"   Error accessing: {e}")
            else:
                print(f"❌ Missing COMMON block: {block}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Cannot import temain_mod: {e}")
        return False

def test_step_by_step():
    """Test step-by-step initialization and execution."""
    try:
        import temain_mod
        
        print("\n🎯 Step-by-step test...")
        
        # Step 1: Initialize COMMON blocks
        print("1️⃣ Accessing COMMON blocks...")
        if hasattr(temain_mod, 'pv'):
            pv = temain_mod.pv
            print(f"   PV block: {type(pv)}")
            
        # Step 2: Try to initialize system state
        print("2️⃣ Initializing system state...")
        try:
            # Try different initialization approaches
            time = 0.0
            nn = 50
            yy = np.zeros(nn, dtype=float)
            yp = np.zeros(nn, dtype=float)
            
            temain_mod.teinit(time, yy, yp, nn)
            print("✅ teinit with nn parameter successful")
        except Exception as e:
            print(f"⚠️ teinit with nn failed: {e}")
            try:
                temain_mod.teinit(time, yy, yp)
                print("✅ teinit without nn successful")
            except Exception as e2:
                print(f"⚠️ teinit without nn failed: {e2}")
        
        # Step 3: Try temain
        print("3️⃣ Running temain...")
        n_steps = 1
        idata = np.zeros((n_steps, 20), dtype=float)
        xdata = np.zeros((n_steps, 52), dtype=float)
        
        try:
            result = temain_mod.temain(
                np.asarray(60*3*n_steps, dtype=int),
                idata,
                xdata,
                1
            )
            print("✅ Step-by-step SUCCESS!")
            return True
        except Exception as e:
            print(f"❌ Step-by-step temain failed: {e}")
            
        return False
        
    except ImportError as e:
        print(f"❌ Cannot import temain_mod: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting TEP new signature test...")
    
    # Test 1: Correct f2py signature
    result = test_correct_f2py_signature()
    if result is not None:
        print("\n✅ New signature working!")
        sys.exit(0)
    
    # Test 2: With initialization
    if test_with_initialization():
        print("\n✅ Initialization sequence working!")
        sys.exit(0)
    
    # Test 3: COMMON blocks
    test_common_blocks()
    
    # Test 4: Step by step
    if test_step_by_step():
        print("\n✅ Step-by-step working!")
        sys.exit(0)
    
    print("\n❌ All new signature tests failed")
