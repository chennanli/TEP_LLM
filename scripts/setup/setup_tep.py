#!/usr/bin/env python3
"""
TEP Simulator Setup and Verification Script
===========================================

This script helps users verify their TEP simulator installation
and provides guidance for getting started.

Author: Augment Agent
Date: 2025-06-29
"""

import os
import sys
import subprocess
import importlib.util


def check_virtual_environment():
    """Check if virtual environment is activated."""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment is activated")
        return True
    else:
        print("❌ Virtual environment is NOT activated")
        print("   Please run: source tep_env/bin/activate")
        return False


def check_required_packages():
    """Check if required Python packages are installed."""
    required_packages = ['numpy', 'pandas', 'matplotlib']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 To install missing packages, run:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True


def check_fortran_compiler():
    """Check if gfortran is available."""
    try:
        result = subprocess.run(['gfortran', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ gfortran is available: {version_line}")
            return True
        else:
            print("❌ gfortran is not working properly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ gfortran is NOT installed")
        print("   Please install with: brew install gcc")
        return False


def check_compiled_module():
    """Check if the Fortran module is compiled."""
    module_path = "external_repos/tep2py-master/temain_mod.cpython-39-darwin.so"
    
    if os.path.exists(module_path):
        print("✅ Compiled Fortran module found")
        return True
    else:
        print("❌ Compiled Fortran module NOT found")
        print("   Expected location: " + module_path)
        return False


def check_tep2py_import():
    """Check if tep2py can be imported."""
    sys.path.append('external_repos/tep2py-master')
    
    try:
        from tep2py import tep2py
        print("✅ tep2py module can be imported")
        return True
    except ImportError as e:
        print(f"❌ Cannot import tep2py: {e}")
        return False


def run_quick_test():
    """Run a quick simulation test."""
    try:
        sys.path.append('external_repos/tep2py-master')
        from tep2py import tep2py
        import numpy as np
        
        print("🧪 Running quick simulation test...")
        
        # Create small test simulation
        idata = np.zeros((3, 20))  # 3 samples, no faults
        tep = tep2py(idata)
        tep.simulate()
        
        if len(tep.process_data) == 3:
            print("✅ Quick simulation test PASSED")
            print(f"   Generated {len(tep.process_data)} data points")
            return True
        else:
            print("❌ Quick simulation test FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Quick simulation test FAILED: {e}")
        return False


def print_next_steps():
    """Print instructions for next steps."""
    print("\n" + "="*60)
    print("🎯 NEXT STEPS")
    print("="*60)
    print("1. Run the easy simulator:")
    print("   python tep_simulator_easy.py")
    print()
    print("2. Or use it in your own code:")
    print("   from tep_simulator_easy import TEPSimulatorEasy")
    print("   simulator = TEPSimulatorEasy()")
    print("   results = simulator.run_simulation(duration_hours=4, fault_type=1)")
    print()
    print("3. Explore different fault scenarios (0-20)")
    print("4. Modify simulation parameters as needed")
    print("5. Check generated CSV files and plots")


def main():
    """Main setup verification function."""
    print("🔧 TEP Simulator Setup Verification")
    print("="*60)
    
    checks = [
        ("Virtual Environment", check_virtual_environment),
        ("Required Packages", check_required_packages),
        ("Fortran Compiler", check_fortran_compiler),
        ("Compiled Module", check_compiled_module),
        ("TEP2PY Import", check_tep2py_import),
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n📋 Checking {check_name}...")
        if not check_func():
            all_passed = False
    
    print("\n" + "="*60)
    
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ Your TEP simulator is ready to use!")
        
        # Run quick test
        print("\n📊 Running final verification test...")
        if run_quick_test():
            print_next_steps()
        else:
            print("❌ Final test failed. Please check the error messages above.")
    else:
        print("❌ SOME CHECKS FAILED")
        print("Please fix the issues above before proceeding.")
        print("\n💡 Common solutions:")
        print("   • Activate virtual environment: source tep_env/bin/activate")
        print("   • Install packages: pip install numpy pandas matplotlib")
        print("   • Install gfortran: brew install gcc")
        print("   • Recompile Fortran: cd external_repos/tep2py-master && python -m numpy.f2py -c temain_mod-smart.pyf src/tep/temain_mod.f src/tep/teprob.f")


if __name__ == "__main__":
    main()
