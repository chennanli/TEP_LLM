#!/usr/bin/env python3
"""
TEP Steady State Startup Script
Ensures TEP simulation always starts from steady state
"""

import os
import sys
import time
import requests
import json

def check_tep_status():
    """Check if TEP is running and get status"""
    try:
        response = requests.get("http://localhost:9001/api/status", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def restart_tep_clean():
    """Restart TEP with clean state"""
    try:
        print("🔄 Restarting TEP simulation...")
        response = requests.post("http://localhost:9001/api/tep/restart", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ TEP restarted successfully")
                return True
            else:
                print(f"❌ TEP restart failed: {result.get('message')}")
        else:
            print(f"❌ TEP restart HTTP error: {response.status_code}")
    except Exception as e:
        print(f"❌ TEP restart error: {e}")
    
    return False

def set_speed_factor(speed_factor):
    """Set TEP speed factor"""
    try:
        print(f"⚡ Setting speed factor to {speed_factor}x...")
        response = requests.post(
            "http://localhost:9001/api/speed/factor",
            json={"speed_factor": speed_factor},
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Speed set to {speed_factor}x (interval: {result.get('step_interval_seconds')}s)")
                return True
    except Exception as e:
        print(f"❌ Speed setting error: {e}")
    
    return False

def wait_for_steady_state(target_steps=3):
    """Wait for TEP to generate steady state data"""
    print(f"⏳ Waiting for {target_steps} steady state steps...")
    
    start_time = time.time()
    last_step = -1
    
    while time.time() - start_time < 300:  # 5 minute timeout
        status = check_tep_status()
        if status:
            current_step = status.get('current_step', 0)
            tep_running = status.get('tep_running', False)
            
            if not tep_running:
                print("❌ TEP simulation stopped")
                return False
            
            if current_step > last_step:
                print(f"📊 Step {current_step} completed")
                last_step = current_step
                
                if current_step >= target_steps:
                    print(f"✅ Reached {target_steps} steady state steps")
                    return True
        
        time.sleep(2)
    
    print("⏰ Timeout waiting for steady state")
    return False

def verify_data_stability():
    """Verify that generated data is stable"""
    try:
        # Check if data file exists and has reasonable content
        data_file = 'legacy/data/live_tep_data.csv'
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                lines = f.readlines()
            
            if len(lines) > 1:  # Header + at least 1 data row
                print(f"✅ Data file has {len(lines)-1} data rows")
                
                # Check last few lines for step consistency
                if len(lines) >= 4:  # Header + 3 data rows
                    last_lines = lines[-3:]
                    steps = []
                    for line in last_lines:
                        parts = line.strip().split(',')
                        if len(parts) > 1:
                            try:
                                step = int(float(parts[1]))  # step column
                                steps.append(step)
                            except:
                                pass
                    
                    if len(steps) >= 2:
                        step_diff = steps[-1] - steps[-2]
                        if step_diff == 1:
                            print("✅ Step numbers are consecutive")
                            return True
                        else:
                            print(f"⚠️ Step difference: {step_diff} (expected: 1)")
                
                return True
            else:
                print("⚠️ Data file is empty")
        else:
            print("⚠️ Data file does not exist")
    except Exception as e:
        print(f"❌ Error verifying data: {e}")
    
    return False

def main():
    print("🏭 TEP STEADY STATE STARTUP")
    print("=" * 50)
    
    # 1. Check if TEP control panel is running
    print("🔍 Checking TEP control panel...")
    status = check_tep_status()
    if not status:
        print("❌ TEP control panel not running")
        print("Please start it with: cd legacy && ./start_legacy_system.sh")
        return False
    
    print("✅ TEP control panel is running")
    
    # 2. Restart TEP for clean state
    if not restart_tep_clean():
        print("❌ Failed to restart TEP")
        return False
    
    # 3. Set desired speed (default 10x for quick testing)
    speed_factor = float(input("Enter speed factor (1.0-50.0, default 10.0): ") or "10.0")
    speed_factor = max(1.0, min(50.0, speed_factor))
    
    if not set_speed_factor(speed_factor):
        print("❌ Failed to set speed factor")
        return False
    
    # 4. Wait for steady state
    if not wait_for_steady_state(target_steps=3):
        print("❌ Failed to reach steady state")
        return False
    
    # 5. Verify data stability
    if not verify_data_stability():
        print("⚠️ Data stability verification failed")
    
    # 6. Final status
    final_status = check_tep_status()
    if final_status:
        print("\n📊 FINAL STATUS:")
        print(f"   TEP Running: {final_status.get('tep_running')}")
        print(f"   Current Step: {final_status.get('current_step')}")
        print(f"   Speed Factor: {final_status.get('speed_factor')}x")
        print(f"   Step Interval: {final_status.get('step_interval_seconds')}s")
        print(f"   Data Points: {final_status.get('raw_data_points')}")
    
    print("\n🎉 TEP STEADY STATE STARTUP COMPLETE")
    print("Your TEP simulation is now running with stable data generation")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
