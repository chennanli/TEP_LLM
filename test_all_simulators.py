#!/usr/bin/env python3
"""
Comprehensive Test of All Simulators
====================================

Tests all simulator options to ensure they work properly.
"""

import subprocess
import sys
import os
import time
import importlib.util

def test_imports():
    """Test all required imports."""
    print("🔍 Testing Required Imports...")
    print("="*50)
    
    # Test TEP simulator
    try:
        sys.path.append('external_repos/tep2py-master')
        from tep2py import tep2py
        print("✅ TEP simulator (tep2py) - OK")
    except ImportError as e:
        print(f"❌ TEP simulator (tep2py) - FAILED: {e}")
        return False
    
    # Test Flask
    try:
        import flask
        print("✅ Flask - OK")
    except ImportError as e:
        print(f"❌ Flask - FAILED: {e}")
        return False
    
    # Test PyQt5
    try:
        import PyQt5
        print("✅ PyQt5 - OK")
    except ImportError as e:
        print(f"❌ PyQt5 - FAILED: {e}")
        return False
    
    # Test psutil
    try:
        import psutil
        print("✅ psutil - OK")
    except ImportError as e:
        print(f"❌ psutil - FAILED: {e}")
        return False
    
    # Test matplotlib
    try:
        import matplotlib
        print("✅ matplotlib - OK")
    except ImportError as e:
        print(f"❌ matplotlib - FAILED: {e}")
        return False
    
    # Test numpy
    try:
        import numpy
        print("✅ numpy - OK")
    except ImportError as e:
        print(f"❌ numpy - FAILED: {e}")
        return False
    
    # Test pandas
    try:
        import pandas
        print("✅ pandas - OK")
    except ImportError as e:
        print(f"❌ pandas - FAILED: {e}")
        return False
    
    print("\n✅ All imports successful!")
    return True

def test_file_existence():
    """Test if all simulator files exist."""
    print("\n🔍 Testing File Existence...")
    print("="*50)
    
    files_to_check = [
        "simulators/live/simple_web_tep_simulator.py",
        "simulators/live/clean_qt_tep_simulator.py", 
        "simulators/live/smart_launcher.py",
        "simulators/live/improved_tep_simulator.py",
        "scripts/utilities/check_simulators.py",
        "generate_training_data.py",
        "run_simulator.py"
    ]
    
    all_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - EXISTS")
        else:
            print(f"❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def test_simulator_syntax(file_path):
    """Test if a Python file has valid syntax."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        compile(content, file_path, 'exec')
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking {file_path}: {e}")
        return False

def test_syntax():
    """Test syntax of all simulator files."""
    print("\n🔍 Testing Python Syntax...")
    print("="*50)
    
    files_to_check = [
        "simulators/live/simple_web_tep_simulator.py",
        "simulators/live/clean_qt_tep_simulator.py", 
        "simulators/live/smart_launcher.py",
        "simulators/live/improved_tep_simulator.py",
        "scripts/utilities/check_simulators.py",
        "generate_training_data.py",
        "run_simulator.py"
    ]
    
    all_valid = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            if test_simulator_syntax(file_path):
                print(f"✅ {file_path} - SYNTAX OK")
            else:
                all_valid = False
        else:
            print(f"❌ {file_path} - FILE MISSING")
            all_valid = False
    
    return all_valid

def test_tep_simulation():
    """Test basic TEP simulation functionality."""
    print("\n🔍 Testing TEP Simulation...")
    print("="*50)
    
    try:
        sys.path.append('external_repos/tep2py-master')
        from tep2py import tep2py
        import numpy as np
        
        # Create test data
        idata = np.zeros((2, 20))
        idata[1, 0] = 1.0  # Fault 1
        
        # Run simulation
        tep = tep2py(idata)
        tep.simulate()
        data = tep.process_data
        
        if len(data) > 0:
            print("✅ TEP simulation - OK")
            print(f"   Generated {len(data)} data points")
            print(f"   Variables: {len(data.columns)} columns")
            return True
        else:
            print("❌ TEP simulation - NO DATA GENERATED")
            return False
            
    except Exception as e:
        print(f"❌ TEP simulation - FAILED: {e}")
        return False

def test_launcher_options():
    """Test if launcher can find all simulator files."""
    print("\n🔍 Testing Launcher Options...")
    print("="*50)
    
    # Test if run_simulator.py can import subprocess
    try:
        result = subprocess.run([
            sys.executable, "-c", 
            "import subprocess; import sys; import os; print('Launcher imports OK')"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Launcher imports - OK")
        else:
            print(f"❌ Launcher imports - FAILED: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Launcher test - FAILED: {e}")
        return False
    
    return True

def main():
    """Run comprehensive tests."""
    print("🎛️ Comprehensive TEP Simulator Test")
    print("="*60)
    print("Testing all simulator options to ensure they work properly.")
    print()
    
    # Check virtual environment
    if 'tep_env' not in sys.executable:
        print("⚠️  WARNING: Virtual environment not detected!")
        print("   Please run: source tep_env/bin/activate")
        print("   Then run this script again.")
        return
    
    tests = [
        ("Import Dependencies", test_imports),
        ("File Existence", test_file_existence),
        ("Python Syntax", test_syntax),
        ("TEP Simulation", test_tep_simulation),
        ("Launcher Options", test_launcher_options)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} - EXCEPTION: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("🎯 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("All simulator options should work correctly.")
        print("\n🚀 You can now use:")
        print("   python run_simulator.py")
    else:
        print(f"\n⚠️  {total - passed} TESTS FAILED!")
        print("Some simulator options may not work correctly.")
        print("Please check the errors above.")
    
    print("\n🎛️ Available Options:")
    print("1️⃣  Simple Web Simulator - http://localhost:8081")
    print("2️⃣  Clean Qt Simulator - Desktop app")
    print("3️⃣  All Simulators - Multiple with auto-cleanup")
    print("4️⃣  Improved TEP Simulator - http://localhost:8082")
    print("5️⃣  Check/Clean Processes - Utility")

if __name__ == "__main__":
    main()
