#!/usr/bin/env python3
"""
Fix TEP initial state - ensure simulation starts from steady state
"""

import os
import sys
import numpy as np

def test_tep_initialization():
    """Test TEP initialization and find steady state"""
    
    print("🔧 TESTING TEP INITIALIZATION")
    print("="*60)
    
    # Add tep2py to path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tep_path = os.path.join(script_dir, 'external_repos', 'tep2py-master')
    if tep_path not in sys.path:
        sys.path.insert(0, tep_path)
    
    try:
        import tep2py
        print("✅ tep2py imported successfully")
        
        # Test 1: Run short simulation to see initial behavior
        print(f"\n📊 Test 1: Short simulation (5 steps)")
        idv_matrix = np.zeros((5, 20))  # 5 steps, all IDV = 0 (normal operation)
        
        tep_sim = tep2py.tep2py(idv_matrix, speed_factor=1.0)
        tep_sim.simulate()
        
        if hasattr(tep_sim, 'process_data'):
            data = tep_sim.process_data
            print(f"   Simulation steps: {len(data)}")
            
            # Check key variables for stability
            reactor_pressure = data['XMEAS(7)'].values
            reactor_temp = data['XMEAS(9)'].values
            
            print(f"   Reactor Pressure: {reactor_pressure[0]:.1f} → {reactor_pressure[-1]:.1f} kPa")
            print(f"   Reactor Temperature: {reactor_temp[0]:.1f} → {reactor_temp[-1]:.1f} °C")
            
            # Check if values are stabilizing
            pressure_change = abs(reactor_pressure[-1] - reactor_pressure[0])
            temp_change = abs(reactor_temp[-1] - reactor_temp[0])
            
            print(f"   Pressure change: {pressure_change:.1f} kPa")
            print(f"   Temperature change: {temp_change:.1f} °C")
            
            if pressure_change > 50 or temp_change > 5:
                print("   ⚠️  Large changes detected - simulation not starting from steady state")
                return False
            else:
                print("   ✅ Relatively stable - good initial state")
                return True
        else:
            print("   ❌ No process data available")
            return False
            
    except Exception as e:
        print(f"❌ Error testing TEP: {e}")
        return False

def find_steady_state_length():
    """Find how many steps needed to reach steady state"""
    
    print(f"\n🎯 FINDING STEADY STATE LENGTH")
    print("="*60)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tep_path = os.path.join(script_dir, 'external_repos', 'tep2py-master')
    if tep_path not in sys.path:
        sys.path.insert(0, tep_path)
    
    try:
        import tep2py
        
        # Run longer simulation to find steady state
        print("Running 50-step simulation to find steady state...")
        idv_matrix = np.zeros((50, 20))  # 50 steps, all IDV = 0
        
        tep_sim = tep2py.tep2py(idv_matrix, speed_factor=1.0)
        tep_sim.simulate()
        
        if hasattr(tep_sim, 'process_data'):
            data = tep_sim.process_data
            
            # Analyze key variables
            reactor_pressure = data['XMEAS(7)'].values
            reactor_temp = data['XMEAS(9)'].values
            
            print(f"Step-by-step analysis:")
            steady_step = None
            
            for i in range(5, len(reactor_pressure)):
                # Check if last 5 steps are stable
                recent_pressure = reactor_pressure[i-4:i+1]
                recent_temp = reactor_temp[i-4:i+1]
                
                pressure_std = np.std(recent_pressure)
                temp_std = np.std(recent_temp)
                
                if i % 10 == 0:  # Print every 10 steps
                    print(f"   Step {i}: P={reactor_pressure[i]:.1f}±{pressure_std:.1f} kPa, T={reactor_temp[i]:.1f}±{temp_std:.1f}°C")
                
                # Consider steady if std deviation is small
                if pressure_std < 5 and temp_std < 0.5 and steady_step is None:
                    steady_step = i
                    print(f"   🎯 Steady state reached at step {steady_step}")
                    break
            
            if steady_step:
                print(f"\n✅ Steady state values (step {steady_step}):")
                print(f"   Reactor Pressure: {reactor_pressure[steady_step]:.1f} kPa")
                print(f"   Reactor Temperature: {reactor_temp[steady_step]:.1f} °C")
                return steady_step, reactor_pressure[steady_step], reactor_temp[steady_step]
            else:
                print(f"\n⚠️  No clear steady state found in 50 steps")
                # Use last values as best estimate
                return 50, reactor_pressure[-1], reactor_temp[-1]
        
    except Exception as e:
        print(f"❌ Error finding steady state: {e}")
        return None, None, None

def create_steady_state_solution():
    """Create a solution for steady state initialization"""
    
    print(f"\n💡 STEADY STATE SOLUTION")
    print("="*60)
    
    print("The problem is that TEP simulation starts from non-steady initial conditions.")
    print("Each time we call tep2py.simulate(), it restarts from the beginning.")
    print()
    
    print("🔧 Recommended solutions:")
    print()
    
    print("1. **Pre-run to steady state** (Recommended)")
    print("   - Run simulation for ~20 steps to reach steady state")
    print("   - Use only the steady-state portion for analysis")
    print("   - Discard the initial transient period")
    print()
    
    print("2. **Continuous simulation** (Better)")
    print("   - Keep one long-running simulation instance")
    print("   - Add new IDV steps to existing simulation")
    print("   - Avoid restarting simulation each time")
    print()
    
    print("3. **Use steady-state initial conditions** (Best)")
    print("   - Modify Fortran code to start from known steady state")
    print("   - Requires recompiling temain_mod")
    print()
    
    print("I'll implement solution #1 (Pre-run to steady state)")

def main():
    print("TEP INITIAL STATE ANALYSIS")
    print("Diagnosing why simulation shows large fluctuations")
    print()
    
    # Test current initialization
    is_stable = test_tep_initialization()
    
    # Find steady state length
    steady_step, steady_pressure, steady_temp = find_steady_state_length()
    
    # Provide solution
    create_steady_state_solution()
    
    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*80}")
    
    if not is_stable:
        print("🔍 DIAGNOSIS: TEP simulation starts from non-steady initial conditions")
        print("   This causes large fluctuations in the first ~20 simulation steps")
        print()
        
        if steady_step:
            print(f"📊 FINDINGS:")
            print(f"   • Steady state reached after ~{steady_step} steps")
            print(f"   • Steady pressure: {steady_pressure:.1f} kPa")
            print(f"   • Steady temperature: {steady_temp:.1f} °C")
            print()
        
        print("🎯 SOLUTION: Modify unified_tep_control_panel.py to:")
        print("   1. Pre-run simulation to steady state")
        print("   2. Use only steady-state data for analysis")
        print("   3. Avoid restarting simulation each step")
        print()
        
        print("📝 Next step: Run fix_tep_steady_state.py to implement the fix")
    else:
        print("✅ TEP simulation appears to start from steady state")
        print("   The fluctuations might be caused by other factors")

if __name__ == "__main__":
    main()
