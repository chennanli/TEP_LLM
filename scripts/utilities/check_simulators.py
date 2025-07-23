#!/usr/bin/env python3
"""
TEP Simulator Process Checker
============================

Check for running TEP simulators and clean up orphaned processes.
"""

import psutil
import sys
import subprocess

def check_running_simulators():
    """Check for running TEP simulator processes."""
    print("🔍 Checking for running TEP simulators...")
    print("="*50)
    
    running_processes = []
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                
                # Check for TEP simulator processes
                if any(keyword in cmdline for keyword in [
                    'tep_simulator', 'simple_web_tep', 'enhanced_web_tep', 
                    'clean_qt_tep', 'qt_tep_simulator'
                ]):
                    running_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': cmdline,
                        'create_time': proc.info['create_time']
                    })
                
                # Check for Flask processes on our ports
                elif ('flask' in cmdline.lower() and 
                      ('8080' in cmdline or '8081' in cmdline)):
                    running_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': cmdline,
                        'create_time': proc.info['create_time']
                    })
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
    except Exception as e:
        print(f"❌ Error checking processes: {e}")
        return []
    
    return running_processes

def check_ports():
    """Check which ports are in use."""
    print("\n🌐 Checking ports 8080 and 8081...")
    print("="*40)
    
    ports_info = {}
    
    try:
        for conn in psutil.net_connections():
            if conn.laddr.port in [8080, 8081] and conn.status == 'LISTEN':
                try:
                    proc = psutil.Process(conn.pid)
                    ports_info[conn.laddr.port] = {
                        'pid': conn.pid,
                        'name': proc.name(),
                        'cmdline': ' '.join(proc.cmdline())
                    }
                except:
                    ports_info[conn.laddr.port] = {
                        'pid': conn.pid,
                        'name': 'Unknown',
                        'cmdline': 'Unknown'
                    }
    except Exception as e:
        print(f"❌ Error checking ports: {e}")
        return {}
    
    return ports_info

def kill_process(pid):
    """Kill a process by PID."""
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        
        # Wait for termination
        try:
            proc.wait(timeout=3)
            return True
        except psutil.TimeoutExpired:
            # Force kill if it doesn't terminate
            proc.kill()
            return True
            
    except psutil.NoSuchProcess:
        return True  # Already dead
    except Exception as e:
        print(f"❌ Error killing process {pid}: {e}")
        return False

def main():
    """Main function."""
    print("🎛️ TEP Simulator Process Checker")
    print("="*50)
    
    # Check running processes
    running = check_running_simulators()
    
    if not running:
        print("✅ No TEP simulator processes found")
    else:
        print(f"⚠️ Found {len(running)} running TEP simulator process(es):")
        print()
        
        for i, proc in enumerate(running, 1):
            print(f"{i}. PID: {proc['pid']}")
            print(f"   Name: {proc['name']}")
            print(f"   Command: {proc['cmdline'][:80]}...")
            print()
    
    # Check ports
    ports = check_ports()
    
    if not ports:
        print("✅ Ports 8080 and 8081 are free")
    else:
        print("⚠️ Ports in use:")
        for port, info in ports.items():
            print(f"   Port {port}: PID {info['pid']} ({info['name']})")
    
    # Offer to clean up
    if running or ports:
        print("\n🧹 CLEANUP OPTIONS:")
        print("="*30)
        print("1. Kill all TEP simulator processes")
        print("2. Kill specific process by PID")
        print("3. Do nothing")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            print("\n🔪 Killing all TEP simulator processes...")
            
            # Kill running processes
            for proc in running:
                print(f"   Killing PID {proc['pid']}...")
                if kill_process(proc['pid']):
                    print(f"   ✅ PID {proc['pid']} killed")
                else:
                    print(f"   ❌ Failed to kill PID {proc['pid']}")
            
            # Kill port processes
            for port, info in ports.items():
                if info['pid'] not in [p['pid'] for p in running]:
                    print(f"   Killing port {port} process (PID {info['pid']})...")
                    if kill_process(info['pid']):
                        print(f"   ✅ Port {port} freed")
                    else:
                        print(f"   ❌ Failed to free port {port}")
            
            print("\n✅ Cleanup complete!")
            
        elif choice == "2":
            pid_str = input("Enter PID to kill: ").strip()
            try:
                pid = int(pid_str)
                print(f"\n🔪 Killing PID {pid}...")
                if kill_process(pid):
                    print(f"✅ PID {pid} killed")
                else:
                    print(f"❌ Failed to kill PID {pid}")
            except ValueError:
                print("❌ Invalid PID")
                
        else:
            print("✅ No action taken")
    
    print("\n🎯 RECOMMENDATIONS:")
    print("="*30)
    print("• Use 'smart_launcher.py' for automatic cleanup")
    print("• Always use Ctrl+C to stop simulators cleanly")
    print("• Run this checker if you suspect orphaned processes")
    print("• Restart terminal if ports remain occupied")

if __name__ == "__main__":
    main()
