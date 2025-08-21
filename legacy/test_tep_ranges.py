#!/usr/bin/env python3
"""
Test TEP data ranges to verify if output values are within normal operating limits.
"""

import sys
import os
import numpy as np
import pandas as pd

# Add tep2py to path
script_dir = os.path.dirname(os.path.abspath(__file__))
tep_path = os.path.join(script_dir, 'external_repos', 'tep2py-master')
if tep_path not in sys.path:
    sys.path.insert(0, tep_path)

# TEP Normal Operating Ranges (from documentation)
TEP_RANGES = {
    # XMEAS Variables
    1: {"name": "A Feed", "min": 0.15, "max": 0.35, "unit": "kscmh"},
    2: {"name": "D Feed", "min": 3500, "max": 3800, "unit": "kg/h"},
    3: {"name": "E Feed", "min": 4300, "max": 4700, "unit": "kg/h"},
    4: {"name": "A and C Feed", "min": 8.5, "max": 10.0, "unit": "kscmh"},
    5: {"name": "Recycle Flow", "min": 25, "max": 29, "unit": "kscmh"},
    6: {"name": "Reactor Feed Rate", "min": 40, "max": 45, "unit": "kscmh"},
    7: {"name": "Reactor Pressure", "min": 2650, "max": 2750, "unit": "kPa", "critical": True},
    8: {"name": "Reactor Level", "min": 70, "max": 80, "unit": "%", "critical": True},
    9: {"name": "Reactor Temperature", "min": 120.2, "max": 120.6, "unit": "°C", "critical": True},
    10: {"name": "Purge Rate", "min": 0.30, "max": 0.40, "unit": "kscmh"},
    11: {"name": "Product Sep Temp", "min": 75, "max": 85, "unit": "°C"},
    12: {"name": "Product Sep Level", "min": 45, "max": 55, "unit": "%", "critical": True},
    13: {"name": "Product Sep Pressure", "min": 2600, "max": 2700, "unit": "kPa"},
    14: {"name": "Product Sep Underflow", "min": 20, "max": 30, "unit": "m³/h"},
    15: {"name": "Stripper Level", "min": 45, "max": 55, "unit": "%"},
    16: {"name": "Stripper Pressure", "min": 3000, "max": 3200, "unit": "kPa"},
    17: {"name": "Stripper Underflow", "min": 20, "max": 26, "unit": "m³/h"},
    18: {"name": "Stripper Temp", "min": 60, "max": 70, "unit": "°C"},
    19: {"name": "Stripper Steam Flow", "min": 220, "max": 250, "unit": "kg/h"},
    20: {"name": "Compressor Work", "min": 330, "max": 350, "unit": "kW"},
    21: {"name": "Reactor Coolant Temp", "min": 90, "max": 100, "unit": "°C"},
    22: {"name": "Separator Coolant Temp", "min": 75, "max": 85, "unit": "°C"},
}

def test_tep_simulation():
    """Test TEP simulation and check if values are in normal ranges."""
    try:
        import tep2py
        print("✅ tep2py loaded successfully")

        # Initialize TEP simulation
        print("🔄 Initializing TEP simulation...")

        # Create a simple IDV matrix for fallback testing
        idata = np.zeros((5, 20))  # 5 time steps, 20 IDV inputs

        # Run simulation using tep2py class (which will use fallback)
        print("🚀 Running TEP simulation...")

        tep_sim = tep2py.tep2py(idata)
        tep_sim.simulate()

        if hasattr(tep_sim, 'process_data') and len(tep_sim.process_data) > 0:
            # Get the last row of data
            latest_data = tep_sim.process_data.iloc[-1]

            # Extract XMEAS values (first 41 columns should be XMEAS_1 to XMEAS_41)
            xmeas_cols = [col for col in tep_sim.process_data.columns if 'XMEAS' in col]
            if len(xmeas_cols) >= 22:
                xmeas = latest_data[xmeas_cols[:41]].values  # Get first 41 XMEAS values
                source = "tep2py fallback data"
                print(f"   ✅ {source} successful")
            else:
                print(f"   ❌ Insufficient XMEAS columns: {len(xmeas_cols)}")
                return False
        else:
            print("   ❌ No process data generated")
            return False
        
        print(f"\n📊 TEP Simulation Results (Source: {source}):")
        print("=" * 80)
        
        # Check ranges for first 22 XMEAS variables
        in_range_count = 0
        out_of_range = []
        
        for i in range(1, 23):  # XMEAS 1-22
            if i in TEP_RANGES:
                range_info = TEP_RANGES[i]
                value = xmeas[i-1]  # XMEAS is 0-indexed in array
                
                in_range = range_info["min"] <= value <= range_info["max"]
                status = "✅" if in_range else "❌"
                critical = "🚨" if range_info.get("critical", False) else "  "
                
                print(f"{critical} XMEAS_{i:2d} {range_info['name']:25s}: {value:8.3f} {range_info['unit']:6s} "
                      f"[{range_info['min']:6.1f} - {range_info['max']:6.1f}] {status}")
                
                if in_range:
                    in_range_count += 1
                else:
                    out_of_range.append((i, range_info['name'], value, range_info['min'], range_info['max']))
        
        print("=" * 80)
        print(f"📈 Summary: {in_range_count}/22 variables in normal range ({in_range_count/22*100:.1f}%)")
        
        if out_of_range:
            print(f"\n🚨 {len(out_of_range)} variables OUT OF RANGE:")
            for i, name, value, min_val, max_val in out_of_range:
                deviation = min(abs(value - min_val), abs(value - max_val))
                print(f"   XMEAS_{i:2d} {name:25s}: {value:8.3f} (deviation: {deviation:6.3f})")
        else:
            print("\n🎉 All variables are within normal operating ranges!")
        
        return len(out_of_range) == 0
        
    except ImportError as e:
        print(f"❌ Failed to import tep2py: {e}")
        return False
    except Exception as e:
        print(f"❌ TEP simulation failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TEP Range Validation Test")
    print("=" * 50)
    
    success = test_tep_simulation()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ TEST PASSED: All TEP values are within normal ranges")
    else:
        print("❌ TEST FAILED: Some TEP values are outside normal ranges")
        print("   This explains why PCA anomaly detection shows high T² values!")
