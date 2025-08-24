#!/usr/bin/env python3
"""
Test TEP initialization sequence to fix dimension errors.
The error suggests we need to initialize the TEP system before calling temain.
"""

import numpy as np
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_tep_initialization():
    """Test if we need to call teinit before temain."""
    try:
        import temain_mod
        
        print("🔧 Testing TEP initialization sequence...")
        
        # Check if teinit exists and what it does
        if hasattr(temain_mod, 'teinit'):
            print("✅ Found teinit function")
            
            # Try calling teinit first
            print("🚀 Calling teinit()...")
            try:
                result = temain_mod.teinit()
                print(f"✅ teinit() completed: {result}")
            except Exception as e:
                print(f"❌ teinit() failed: {e}")
                return False
                
            # Now try temain after initialization
            print("🔬 Testing temain after teinit...")
            idata = np.zeros((1, 20), dtype=float)
            xdata = np.zeros((1, 52), dtype=float, order='F')
            
            try:
                result = temain_mod.temain(180, 1, idata, xdata, 1)
                print(f"✅ temain after teinit: SUCCESS!")
                return True
            except Exception as e:
                print(f"❌ temain after teinit: {e}")
                
        else:
            print("❌ No teinit function found")
            
        return False
        
    except ImportError as e:
        print(f"❌ Cannot import temain_mod: {e}")
        return False

def test_alternative_functions():
    """Test other TEP functions that might work."""
    try:
        import temain_mod
        
        print("\n🔍 Testing alternative TEP functions...")
        
        # Test teproc function
        if hasattr(temain_mod, 'teproc'):
            print("🧪 Testing teproc function...")
            try:
                # teproc might be the low-level function
                result = temain_mod.teproc()
                print(f"✅ teproc() worked: {result}")
            except Exception as e:
                print(f"❌ teproc() failed: {e}")
        
        # Test tefunc function  
        if hasattr(temain_mod, 'tefunc'):
            print("🧪 Testing tefunc function...")
            try:
                result = temain_mod.tefunc()
                print(f"✅ tefunc() worked: {result}")
            except Exception as e:
                print(f"❌ tefunc() failed: {e}")
                
        # Test temain_accelerated
        if hasattr(temain_mod, 'temain_accelerated'):
            print("🧪 Testing temain_accelerated function...")
            try:
                idata = np.zeros((1, 20), dtype=float)
                xdata = np.zeros((1, 52), dtype=float, order='F')
                result = temain_mod.temain_accelerated(180, 1, idata, xdata, 1)
                print(f"✅ temain_accelerated worked!")
                return True
            except Exception as e:
                print(f"❌ temain_accelerated failed: {e}")
                
        return False
        
    except ImportError as e:
        print(f"❌ Cannot import temain_mod: {e}")
        return False

def test_with_proper_arrays():
    """Test with properly initialized arrays."""
    try:
        import temain_mod
        
        print("\n🎯 Testing with properly initialized arrays...")
        
        # Try calling teinit first if it exists
        if hasattr(temain_mod, 'teinit'):
            try:
                temain_mod.teinit()
                print("✅ teinit() called")
            except:
                pass
        
        # Create arrays with proper initialization
        n_steps = 1
        
        # IDV array - try with proper values instead of zeros
        idata = np.zeros((n_steps, 20), dtype=np.float64, order='F')
        print(f"IDV array: shape={idata.shape}, dtype={idata.dtype}, order={'F' if idata.flags.f_contiguous else 'C'}")
        
        # XDATA array - pre-allocate with Fortran ordering
        xdata = np.zeros((n_steps, 52), dtype=np.float64, order='F')
        print(f"XDATA array: shape={xdata.shape}, dtype={xdata.dtype}, order={'F' if xdata.flags.f_contiguous else 'C'}")
        
        # Try different parameter combinations
        test_params = [
            (180, n_steps, idata, xdata, 1),
            (60, n_steps, idata, xdata, 1),
            (180, n_steps, idata, xdata, 0),
        ]
        
        for i, params in enumerate(test_params):
            print(f"\n--- Test {i+1}: time={params[0]}, steps={params[1]}, verbose={params[4]} ---")
            try:
                result = temain_mod.temain(*params)
                print(f"✅ SUCCESS with params {params[:2]} + arrays + {params[4]}")
                print(f"   Result type: {type(result)}")
                if hasattr(result, 'shape'):
                    print(f"   Result shape: {result.shape}")
                return True
            except Exception as e:
                print(f"❌ Failed: {e}")
                
        return False
        
    except ImportError as e:
        print(f"❌ Cannot import temain_mod: {e}")
        return False

def inspect_fortran_signature():
    """Try to understand the Fortran function signature."""
    try:
        import temain_mod
        
        print("\n🔍 Inspecting Fortran function signatures...")
        
        # Check the .pyf files for interface definitions
        pyf_files = ['temain_mod-auto.pyf', 'temain_mod-smart.pyf']
        
        for pyf_file in pyf_files:
            if os.path.exists(pyf_file):
                print(f"\n📄 Found {pyf_file}:")
                with open(pyf_file, 'r') as f:
                    content = f.read()
                    # Look for temain function definition
                    if 'subroutine temain' in content.lower():
                        lines = content.split('\n')
                        in_temain = False
                        for line in lines:
                            if 'subroutine temain' in line.lower():
                                in_temain = True
                            if in_temain:
                                print(f"   {line}")
                                if 'end subroutine' in line.lower():
                                    break
                        return True
        
        print("❌ No .pyf files found with temain definition")
        return False
        
    except Exception as e:
        print(f"❌ Error inspecting signatures: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting TEP initialization debugging...")
    
    # Test 1: Initialization sequence
    if test_tep_initialization():
        print("\n✅ Initialization sequence working!")
        sys.exit(0)
    
    # Test 2: Alternative functions
    if test_alternative_functions():
        print("\n✅ Alternative functions working!")
        sys.exit(0)
    
    # Test 3: Proper arrays
    if test_with_proper_arrays():
        print("\n✅ Proper array initialization working!")
        sys.exit(0)
    
    # Test 4: Inspect signatures
    inspect_fortran_signature()
    
    print("\n❌ All tests failed - need to investigate further")
