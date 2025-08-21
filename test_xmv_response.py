#!/usr/bin/env python3
"""
🧪 XMV Response Test - Verify XMV controls actually affect XMEAS measurements

This test will:
1. Run TEP with default XMV values
2. Run TEP with extreme XMV values  
3. Compare the XMEAS responses to see if XMV controls are working
"""

import numpy as np
import pandas as pd
import sys
import os

# Add the path to find tep2py
sys.path.append('legacy/external_repos/tep2py-master')
from tep2py import tep2py

def test_xmv_response():
    """Test if XMV changes actually affect XMEAS measurements."""
    
    print("🧪 XMV RESPONSE TEST")
    print("=" * 60)
    print("Testing if XMV controls actually affect XMEAS measurements...")
    
    # Test parameters
    steps = 10  # 30 minutes of simulation (3 min per step)
    idv_matrix = np.zeros((steps, 20))  # No faults
    
    # Test 1: Default XMV values
    print("\n📊 Test 1: Default XMV Values")
    print("-" * 40)
    
    tep_default = tep2py(idv_matrix, speed_factor=1.0)
    tep_default.simulate()
    
    if not hasattr(tep_default, 'process_data') or len(tep_default.process_data) == 0:
        print("❌ Default simulation failed!")
        return
    
    default_data = tep_default.process_data
    print(f"✅ Default simulation: {len(default_data)} data points")
    
    # Test 2: Extreme XMV values (push key controls to limits)
    print("\n📊 Test 2: Extreme XMV Values")
    print("-" * 40)
    
    # Push key XMV controls to extreme values
    extreme_xmv = [
        90.0,  # XMV_1: D Feed Flow (default ~63) -> 90%
        90.0,  # XMV_2: E Feed Flow (default ~54) -> 90%  
        10.0,  # XMV_3: A Feed Flow (default ~24) -> 10%
        90.0,  # XMV_4: A+C Feed Flow (default ~61) -> 90%
        10.0,  # XMV_5: Compressor Recycle (default ~22) -> 10%
        80.0,  # XMV_6: Purge Valve (default ~40) -> 80%
        80.0,  # XMV_7: Separator Liquid (default ~38) -> 80%
        80.0,  # XMV_8: Stripper Liquid (default ~46) -> 80%
        80.0,  # XMV_9: Stripper Steam (default ~47) -> 80%
        80.0,  # XMV_10: Reactor Cooling (default ~41) -> 80%
        80.0   # XMV_11: Condenser Cooling (default ~18) -> 80%
    ]
    
    print(f"🎯 Setting extreme XMV values: {extreme_xmv}")
    
    tep_extreme = tep2py(idv_matrix, speed_factor=1.0, user_xmv=extreme_xmv)
    tep_extreme.simulate()
    
    if not hasattr(tep_extreme, 'process_data') or len(tep_extreme.process_data) == 0:
        print("❌ Extreme simulation failed!")
        return
    
    extreme_data = tep_extreme.process_data
    print(f"✅ Extreme simulation: {len(extreme_data)} data points")
    
    # Test 3: Compare key XMEAS responses
    print("\n📈 Test 3: XMEAS Response Analysis")
    print("-" * 40)
    
    # Key XMEAS variables that should respond to XMV changes
    key_xmeas = {
        'XMEAS(1)': 'A Feed (controlled by XMV_3)',
        'XMEAS(2)': 'D Feed (controlled by XMV_1)', 
        'XMEAS(3)': 'E Feed (controlled by XMV_2)',
        'XMEAS(4)': 'A+C Feed (controlled by XMV_4)',
        'XMEAS(7)': 'Reactor Pressure (affected by XMV_5)',
        'XMEAS(9)': 'Reactor Temperature (affected by XMV_10)',
        'XMEAS(16)': 'Stripper Pressure (affected by XMV_8)',
        'XMEAS(19)': 'Stripper Steam Flow (controlled by XMV_9)',
        'XMEAS(20)': 'Compressor Work (affected by XMV_5)'
    }
    
    print(f"{'Variable':<15} {'Default':<12} {'Extreme':<12} {'Change':<12} {'% Change':<12} {'Status'}")
    print("-" * 80)
    
    significant_changes = 0
    total_tests = 0
    
    for xmeas_var, description in key_xmeas.items():
        if xmeas_var in default_data.columns and xmeas_var in extreme_data.columns:
            # Use final values (steady state)
            default_val = default_data[xmeas_var].iloc[-1]
            extreme_val = extreme_data[xmeas_var].iloc[-1]
            
            change = extreme_val - default_val
            pct_change = (change / default_val * 100) if default_val != 0 else 0
            
            # Consider >5% change as significant
            status = "✅ SIGNIFICANT" if abs(pct_change) > 5 else "⚠️  Small"
            if abs(pct_change) > 5:
                significant_changes += 1
            
            print(f"{xmeas_var:<15} {default_val:<12.3f} {extreme_val:<12.3f} {change:<12.3f} {pct_change:<12.1f}% {status}")
            total_tests += 1
    
    # Test 4: Summary and Conclusion
    print("\n🎯 Test 4: Summary")
    print("-" * 40)
    
    success_rate = (significant_changes / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📊 Variables tested: {total_tests}")
    print(f"📈 Significant changes (>5%): {significant_changes}")
    print(f"📉 Success rate: {success_rate:.1f}%")
    
    if success_rate > 50:
        print("✅ CONCLUSION: XMV controls ARE working! Changes are affecting XMEAS measurements.")
        print("   The monitoring interface should show these changes over time.")
    elif success_rate > 20:
        print("⚠️  CONCLUSION: XMV controls have PARTIAL effect. Some variables respond.")
        print("   You may need to wait longer or make more extreme changes.")
    else:
        print("❌ CONCLUSION: XMV controls may NOT be working properly.")
        print("   This suggests a potential issue with the control system.")
    
    # Test 5: Monitoring Interface Variables Check
    print("\n📺 Test 5: Monitoring Interface Variables")
    print("-" * 40)
    
    # Variables shown in monitoring interface (first 9 main ones)
    monitoring_vars = {
        'XMEAS(1)': 'A Feed',
        'XMEAS(2)': 'D Feed', 
        'XMEAS(3)': 'E Feed',
        'XMEAS(4)': 'A and C Feed',
        'XMEAS(7)': 'Reactor Pressure',
        'XMEAS(13)': 'Product Sep Pressure',
        'XMEAS(16)': 'Stripper Pressure', 
        'XMEAS(19)': 'Stripper Steam Flow',
        'XMEAS(20)': 'Compressor Work'
    }
    
    print("Variables visible in your monitoring interface:")
    monitoring_changes = 0
    
    for xmeas_var, display_name in monitoring_vars.items():
        if xmeas_var in default_data.columns and xmeas_var in extreme_data.columns:
            default_val = default_data[xmeas_var].iloc[-1]
            extreme_val = extreme_data[xmeas_var].iloc[-1]
            pct_change = ((extreme_val - default_val) / default_val * 100) if default_val != 0 else 0
            
            status = "📈 VISIBLE" if abs(pct_change) > 2 else "📉 Minimal"
            if abs(pct_change) > 2:
                monitoring_changes += 1
                
            print(f"  {display_name:<20}: {pct_change:>6.1f}% change - {status}")
    
    print(f"\n📊 Monitoring variables with visible changes: {monitoring_changes}/{len(monitoring_vars)}")
    
    if monitoring_changes >= 3:
        print("✅ You SHOULD see changes in the monitoring interface!")
    else:
        print("⚠️  Changes may be too small to notice in the monitoring interface.")
        print("   Try running for more time steps or making more extreme XMV changes.")

if __name__ == "__main__":
    test_xmv_response()
