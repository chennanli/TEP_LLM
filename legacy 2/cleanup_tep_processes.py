#!/usr/bin/env python3
"""
TEP Process Cleanup Script
Ensures only one TEP simulation is running at a time
"""

import os
import sys
import psutil
import signal
import time
import requests

def find_tep_processes():
    """Find all TEP-related processes"""
    tep_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            
            # Look for TEP-related processes
            if any(keyword in cmdline.lower() for keyword in [
                'unified_tep_control_panel',
                'tep_bridge',
                'tep_simulator',
                'temain',
                'fortran',
                'mvp_dashboard'
            ]):
                tep_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': cmdline
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return tep_processes

def stop_tep_services():
    """Stop TEP services via API if available"""
    try:
        # Try to stop via API first
        response = requests.post("http://localhost:9001/api/tep/stop", timeout=5)
        if response.status_code == 200:
            print("✅ TEP simulation stopped via API")
            time.sleep(2)
            return True
    except:
        pass
    
    return False

def kill_process_tree(pid):
    """Kill a process and all its children"""
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        
        # Kill children first
        for child in children:
            try:
                child.terminate()
            except psutil.NoSuchProcess:
                pass
        
        # Kill parent
        parent.terminate()
        
        # Wait for termination
        gone, alive = psutil.wait_procs(children + [parent], timeout=5)
        
        # Force kill if still alive
        for proc in alive:
            try:
                proc.kill()
            except psutil.NoSuchProcess:
                pass
                
        return True
    except psutil.NoSuchProcess:
        return True
    except Exception as e:
        print(f"❌ Error killing process {pid}: {e}")
        return False

def cleanup_data_files():
    """Clean up data files for fresh start"""
    data_files = [
        'legacy/data/live_tep_data.csv',
        'data/live_tep_data.csv'
    ]
    
    for file_path in data_files:
        if os.path.exists(file_path):
            try:
                # Keep header only
                with open(file_path, 'r') as f:
                    header = f.readline()
                
                with open(file_path, 'w') as f:
                    f.write(header)
                
                print(f"✅ Cleaned {file_path}")
            except Exception as e:
                print(f"⚠️ Could not clean {file_path}: {e}")

def main():
    print("🧹 TEP PROCESS CLEANUP")
    print("=" * 50)
    
    # 1. Find all TEP processes
    tep_processes = find_tep_processes()
    
    if not tep_processes:
        print("✅ No TEP processes found")
    else:
        print(f"Found {len(tep_processes)} TEP-related processes:")
        for proc in tep_processes:
            print(f"  PID {proc['pid']}: {proc['name']} - {proc['cmdline'][:80]}...")
        
        # 2. Try graceful shutdown first
        print("\n🛑 Attempting graceful shutdown...")
        stop_tep_services()
        
        # 3. Kill remaining processes
        print("🔪 Killing remaining processes...")
        for proc in tep_processes:
            if kill_process_tree(proc['pid']):
                print(f"✅ Killed PID {proc['pid']}")
            else:
                print(f"❌ Failed to kill PID {proc['pid']}")
    
    # 4. Clean up data files
    print("\n🗑️ Cleaning up data files...")
    cleanup_data_files()
    
    # 5. Verify cleanup
    print("\n🔍 Verifying cleanup...")
    remaining = find_tep_processes()
    if remaining:
        print(f"⚠️ {len(remaining)} processes still running:")
        for proc in remaining:
            print(f"  PID {proc['pid']}: {proc['name']}")
    else:
        print("✅ All TEP processes cleaned up")
    
    print("\n🎯 CLEANUP COMPLETE")
    print("You can now start a fresh TEP simulation")

if __name__ == "__main__":
    main()
