#!/usr/bin/env python3
"""
Test LLM Integration for TEP Fault Diagnosis
===========================================

This script tests the complete LLM fault diagnosis pipeline:
1. TEP simulator generates fault data
2. FaultExplainer backend analyzes the data
3. LLM provides natural language explanation

Usage:
    python test_llm_integration.py
"""

import sys
import numpy as np
import pandas as pd
import requests
import json
import time
from datetime import datetime

# Add TEP simulator to path
sys.path.append('external_repos/tep2py-master')

def test_tep_simulator():
    """Test if TEP simulator is working."""
    print("🔍 Testing TEP Simulator...")
    try:
        from tep2py import tep2py
        
        # Create test data with fault
        idata = np.zeros((2, 20))
        idata[1, 0] = 1.0  # Fault 1: A/C Feed Ratio
        
        # Run simulation
        tep = tep2py(idata)
        tep.simulate()
        data = tep.process_data
        
        if len(data) > 0:
            print(f"✅ TEP simulator working - Generated {len(data)} data points")
            return True, data
        else:
            print("❌ TEP simulator - No data generated")
            return False, None
            
    except Exception as e:
        print(f"❌ TEP simulator error: {e}")
        return False, None

def test_faultexplainer_backend():
    """Test if FaultExplainer backend is running."""
    print("\n🔍 Testing FaultExplainer Backend...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ FaultExplainer backend is running")
            return True
        else:
            print(f"❌ FaultExplainer backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ FaultExplainer backend not running")
        print("   Start it with: cd external_repos/FaultExplainer-MultiLLM/backend && python app.py")
        return False
    except Exception as e:
        print(f"❌ FaultExplainer backend error: {e}")
        return False

def test_llm_analysis(tep_data):
    """Test LLM analysis with real TEP data."""
    print("\n🔍 Testing LLM Analysis...")
    try:
        # Prepare data for analysis (simulate fault detection)
        latest_data = tep_data.iloc[-10:].to_dict('records')  # Last 10 data points
        
        # Create analysis request
        analysis_request = {
            "fault_detected": True,
            "fault_type": 1,
            "sensor_data": latest_data,
            "top_features": ["XMEAS(9)", "XMEAS(7)", "XMEAS(40)", "XMEAS(14)", "XMEAS(17)", "XMEAS(10)"],
            "timestamp": datetime.now().isoformat()
        }
        
        print("📤 Sending analysis request to LLM...")
        response = requests.post(
            "http://localhost:8000/analyze",
            json=analysis_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ LLM analysis successful!")
            print("\n🤖 LLM Response:")
            print("=" * 60)
            print(result.get('explanation', 'No explanation provided'))
            print("=" * 60)
            return True
        else:
            print(f"❌ LLM analysis failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ LLM analysis error: {e}")
        return False

def test_live_integration():
    """Test the live TEP with LLM integration."""
    print("\n🔍 Testing Live Integration...")
    try:
        # Import the live simulator
        from simulators.live.live_tep_with_llm import FaultExplainerClient
        
        # Test client connection
        client = FaultExplainerClient()
        if client.test_connection():
            print("✅ Live integration client working")
            return True
        else:
            print("❌ Live integration client failed")
            return False
            
    except Exception as e:
        print(f"❌ Live integration error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 TEP LLM Integration Test Suite")
    print("=" * 50)
    
    # Test 1: TEP Simulator
    tep_ok, tep_data = test_tep_simulator()
    if not tep_ok:
        print("\n❌ Cannot proceed without working TEP simulator")
        return
    
    # Test 2: FaultExplainer Backend
    backend_ok = test_faultexplainer_backend()
    if not backend_ok:
        print("\n⚠️  FaultExplainer backend not running - skipping LLM tests")
        print("\n🚀 To start the backend:")
        print("   cd external_repos/FaultExplainer-MultiLLM/backend")
        print("   python app.py")
        return
    
    # Test 3: LLM Analysis
    llm_ok = test_llm_analysis(tep_data)
    
    # Test 4: Live Integration
    live_ok = test_live_integration()
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 TEST SUMMARY")
    print("=" * 50)
    
    tests = [
        ("TEP Simulator", tep_ok),
        ("FaultExplainer Backend", backend_ok),
        ("LLM Analysis", llm_ok),
        ("Live Integration", live_ok)
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("Your LLM fault diagnosis system is ready!")
        print("\n🚀 Next steps:")
        print("1. Run: python simulators/live/live_tep_with_llm.py")
        print("2. Select a fault and watch the LLM analysis")
        print("3. Experiment with different fault types")
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        print("Please check the errors above and follow the setup guide")

if __name__ == "__main__":
    main()
